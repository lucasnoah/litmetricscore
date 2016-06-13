from gensim import corpora, models, similarities
from gensim.models.ldamodel import LdaModel
import gensim
from core.models import WordToken
from topic_modeling.filters import *
from topic_modeling.models import *
from django.conf import settings
from topic_modeling.utils import chunk_bag_of_word_collection_by_char_string, chunk_bag_of_word_collection_by_chunk_size


# gather words to be modeled as a list of words

# create a gensim dictionary object out of all the words. Gensim dictionary accepts a list of texts, which is really
# just a list of tokenized words.


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


def create_lda(dictionary, corpus, num_topics, update_every, passes, *args, **kwargs):
    """
    Builds a Latend Deralicht Analysis from a corpus and a dictionary
    :param dictionary:
    :param corpus:
    :param num_topics:
    :param update_every:
    :param passes:
    :return: lda
    """

    alpha = kwargs.get('alpha') or 'auto'

    #: default is 50 supposedly increasing is not particularly useful, lowering can be useful if # ofdocuments is small
    iterations = kwargs.get('iterations') or 50
    #
    gamma_threshold = kwargs.get('gamma_threshold') or 0.001
    #
    minimum_probability = kwargs.get('minimum_probability') or 0.01
    #
    chunksize = kwargs.get('chunksize') or 2000

    lda = LdaModel(corpus=corpus, id2word=dictionary, num_topics=num_topics, update_every=update_every, passes=passes,
                   iterations=iterations, gamma_threshold=gamma_threshold, minimum_probability=minimum_probability,
                   alpha=alpha, chunksize=chunksize)

    return lda


def create_hdp(dictionary, corpus, **kwargs):
    """
    :param dictionary:
    :param corpus:
    :param num_topics:
    :param update_every:
    :param passes:
    :param args:
    :param kwargs:
    :return:
    """

    max_chunks = kwargs.get('max_chunks') or None
    max_time = kwargs.get('max_time') or None
    chunkz_size = kwargs.get('chunk_size') or 256
    kappa = kwargs.get('kappa') or 1.0
    tau = kwargs.get('tau') or 64.0
    K = kwargs.get('K') or 15
    T = kwargs.get('T') or 150
    alpha = kwargs.get('alpha') or 1
    gamma = kwargs.get('gamma') or 1
    eta = kwargs.get('eta') or 0.01
    scale = kwargs.get('scale') or 1.0
    var_converge = kwargs.get('var_converge') or 0.0001

    model = gensim.models.hdpmodel.HdpModel(corpus, dictionary, max_chunks=max_chunks, max_time=max_time,
                                            chunksize=chunkz_size, kappa=kappa, tau=tau, K=K, T=T, alpha=alpha,
                                            gamma=gamma, eta=eta, scale=scale, var_converge=var_converge)

    return model

def compute_lsi_model(corpus, dictionary, num_topics):
    lsi = gensim.models.lsimodel.LsiModel(corpus=corpus, id2word=dictionary, num_topics=num_topics)
    return lsi


def return_lda_topics(lda, number_of_topics):
    return lda.print_topics(number_of_topics)


class LdaHandler(object):
    """
    Class that handles processing of gensim LDA processes
    """

    def __init__(self, texts):
        self.texts = texts

    def create_dictionary(self):
        self.dictionary = create_gensim_dictionary_object(self.texts)

    def create_corpus(self):
        self.corpus = create_corpus_from_word_lists_and_dictionary(self.dictionary, self.texts)

    def train_lda_model(self, num_topics, update_every, passes, options):
        self.lda_model = create_lda(self.dictionary, self.corpus, num_topics, update_every, passes, **options)

    def train_hdp_model(self, options):
        self.hdp_model = create_hdp(self.dictionary, self.corpus, **options)

    def compute_lsi(self, num_topics):
        self.lsi_model = compute_lsi_model(self.corpus, self.dictionary, num_topics)


###HELPER FUNCTIONS FOR CELERY TEST###


def grab_tokens_for_corpus_item(id):
    return WordToken.objects.filter(sentence__corpus_item_id=id)


def grab_initial_bof_query_set_with_filers_from_view(collection_data):
    collection_bof_list = []
    print collection_data
    for collection in collection_data:
        # grab list of id's for corpus items in collection
        list_of_corpus_items_ids_in_collection = [c.get('id') for c in collection['items']]
        # grabs a list of token lists
        document_token_list = [grab_tokens_for_corpus_item(id) for id in list_of_corpus_items_ids_in_collection]
        print collection['filter']
        if collection['filter']['name'] == 'default':
            collection['filter'] = settings.DEFAULT_FILTER
        collection_bof_list.append((document_token_list, collection['filter']))
    return collection_bof_list


def apply_filter_to_collection(collection_tuple):
    """
    Applies the filters to the collection/filter tuples and returns a list of words for gensim.
    :param collection_tuple:
    :return: list of lists(documents)
    """
    collection_token_lists = collection_tuple[0]
    filter = collection_tuple[1]
    document_token_bag = []
    for l in collection_token_lists:
        qs = select_only_desired_pos_tags(l, filter['filter_data']['pos'])
        qs = filter_out_named_entities(qs, filter['filter_data']['ner'])
        qs = filter_out_stopwords(qs, filter['filter_data']['stopwords'])
        document_token_bag.append(list(qs))
    return document_token_bag


def build_and_save_topic_tuples_and_topic_groups(topics, user, collection_data):
    topic_group = TopicModelGroup.objects.create(
        user=user,
        input_data=collection_data
    )

    for topic in topics:
        new_topic = Topic.objects.create(topic_model_group=topic_group)
        # topic_group.
        for topic_tuple in topic[1]:
            TopicTuple.objects.create(
                word=topic_tuple[0],
                weight=topic_tuple[1],
                topic=new_topic
            )

    return topic_group


def add_collections_to_topic_group(topic_group, collections):
    collections_objects = [CorpusItemCollection.objects.get(pk=c['id']) for c in collections]
    for c in collections_objects:
        topic_group.collections.add(c)


######TOPIC MODELING CELERY TASK######
from litmetricscore.celery import app


@app.task()
def topic_modeling_celery_task(collection_data, options, user, *args, **kwargs):
    # get user from user id
    user = User.objects.get(pk=user)

    words_and_filters = grab_initial_bof_query_set_with_filers_from_view(collection_data)
    # list of tuples containing a (list of docs, filter)

    # loop through words with filters, apply the filters and return that to a bag of words list to send to gensim.
    filtered_docs = []
    for tup in words_and_filters:
        filtered_docs += apply_filter_to_collection(tup)

    # handle chunk by count case
    if options['chunking'] == "count":
        chunked_words_bags = []
        for bag in filtered_docs:
            chunked_words_bags += chunk_bag_of_word_collection_by_chunk_size(bag, options['chunk_size'])

    # handle chunk by breakchar string
    if options['chunking'] == 'breakword':
        chunked_words_bags = []
        for bag in filtered_docs:
            chunked_words_bags += chunk_bag_of_word_collection_by_char_string(bag, options['breakword'])

    # handle no chunking
    if options['chunking'] == 'none':
        chunked_words_bags = []
        for bag in filtered_docs:
            chunked_words_bags.append(bag)

    # turn the tokens into words with the lemmatization and wordnet addition options
    bag_of_docs_to_send_to_gensim = []
    for bag in chunked_words_bags:
        if options['wordNetSense']:
            bag_of_docs_to_send_to_gensim.append(tag_words_with_wordsense_id(bag, options['lemmas']))
        else:
            bag_of_docs_to_send_to_gensim.append(return_untagged_queryset_as_word_list(bag, options['lemmas']))

    # set up and execute gensim modeling
    handler = LdaHandler(bag_of_docs_to_send_to_gensim)
    handler.create_dictionary()
    handler.create_corpus()
    handler.train_lda_model(options['numTopics'], 2, options['numPasses'], options)

    topics = handler.lda_model.show_topics(num_topics=options['numTopics'], num_words=10, log=False, formatted=False)

    # create output models
    topic_group = build_and_save_topic_tuples_and_topic_groups(topics, user, collection_data)
    # relate collections to topic group
    add_collections_to_topic_group(topic_group, collection_data)

    # email upon completion

    return topics


@app.task()
def hdp_celery_task(collection_data, options, user):
    user = User.objects.get(pk=user)

    words_and_filters = grab_initial_bof_query_set_with_filers_from_view(collection_data)
    # list of tuples containing a (list of docs, filter)

    # loop through words with filters, apply the filters and return that to a bag of words list to send to gensim.
    filtered_docs = []
    for tup in words_and_filters:
        filtered_docs += apply_filter_to_collection(tup)

    # handle chunk by count case
    if options['chunking'] == "count":
        chunked_words_bags = []
        for bag in filtered_docs:
            chunked_words_bags += chunk_bag_of_word_collection_by_chunk_size(bag, options['chunk_size'])

    # handle chunk by breakchar string
    if options['chunking'] == 'breakword':
        chunked_words_bags = []
        for bag in filtered_docs:
            chunked_words_bags += chunk_bag_of_word_collection_by_char_string(bag, options['breakword'])

    # handle no chunking
    if options['chunking'] == 'none':
        chunked_words_bags = []
        for bag in filtered_docs:
            chunked_words_bags.append(bag)

    # turn the tokens into words with the lemmatization and wordnet addition options
    bag_of_docs_to_send_to_gensim = []
    for bag in chunked_words_bags:
        if options['wordNetSense']:
            bag_of_docs_to_send_to_gensim.append(tag_words_with_wordsense_id(bag, options['lemmas']))
        else:
            bag_of_docs_to_send_to_gensim.append(return_untagged_queryset_as_word_list(bag, options['lemmas']))

    # set up and execute gensim modeling
    handler = LdaHandler(bag_of_docs_to_send_to_gensim)
    handler.create_dictionary()
    handler.create_corpus()
    handler.train_hdp_model(options)

    topics = handler.hdp_model.show_topics(topics=-1, log=False, formatted=False)

    # create output models
    topic_group = build_and_save_topic_tuples_and_topic_groups(topics, user, collection_data)
    # relate collections to topic group
    add_collections_to_topic_group(topic_group, collection_data)

    # email upon completion
    return topics

@app.task()
def lsi_celery_task(collection_data, options, user):
    user = User.objects.get(pk=user)

    words_and_filters = grab_initial_bof_query_set_with_filers_from_view(collection_data)
    # list of tuples containing a (list of docs, filter)

    # loop through words with filters, apply the filters and return that to a bag of words list to send to gensim.
    filtered_docs = []
    for tup in words_and_filters:
        filtered_docs += apply_filter_to_collection(tup)

    # handle chunk by count case
    if options['chunking'] == "count":
        chunked_words_bags = []
        for bag in filtered_docs:
            chunked_words_bags += chunk_bag_of_word_collection_by_chunk_size(bag, options['chunk_size'])

    # handle chunk by breakchar string
    if options['chunking'] == 'breakword':
        chunked_words_bags = []
        for bag in filtered_docs:
            chunked_words_bags += chunk_bag_of_word_collection_by_char_string(bag, options['breakword'])

    # handle no chunking
    if options['chunking'] == 'none':
        chunked_words_bags = []
        for bag in filtered_docs:
            chunked_words_bags.append(bag)

    # turn the tokens into words with the lemmatization and wordnet addition options
    bag_of_docs_to_send_to_gensim = []
    for bag in chunked_words_bags:
        if options['wordNetSense']:
            bag_of_docs_to_send_to_gensim.append(tag_words_with_wordsense_id(bag, options['lemmas']))
        else:
            bag_of_docs_to_send_to_gensim.append(return_untagged_queryset_as_word_list(bag, options['lemmas']))

    # set up and execute gensim modeling
    handler = LdaHandler(bag_of_docs_to_send_to_gensim)
    handler.create_dictionary()
    handler.create_corpus()
    handler.compute_lsi(num_topics=options['num_topics'])

    topics = handler.lsi_model.show_topics(formatted=False)

    # create output models
    topic_group = build_and_save_topic_tuples_and_topic_groups(topics, user, collection_data)
    # relate collections to topic group
    add_collections_to_topic_group(topic_group, collection_data)

    # email upon completion
    return topics
