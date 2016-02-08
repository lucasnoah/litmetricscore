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
        self.assertEqual(handler.lda_model.top_topics(self.corpus, num_words=20),1)



