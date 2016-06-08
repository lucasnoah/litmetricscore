from models import TopicModelGroup, TopicTuple, Topic
import csv
from django.http import HttpResponse


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
    print response.content

    return response