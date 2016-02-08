from os.path import abspath
from django.contrib.auth.models import User

from django.test import TestCase

from core.sentence_parsers import *
from core.models import *


f_path = abspath("tests/core/parse_response.json")

json_event = ''

with open(f_path) as json_file:
    json_event = json_file.read()



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
        self.assertEqual(sd[0].type,"basic-dependencies" )
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








