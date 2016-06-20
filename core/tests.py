from unittest import TestCase
from core.models import TextFile, CorpusItemCollection, CorpusItem, CorpusItemFilter, WordToken, LockedWordToken
from core.sentence_parsers import SentenceHandler
from os.path import abspath
from django.contrib.auth.models import User
from django.conf import settings
import json
from core.document_processing import grab_consolidated_filtered_list_from_collection_and_filter, \
    dump_collection_to_plain_text, parse_locked_text_upload, save_locked_collection, split_document_into_line_chunks, \
    initial_document_dump

from django.core.files.uploadedfile import SimpleUploadedFile

from os.path import abspath
from django.test import TestCase
from core.sentence_parsers import *
from core.models import *


f_path = abspath("tests/core/parse_response.json")

json_event = ''

with open(f_path) as json_file:
    json_event = json_file.read()



def create_doc_with_x_lines(x):
    nums = [str(num) + '\n' for num in xrange(x)]
    with open('testfile.txt', 'wb+') as f:
        for num in nums:
            f.write(num + '\n')
        f.close()
    return f



class TestDocumentImportExport(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='test', email='test@test.com')
        self.line_file = create_doc_with_x_lines(100)
        TextFile(user=self.user, file=SimpleUploadedFile('best_file_eva.txt', str([str(num) + '\n' for num in xrange(100)]))).save()
        self.text_file = TextFile.objects.last()
        sentences = "I am a pony. I am a frong. I am a dog.  I go to the zoo."
        TextFile(user=self.user, file=SimpleUploadedFile('best_file.txt', sentences)).save()
        self.sentence_file = TextFile.objects.last()
        CorpusItem(title='test_ci', text_file=self.text_file, user=self.user).save()
        self.corpus_item = CorpusItem.objects.last()

        f_path = abspath("tests/core/parse_response.json")
        self.parse_lock_path = abspath("tests/core/parse_locked.txt")

        with open(f_path) as json_file:
            json_event = json_file.read()

        parsed_text = json.loads(json_event)
        sentences = parsed_text['sentences']

        # deal with bulk save
        words_to_save = []

        for sentence in sentences:
            handler = SentenceHandler(sentence, self.corpus_item)
            words_to_save = words_to_save + handler.process_sentence()
        # buld save the words
        WordToken.objects.bulk_create(words_to_save)

        CorpusItemCollection(user=self.user, title='test').save()
        self.collection = CorpusItemCollection.objects.last()
        self.collection.corpus_items.add(self.corpus_item)

        settings.DEFAULT_FILTER = {"name": "bob",
                  "filter_data": {
                      "lemma": True,
                      "ner": False,
                      "pos": ['CC', 'CD', 'DT', 'EX', 'FW', 'IN', 'JJ', 'JJR', 'JJS', 'LS',
                              'MD', 'NN', 'NNS', 'NNP', 'NNPS', 'PDT', 'PDT', 'POS', 'PRP',
                              'PRP$', 'RB', 'RBR', 'RBS', 'RP', 'SYM', 'TO', 'UH', 'VB', 'VBD',
                              'VBG', 'VBN', 'VBP', 'VBZ', 'WDT', 'WP', 'WP$', 'WRB'],
                      "stopwords": (
                      "I,i,me,my,myself,we,our,ours,ourselves,you,your,yours,yourself,yourselves,he,him,his,"
                      "himself,she,her,hers,herself,it,its,itself,they,them,their,theirs,themselves,what,"
                      "which,who,whom,this,that,these,those,am,is,are,was,were,be,been,being,have,has,had,"
                      "having,do,does,did ,doing,a,an,the,and,but,if,or,because,as,until,while,of,at,by,"
                      "for,with,about,against,between,into,through,during,before,after,above,below,to,"
                      "from,up,down,in,out,on,off,over,under,again,further,then,once,here,there,when,"
                      "where,why,how,all,any,both,each,few,more,most,other,some,such,no,nor,not,only,own,"
                      "same,so,than,too,very,s,t,can,will,just,don,should,now")
                  }
                  }
        self.filter = settings.DEFAULT_FILTER

    def tearDown(self):
        self.user.delete()

    def test_split_document_into_line_chunks(self):
        num_lines = len(self.text_file.file.readlines())
        print num_lines
        chunks = split_document_into_line_chunks(self.text_file, 5)
        print chunks
        self.assertEquals(len(chunks), 10)

    def test_grab_consolidated_filtered_list_from_collection_and_filter(self):
        token_list = grab_consolidated_filtered_list_from_collection_and_filter(self.collection, self.filter)
        self.assertEquals(len(token_list), 32)

    def test_dump_collection_to_plain_text(self):
        token_string = dump_collection_to_plain_text(self.collection, self.filter)
        print self.filter
        self.assertEquals(len(token_string), 228)

    """

    def test_parse_locked_text_upload(self):

        parse_list = parse_locked_text_upload(self.line_file)
        self.assertEquals(len(parse_list), 8)

    """
    def test_save_locked_collection(self):
        collection = save_locked_collection(self.text_file, title='test_coll')
        tokens = LockedWordToken.objects.filter(collection=collection)
        self.assertEquals(len(tokens), 100)

    def test_split_document_into_line_chunks(self):
        file = self.line_file
        chunks = split_document_into_line_chunks(self.text_file.file, 'test_file', 10)
        self.assertEquals(len(chunks), 1)


    def test_initial_document_dump(self):
        i = initial_document_dump(self.sentence_file.id, self.corpus_item.id)
        sentences = Sentence.objects.filter(corpus_item=i)
        print 'sentences len', len(sentences)
        print sentences
        self.assertEquals(len(sentences),0)


class TestSentenceParsing(TestCase):

    def setUp(self):
        self.json_data = json_event
        User.objects.create(username='test', password='test')
        self.user = User.objects.last()

        self.textfile = TextFile.objects.create(
            user = self.user,
            file = f_path
        )

        self.corpus_item = CorpusItem.objects.create(
            title = 'testCorpusItem',
            text_file = self.textfile,
            user = self.user
        )

        self.test_sentence = sentences_to_dict(self.json_data)[0]

    def test_that_it_can_be_parsed_to_python(self):
        d = sentences_to_dict(self.json_data)
        self.assertEqual(len(d), 4)

    def test_create_and_save_a_sentence(self):
        create_and_save_a_sentence(sentences_to_dict(self.json_data)[0], self.corpus_item)
        sentences = Sentence.objects.all()
        self.assertEqual(sentences[0].index, 0)
        self.assertEqual(sentences.count(), 1)

    def test_create_and_save_a_token(self):
        create_and_save_a_sentence(sentences_to_dict(self.json_data)[0], self.corpus_item)
        sentences = Sentence.objects.all()
        create_and_save_word_token(self.test_sentence['tokens'][0], sentences[0])
        wd = WordToken.objects.all()
        self.assertEqual(wd[0].pos, 'PRP')
        self.assertEqual(wd.count(), 1)

    def test_create_and_save_a_sentence_dependency(self):
        create_and_save_a_sentence(sentences_to_dict(self.json_data)[0], self.corpus_item)
        sentences = Sentence.objects.all()
        create_and_save_sentence_dependency("basic-dependencies", self.test_sentence["basic-dependencies"][0], sentences[0])
        sd = SentenceDependency.objects.all()
        self.assertEqual(sd[0].type,"basic-dependencies")
        self.assertEqual(sd.count(), 1)


class TestSentenceHandler(TestCase):


    def setUp(self):
        self.json_data = json_event
        User.objects.create(username='test', password='test')
        self.user = User.objects.last()

        self.textfile = TextFile.objects.create(
            user = self.user,
            file = f_path
        )

        self.corpus_item = CorpusItem.objects.create(
            title = 'testCorpusItem',
            text_file = self.textfile,
            user = self.user
        )

        self.test_sentence = sentences_to_dict(self.json_data)[0]




    def test_sentence_handler_create_sentence(self):
        handler = SentenceHandler(self.test_sentence, self.corpus_item)
        handler.create_sentence()
        sentences = Sentence.objects.all()
        self.assertEqual(sentences.count(), 1)

    def test_that_handler_is_saving_tokens(self):
        handler = SentenceHandler(self.test_sentence, self.corpus_item)
        handler.create_sentence()
        handler.save_word_tokens()
        wd = WordToken.objects.all()
        self.assertEqual(wd.count(), 13)

    def test_that_handler_is_saving_dependency_parse(self):
        handler = SentenceHandler(self.test_sentence, self.corpus_item)
        handler.create_sentence()
        handler.save_sentence_dependecy_parses("basic-dependencies")
        sd = SentenceDependency.objects.all()
        self.assertEqual(sd.count(), 13)

    def test_that_sentence_can_be_rebuilt(self):
        handler = SentenceHandler(self.test_sentence, self.corpus_item)
        handler.create_sentence()
        handler.save_word_tokens()
        sentences = Sentence.objects.all()
        words = WordToken.objects.filter(sentence=sentences[0])
        print words[0]
        sentence = rebuild_sentence_from_tokens(words)
        self.assertEqual(sentence, 'I had long been familiar with the area around the Boulevard Ornano.')



class TestStopWordChecking(TestCase):

    def test_to_make_sure_basic_stop_words_are_filtered_out(self):
        a = check_if_word_is_stopword('and')
        self.assertEqual(a, True)
        b = check_if_word_is_stopword('Paris')
        self.assertEqual(b, False)












