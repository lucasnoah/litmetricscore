from gensim import corpora, models, similarities
from gensim.models.ldamodel import LdaModel

#gather words to be modeled as a list of words

#create a gensim dictionary object out of all the words. Gensim dictionary accepts a list of texts, which is really
#just a list of tokenized words.


def create_gensim_dictionary_object(word_lists):
    """
    creates a gensim dict from your set of documents in whatever corpus selection you are using.
    :param word_lists:
    :return: gensim dict
    """
    d = corpora.Dictionary(word_lists)
    return d


def create_corpus_from_word_lists_and_dictionary(dictionary, word_lists):
    """
    Uses a dictionary to create a bag of word style corpus from a list of word_tokens.
    """
    corpus = [dictionary.doc2bow(word_list) for word_list in word_lists]
    return corpus


def create_lda(dictionary, corpus, num_topics, update_every, passes):
    """
    Builds a Latend Deralicht Analysis from a corpus and a dictionary
    :param dictionary:
    :param corpus:
    :param num_topics:
    :param update_every:
    :param passes:
    :return: lda
    """
    lda = LdaModel(corpus=corpus, id2word=dictionary, num_topics=num_topics, update_every=update_every, passes=passes)
    return lda

def return_lda_topics(lda, number_of_topics):
    return lda.print_topics(number_of_topics)


class LdaHandler(object):

    def __init__(self, texts):
        self.texts = texts


    def create_dictionary(self):
        self.dictionary = create_gensim_dictionary_object(self.texts)


    def create_corpus(self):
        self.corpus = create_corpus_from_word_lists_and_dictionary(self.dictionary, self.texts)


    def train_lda_model(self, num_topics, update_every, passes):
        self.lda_model = create_lda(self.dictionary, self.corpus, num_topics, update_every, passes)


    def parse_lda_output(self):
        pass










