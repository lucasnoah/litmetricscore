from models import TopicModelGroup, TopicTuple, Topic
import csv
from django.http import HttpResponse
import itertools

def chunk_bag_of_word_collection_by_chunk_size(list_to_chunk, chunk_size):
    """
    Chunk a bag of word token into chunks of x size
    :param list_to_chunk:
    :param chunk_size:
    :return:
    """

    if chunk_size < 1:
        raise IOError

    counter = 0
    chunks = []
    while counter < len(list_to_chunk):
        if counter + chunk_size > len(list_to_chunk):
            chunks.append(list_to_chunk[counter:])

        else:
            chunks.append(list_to_chunk[counter:counter+chunk_size])

        counter += chunk_size

    return chunks

def chunk_bag_of_word_collection_by_char_string(word_bag, breakstring):
    """
    Chunk tokens in a word by using a breakstring.
    :param word_bag:
    :param breakstring:
    :return:
    """
    return [list(g) for k, g in itertools.groupby(word_bag, lambda x: x.original_text in (breakstring,)) if not k]



def grab_topic_tuple_sets_for_topic_modeling_group(topic_model_group_id):
    """
    return a list of topic model tuples for a topic modeling group
    :param topic_model_group_id:
    :return:
    """
    topics = Topic.objects.filter(topic_model_group__id=topic_model_group_id)
    tuples = [TopicTuple.objects.filter(topic=topic) for topic in topics]
    return tuples

def create_topic_list(topic_tuples_list):
    """
    format the tuples to dumpo into the csv file
    :param topic_tuples_list:
    :return:
    """
    topics = []
    for topic in topic_tuples_list:
        tuple_list = [t.word + ' : ' + str(t.weight) for t in topic]
        topics.append(tuple_list)
    return topics

def create_csv_from_topics_list(topics_list):
    """
    Create the csv file for the list of topics
    :param topics_list:
    :return:
    """
    filename = 'something.csv'
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=' + '"' + filename + '"'
    writer = csv.writer(response)
    for topic in topics_list:
        writer.writerow(topic)
    return response

