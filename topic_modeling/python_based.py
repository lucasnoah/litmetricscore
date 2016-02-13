from gensim import corpora, models, similarities
from gensim.models.ldamodel import LdaModel
from core.models import WordToken
from topic_modeling.filters import *
from topic_modeling.models import *

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


###HELPER FUNCTIONS FOR CELERY TEST###


def grab_tokens_for_corpus_item(id):
    return WordToken.objects.filter(sentence__corpus_item_id=id)



def grab_initial_bof_query_set_with_filers_from_view(collection_data):

    collection_bof_list = []
    for collection in collection_data:
        #grab list of id's for corpus items in collection
        list_of_corpus_items_ids_in_collection = [c['id'] for c in collection['items']]
        #grabs a list of token lists
        document_token_list = [grab_tokens_for_corpus_item(id) for id in list_of_corpus_items_ids_in_collection]
        collection_bof_list.append((document_token_list, collection['filter']))
    return collection_bof_list

def apply_filter_to_collection(collection_tuple):
    """
    Applies the filters to the collection/filter tuples and returns a list of words for gensim.
    :param collection_tuple:
    :return:
    """
    collection_token_lists = collection_tuple[0]
    filter = collection_tuple[1]
    document_token_bag = []
    for l in collection_token_lists:
        qs = select_only_desired_pos_tags(l, filter['filter_data']['pos'])
        qs = filter_out_named_entities(qs, filter['filter_data']['ner'])
        qs = filter_out_stopwords(qs, filter['filter_data']['stopwords'])
        document_token_bag.append(qs)
    return document_token_bag


def build_and_save_topic_tuples_and_topic_groups(topics, user, collection_data):
    topic_group = TopicModelGroup.objects.create(
        user=user,
        input_data=collection_data
    )

    for topic in topics:
        new_topic = Topic.objects.create(topic_model_group=topic_group)
        #topic_group.
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
def topic_modeling_celery_task(collection_data, options, user):

    #get user from user id
    user = User.objects.get(pk=user)

    words_and_filters = grab_initial_bof_query_set_with_filers_from_view(collection_data)

    #loop through words with filters, apply the filters and return that to a bag of words list to send to gensim.
    bags_of_filtered_word_tokens = []
    for tup in words_and_filters:
        bags_of_filtered_word_tokens.append(apply_filter_to_collection(tup))

    #turn the tokens into words with the lemmatization and wordnet addition options
    bag_of_docs_to_send_to_gensim =[]
    print 'bags_of_filtered_word_tokens', bags_of_filtered_word_tokens
    for bag in bags_of_filtered_word_tokens[0]:
        if options['wordNetSense']:
            bag_of_docs_to_send_to_gensim.append(tag_words_with_wordsense_id(bag, options['lemmas']))
        else:
            bag_of_docs_to_send_to_gensim.append(return_untagged_queryset_as_word_list(bag, options['lemmas']))

    #set up and execute gensim modeling
    handler = LdaHandler(bag_of_docs_to_send_to_gensim)
    handler.create_dictionary()
    handler.create_corpus()
    handler.train_lda_model(options['numTopics'],2,options['numPasses'])

    topics = handler.lda_model.show_topics(num_topics=options['numTopics'], num_words=10, log=False, formatted=False)

    #create output models
    topic_group = build_and_save_topic_tuples_and_topic_groups(topics, user, collection_data)
    #relate collections to topic group
    add_collections_to_topic_group(topic_group, collection_data)

    #email upon completion







