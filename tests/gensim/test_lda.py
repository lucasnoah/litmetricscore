from django.test import TestCase
import nltk
from topic_modeling.python_based import *

from nltk.corpus import inaugural

def build_inaugural_corpus():
    """
    Get a word token list for each doc in the inaugural address corpus
    :return: word_lists
    """
    word_lists = []
    for fileid in inaugural.fileids():
        words = [w for w in inaugural.words(fileid)]
        word_lists.append(words)
    return word_lists


class TestLda(TestCase):

    def setUp(self):
        self.corpus = build_inaugural_corpus()

    def test_lda_handler(self):
        handler = LdaHandler(self.corpus)
        handler.create_dictionary()
        handler.create_corpus()
        handler.train_lda_model(40,0,4)
        self.assertEqual(len(handler.lda_model.show_topics(self.corpus, num_words=10)),40)



class TestLdaStorage(TestCase):

    def setUp(self):
        self.corpus = build_inaugural_corpus()
        self.handler = LdaHandler(self.corpus)
        self.handler.create_dictionary()
        self.handler.create_corpus()
        self.handler.train_lda_model(10,0,4)
        self.user = User.objects.create(username='lucas')
        self.corpus_collection = CorpusItemCollection.objects.create(title='test',user=self.user)

    def test_that_store_models_show_topics_generates_the_right_amount_of_objects(self):

        topics=self.handler.lda_model.show_topics(10, formatted=False)
        topic_group=build_and_save_topic_tuples_and_topic_groups(topics,self.user,"blehblahalkj;afj")
        collections = [{'id':self.corpus_collection.id}]
        add_collections_to_topic_group(topic_group, collections)
        self.assertEqual(len(TopicModelGroup.objects.all()),1)
        self.assertEqual(len(Topic.objects.all()),10)
        self.assertEqual(len(TopicTuple.objects.all()),100)
        self.assertEqual(topic_group.collections.count(),1)

