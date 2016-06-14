import factory
from utils import create_topic_list, grab_topic_tuple_sets_for_topic_modeling_group, create_csv_from_topics_list, \
    chunk_bag_of_word_collection_by_chunk_size, chunk_bag_of_word_collection_by_char_string
from topic_modeling.python_based import topic_modeling_celery_task, hdp_celery_task, lsi_celery_task
from core.models import TextFile, CorpusItem, WordToken, CorpusItemCollection
from unittest import TestCase
from django.contrib.auth.models import User
from os.path import abspath
from core.sentence_parsers import SentenceHandler
import json
from django.conf import settings


class TopicModelGroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'topic_modeling.TopicModelGroup'
        django_get_or_create = ('user',)


class TopicFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'topic_modeling.Topic'
        django_get_or_create = ('topic_model_group',)


class TopicTupleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'topic_modeling.TopicTuple'  # Equivalent to ``model = myapp.models.User``
        django_get_or_create = ('weight', 'word', 'topic')

    weight = 4.0
    word = 'word'


class TestUtils(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='test', email='test@test.com')
        self.topic_group = TopicModelGroupFactory(user=self.user)
        self.topic = TopicFactory(topic_model_group=self.topic_group)
        self.topic_tuple = TopicTupleFactory(topic=self.topic)


    def tearDown(self):
        self.user.delete()

    def test_grab_topic_tuple_sets_for_topic_modeling_group(self):
        tuples = grab_topic_tuple_sets_for_topic_modeling_group(self.topic_group.id)
        self.assertEquals(len(tuples), 1)

    def test_create_topic_list(self):
        input = []
        input.append([self.topic_tuple, TopicTupleFactory(word='word2', topic=self.topic)])
        out = create_topic_list(input)
        self.assertEquals(out, [['word : 4.0', 'word2 : 4.0']])

    def test_create_csv_from_topics_list(self):
        input = []
        input.append([self.topic_tuple, TopicTupleFactory(word='word2', topic=self.topic)])
        input.append([self.topic_tuple, TopicTupleFactory(word='word2', topic=self.topic)])
        topics_list = create_topic_list(input)
        csv = create_csv_from_topics_list(topics_list)
        output = 'word : 4.0,word2 : 4.0\r\nword : 4.0,word2 : 4.0\r\n'
        self.assertEquals(csv.content, output)

    def test_chunk_bag_of_word_collection_by_chunk_size(self):
        list_to_chunk = list(xrange(500))
        self.assertEquals(len(chunk_bag_of_word_collection_by_chunk_size(list_to_chunk, 100)), 5)
        # test for chunk size input less than one.

        with self.assertRaises(IOError):
            chunk_bag_of_word_collection_by_chunk_size(list_to_chunk, 0)

        list_to_chunk = list(xrange(3))
        self.assertEquals(len(chunk_bag_of_word_collection_by_chunk_size(list_to_chunk, 2)), 2)

    def test_chunk_bag_of_word_collection_by_char_string(self):
        word_1 = WordToken(original_text='1')
        word_2 = WordToken(original_text='2')
        word_3 = WordToken(original_text='3')
        l =[word_1, word_2, word_3]
        out = [[word_1], [word_3]]
        self.assertEquals(chunk_bag_of_word_collection_by_char_string(l, '2'), out)


class TestPythonBasedModeling(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='test', email='test@test.com')
        TextFile(user=self.user, file=None).save()
        self.text_file = TextFile.objects.last()
        CorpusItem(title='test_ci', text_file=self.text_file, user=self.user).save()
        self.corpus_item = CorpusItem.objects.last()

        f_path = abspath("tests/core/parse_response.json")

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

    def tearDown(self):
        self.user.delete()

    def test_topic_modeling_celery_task(self):
        collection_data = [
                {
                    "items": [
                    {
                        "id": self.corpus_item.id
                    }
                        ],

                    "filter": {
                        "name": "default"
                    },
                    "id": self.collection.id
                }
            ]

        options = {

            "chunking": "count",
            "chunk_size": 2,
            "breakword": "breakword",
            "numPasses": 1,
            "numTopics": 10,
            "wordNetSense": True,
            "lemmas": True
        }

        self.assertEquals(len(topic_modeling_celery_task(collection_data, options, self.user.id)), 10)
        options['chunking'] = 'none'
        self.assertEquals(len(topic_modeling_celery_task(collection_data, options, self.user.id)), 10)
        options['chunking'] = 'breakword'
        self.assertEquals(len(topic_modeling_celery_task(collection_data, options, self.user.id)), 10)
        options['alpha'] = 'auto'
        self.assertEquals(len(topic_modeling_celery_task(collection_data, options, self.user.id)), 10)
        options['iterations'] = 50
        options['gamma_threshold'] = 0.001
        self.assertEquals(len(topic_modeling_celery_task(collection_data, options, self.user.id)), 10)
        options = {

            "chunking": "count",
            "chunk_size": 2,
            "breakword": "breakword",
            "numPasses": 1,
            "numTopics": 10,
            "wordNetSense": True,
            "lemmas": True

        }

        #TEST HDP TOPIC MODELING
        self.assertEquals(len(hdp_celery_task(collection_data, options, self.user.id)), 150)

        #TEST LSI CELERY TASK
        options = {

            "chunking": "count",
            "chunk_size": 30,
            "breakword": "breakword",
            "numPasses": 1,
            "numTopics": 10,
            "wordNetSense": True,
            "lemmas": True,
            "num_topics" : 100
        }
        topics = lsi_celery_task(collection_data, options, self.user.id)
        self.assertEquals(len(topics), 2)

