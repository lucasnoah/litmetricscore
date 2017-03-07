from gensim import corpora, models, similarities
from gensim.models.ldamodel import LdaModel
import gensim
from core.models import WordToken
from topic_modeling.filters import *
from topic_modeling.models import *
from django.conf import settings
from topic_modeling.utils import chunk_bag_of_word_collection_by_char_string, chunk_bag_of_word_collection_by_chunk_size
import json
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from litmetricscore.celery import app
from django.core.mail import send_mail
from .gensimsimilarities.word_pair_similarity_matrix import all_in_one_similiarity_matrix
from gensim.models.word2vec import Word2Vec

# gather words to be modeled as a list of words

# create a gensim dictionary object out of all the words. Gensim dictionary accepts a list of texts, which is really
# just a list of tokenized words.

def send_document_done_email(user):
    send_mail("Topic Model Done", "litmetrics Topic modeling has finished processing",
              "litmetrics <info@litmetrics.com", [user.email])


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

    #random_state = int(kwargs.get('random_state')) or None

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

def create_mallet_model(corpus, dictionary, num_topics):
    model = gensim.models.wrappers.LdaMallet(settings.BASE_DIR + '/topic_modeling/mallet_source/mallet-2.0.7/bin/mallet', corpus=corpus, num_topics=num_topics,
                                             id2word=dictionary)
    return model


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

    def train_mallet_model(self, num_topics):
        self.mallet_model = create_mallet_model(self.corpus, self.dictionary, num_topics)

###HELPER FUNCTIONS FOR CELERY TEST###


def grab_tokens_for_corpus_item(id):
    return WordToken.objects.filter(sentence__corpus_item_id=id)


def grab_initial_bof_query_set_with_filers_from_view(collection_data):
    collection_bof_list = []
    for collection in collection_data:
        # grab list of id's for corpus items in collection
        list_of_corpus_items_ids_in_collection = [c.get('id') for c in collection['items']]
        # grabs a list of token lists
        document_token_list = [grab_tokens_for_corpus_item(id) for id in list_of_corpus_items_ids_in_collection]
        if collection['filter']['name'] == 'default':
            collection['filter'] = settings.DEFAULT_FILTER
        elif collection['filter']['name'] == 'none':
            collection['filter'] = settings.NONE_FILTER
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
        qs = filter_out_stopwords(qs, filter['filter_data']['stopwords'])
        qs = filter_out_named_entities(qs, filter['filter_data']['ner'])
        document_token_bag.append(list(qs))
    return document_token_bag


class CollectionParser:

    def __init__(self, collection_id, filter, *args, **kwargs):
        self.collection = CorpusItemCollection.objects.get(pk=collection_id)
        self.lock_status = self.collection.locked
        self.filter = self.get_filter_dict(filter)
        wordnet_status = kwargs.get('wordnet_status')
        if  wordnet_status == None:
            wordnet_status = True
        self.wordnet_status = wordnet_status
        self.token_lists = []
        self.tokens = []
        self.bow = []
        self.grab_and_filter_tokens()
        self.make_bow()


    def get_filter_dict(self, filter_id):
        """
        Handle filling out the data for the standard filters
        :param filter:
        :return:
        """
        if filter_id == 'default':
            filter_to_use = settings.DEFAULT_FILTER.get('filter_data')
        if filter_id == "none":
            filter_to_use = settings.NONE_FILTER.get('filter_data')
        else:
            try:
                filter_to_use = CorpusItemFilter.objects.get(pk=filter_id).filter_data
            except Exception:
                filter_to_use = settings.NONE_FILTER.get('filter_data')

        return filter_to_use

    def apply_filter_to_collection(self):
        document_token_bag = []
        for l in self.token_lists:
            qs = select_only_desired_pos_tags(l, self.filter['pos'])
            qs = filter_out_stopwords(qs, self.filter['stopwords'])
            qs = filter_out_named_entities(qs, self.filter['ner'])
            document_token_bag += list(qs)
        return document_token_bag

    def grab_and_filter_tokens(self):
        """
        differentiate between locked and normal collections and return filtered tokens
        :return:
        """

        if self.lock_status:
            self.tokens = LockedWordToken.objects.filter(collection=self.collection)

        else:
            # grab the items for the collection
            self.token_lists = [grab_tokens_for_corpus_item(item.id) for item in self.collection.corpus_items.all()]
            self.tokens = self.apply_filter_to_collection()

    def get_bow(self):
        return self.bow

    def get_tokens(self):
        return self.tokens

    def do_wordnet_tagging(self, token, out_token):
        """
        Tag tokens with wordnet id's
        :param token:
        :param out_token:
        :return:
        """
        if self.wordnet_status:
            return out_token + '-' + token.wordnet_id
        else:
            return out_token

    def make_bow(self):
        """
        Converts to a list of strings and deals with lemmatization and wordnet id tagging.
        :return:
        """
        if self.filter['lemma'] and not self.lock_status:
            self.bow = [self.do_wordnet_tagging(token, token.lemma) for token in self.tokens]

        else:
            if self.lock_status:
                self.bow = [token.word for token in self.tokens]
            else:
                self.bow = [self.do_wordnet_tagging(token, token.original_text) for token in self.tokens]


def build_and_save_topic_tuples_and_topic_groups(topics, user, collection_data, method, options):
    """
    Format a stash returned topics and topic groups in the database
    :param topics:
    :param user:
    :param collection_data:
    :param method:
    :param options:
    :return:
    """
    topic_group = TopicModelGroup.objects.create(
        user=user,
        input_data=collection_data,
        method=method,
        options=json.dumps(options)
    )

    for topic in topics:
        # topic_group.
        if method == 'mallet':
            new_topic = Topic.objects.create(topic_model_group=topic_group)
            for topic_tuple in topic:
                TopicTuple.objects.create(
                    word=topic_tuple[1],
                    weight=topic_tuple[0],
                    topic=new_topic
                )
        else:
            new_topic = Topic.objects.create(topic_model_group=topic_group, u_mass=topic[1])
            for topic_tuple in topic[0]:
                TopicTuple.objects.create(
                    word=topic_tuple[1],
                    weight=topic_tuple[0],
                    topic=new_topic
                )

    return topic_group

def add_collections_to_topic_group(topic_group, collections):
    """
    Tag topic group with collection data
    :param topic_group:
    :param collections:
    :return:
    """
    collections_objects = [CorpusItemCollection.objects.get(pk=c.get('collectionId')) for c in collections]
    for c in collections_objects:
        topic_group.collections.add(c)


######TOPIC MODELING CELERY TASK######

def return_filtered_documents(words_and_filters):
    filtered_docs = []
    for tup in words_and_filters:
        filtered_docs += apply_filter_to_collection(tup)
    return filtered_docs


@app.task()
def topic_modeling_celery_task(collection_data, options, user, *args, **kwargs):
    """
    Async tosk to do gensim based topic modeling.
    :param collection_data:
    :param options:
    :param user:
    :param args:
    :param kwargs:
    :return:
    """
    # get user from user id
    user = User.objects.get(pk=user)

    # get tokens from collection and parse with filters
    filtered_docs = []
    wordnet_status = options['wordNetSense']
    for item in collection_data:
        # overide the collections filter wordnet status.  This should probably live somewhere else in the future.
        # grab the collection id
        collection_id = item.get('collectionId')
        # grab the filter
        filter_id = item.get('filter')

        tokens = CollectionParser(collection_id, filter_id, wordnet_status=wordnet_status).get_bow()
        filtered_docs.append(tokens)

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

    # set up and execute gensim modeling
    handler = LdaHandler(chunked_words_bags)
    handler.create_dictionary()
    handler.create_corpus()
    update_every = options.get('update_every') or 2
    del options['update_every']
    handler.train_lda_model(options['numTopics'], update_every, options['numPasses'], options)
    handler.lda_model.top_topics(handler.corpus, options['numTopics'])
    topics = handler.lda_model.top_topics(handler.corpus, num_words=options['top_n'])
    # create output models
    topic_group = build_and_save_topic_tuples_and_topic_groups(topics, user, collection_data, 'lda', options)
    # relate collections to topic group
    add_collections_to_topic_group(topic_group, collection_data)

    # email upon completion
    try:
        send_document_done_email(user)
    except Exception as e:
        print e
    return topics

@app.task()
def mallet_celery_task(collection_data, options, user, *args, **kwargs):
    """
    Async mallet task
    :param collection_data:
    :param options:
    :param user:
    :param args:
    :param kwargs:
    :return:
    """
    # get user from user id
    user = User.objects.get(pk=user)

    # get collection tokens and filter them
    filtered_docs = []
    for item in collection_data:
        tokens = CollectionParser(item['id'], item['filter'], wordnet_status=options['wordNetSense']).get_bow()
        filtered_docs.append(tokens)

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

    # set up and execute gensim modeling
    handler = LdaHandler(chunked_words_bags)
    handler.create_dictionary()
    handler.create_corpus()
    handler.train_mallet_model(options['numTopics'])
    topics = handler.mallet_model.show_topics(num_topics=options['numTopics'], log=False, formatted=False, num_words=options['top_n'])
    # create output models
    topic_group = build_and_save_topic_tuples_and_topic_groups(topics, user, collection_data, 'mallet', options)
    # relate collections to topic group
    add_collections_to_topic_group(topic_group, collection_data)

    # email upon completion
    try:
        send_document_done_email(user)
    except Exception as e:
        print e


@app.task()
def hdp_celery_task(collection_data, options, user):
    """
    Async gensim HDP task
    :param collection_data:
    :param options:
    :param user:
    :return:
    """
    user = User.objects.get(pk=user)

    # get tokens from collection and filter them
    filtered_docs = []
    for item in collection_data:
        tokens = CollectionParser(item['id'], item['filter'], wordnet_status=options['wordNetSense']).get_bow()
        filtered_docs.append(tokens)

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

    # set up and execute gensim modeling
    handler = LdaHandler(chunked_words_bags)
    handler.create_dictionary()
    handler.create_corpus()
    handler.train_hdp_model(options)

    topics = handler.hdp_model.show_topics(topics=-1, log=False, formatted=False)

    # create output models
    topic_group = build_and_save_topic_tuples_and_topic_groups(topics, user, collection_data, 'hdp', options)
    # relate collections to topic group
    add_collections_to_topic_group(topic_group, collection_data)

    # email upon completion
    try:
        send_document_done_email(user)
    except Exception as e:
        print e
    return topics


def kClosestTerms(k,term,transformer,model):
    """
    Get k closest terms
    :param k:
    :param term:
    :param transformer:
    :param model:
    :return:
    """

    print 'running KclosestTerms'
    index = transformer.vocabulary_[term]

    model = np.dot(model,model.T)

    closestTerms = {}
    for i in range(len(model)):
        closestTerms[transformer.get_feature_names()[i]] = model[index][i]

    sortedList = sorted(closestTerms , key= lambda l : closestTerms[l])
    print "sorted list in k closest terms"
    print sortedList
    return sortedList[::-1][0:k]


@app.task()
def lsi_celery_task(collection_data, options, user):
    """
    Async task to perform lsa
    :param collection_data:
    :param options:
    :param user:
    :return:
    """
    user = User.objects.get(pk=user)

    # get tokens from collections and filter them
    filtered_docs = []
    wordnet_status = options['wordNetSense']
    print "wordnet status", wordnet_status
    for item in collection_data:
            tokens = CollectionParser(item['id'], item['filter'], wordnet_status=wordnet_status).get_bow()
            filtered_docs.append(tokens)

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

    stringed_docs = []
    for doc in chunked_words_bags:
        stringed_docs.append(" ".join([x.lower() for x in doc]))

    try:
        # set up and execute gensim modeling
        print "#######################333333"
        print "GO GO HANDELR FOR DICT AND DCORPUS"
        handler = LdaHandler(chunked_words_bags)
        handler.create_dictionary()
        handler.create_corpus()


        one_d_vec = None
        working = False
        search_query = options['search_query']
        # loop through the dictionary and find the search query
        for key, val in handler.dictionary.items():
            print key, val, search_query, val==search_query
            if val == options['search_query']:
                print val
                print "###########################################33"
                print "The v key is lit"
                working = True
                one_d_vec = val
                break



        num_topics = 200
        lsi_model = gensim.models.lsimodel.LsiModel(corpus=handler.corpus, num_topics=1, id2word=handler.dictionary,
                                                    chunksize=20000, decay=1.0,distributed=False, onepass=True,
                                                    power_iters=2, extra_samples=100)





        one_d_vec = options['search_query']
        print "####ONE D VECK#####sss"
        print one_d_vec
        sim_table = all_in_one_similiarity_matrix([one_d_vec],handler.dictionary,lsi_model,num_topics,[],True)
        print "Showing similarity table "
        print sim_table


        LsiResult(
            user=user,
            results=json.dumps(terms),
            query_term=options['search_query']
        ).save()
        result = LsiResult.objects.last()
        collections = [CorpusItemCollection.objects.get(pk=c.get('id')) for c in collection_data]
        for collection in collections:
            result.collections.add(collection)
        result.save()
    except Exception as e:
        print e



