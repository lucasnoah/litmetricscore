import factory
from utils import create_topic_list, grab_topic_tuple_sets_for_topic_modeling_group, create_csv_from_topics_list
from unittest import TestCase
from django.contrib.auth.models import User


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

