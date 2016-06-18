from unittest import TestCase
from core.models import TextFile, CorpusItemCollection, CorpusItem, CorpusItemFilter, WordToken, LockedWordToken
from core.sentence_parsers import SentenceHandler
from os.path import abspath
from django.contrib.auth.models import User
from django.conf import settings
import json
from core.document_processing import grab_consolidated_filtered_list_from_collection_and_filter, \
    dump_collection_to_plain_text, parse_locked_text_upload, save_locked_collection

class TestDocumentImportExport(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='test', email='test@test.com')
        TextFile(user=self.user, file=abspath("tests/core/parse_locked.txt")).save()
        self.text_file = TextFile.objects.last()
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


        self.filter = settings.DEFAULT_FILTER

    def tearDown(self):
        self.user.delete()

    def test_grab_consolidated_filtered_list_from_collection_and_filter(self):
        token_list = grab_consolidated_filtered_list_from_collection_and_filter(self.collection, self.filter)
        self.assertEquals(len(token_list), 34)

    def test_dump_collection_to_plain_text(self):
        token_string = dump_collection_to_plain_text(self.collection, self.filter)
        self.assertEquals(len(token_string), 232)

    def test_parse_locked_text_upload(self):
        parse_list = parse_locked_text_upload(self.text_file.file)
        self.assertEquals(len(parse_list), 8)

    def test_save_locked_collection(self):
        collection = save_locked_collection(self.text_file, title='test_coll')
        tokens = LockedWordToken.objects.filter(collection=collection)
        self.assertEquals(len(tokens), 8)


