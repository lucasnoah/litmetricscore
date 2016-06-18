from core.models import *
from core.nlp_server import *
from sentence_parsers import *
from litmetricscore.celery import app
from vard.interface import *
from topic_modeling.python_based import apply_filter_to_collection, select_only_desired_pos_tags,\
    filter_out_named_entities, filter_out_stopwords
from django.http import HttpResponse

from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives


def send_document_done_email(user, doc_name):
    send_mail("litmetrics Document Done Processing", doc_name + ' has finished processing',
              "litmetrics <info@litmetrics.com", [user.email])


@app.task()
def initial_document_dump(text_file_id, corpus_item_id):
    """
    pos tags and loads a corpus-item into the db from and uploaded text file
    :param text_file:
    :param text_file_title:
    :return:
    """
    print 'start corpus proccessing'
    text_file = TextFile.objects.get(pk=text_file_id)
    corpus_item = CorpusItem.objects.get(pk=corpus_item_id)

    #open up the file and read it into memory
    #do var and return text in memory
    #print text_file.file
    try:
        document_text = do_vard(text_file.file)
        print 'vard is over'
    except Exception as e:
        print e
        document_text = text_file.file.read()

    #send the file to be parsed by server
    try:
        parsed_text = parse_core_nlp_text(document_text)
    except Exception as e:
        print e
    print 'parsing done'

    #loop through the output and dump it in the database
    sentences = parsed_text['sentences']

    #deal with bulk save
    words_to_save = []

    for sentence in sentences:
        handler = SentenceHandler(sentence, corpus_item)
        words_to_save = words_to_save + handler.process_sentence()

    print len(words_to_save)

    #buld save the words
    WordToken.objects.bulk_create(words_to_save)

    #set the corpus items processing status to done
    corpus_item.is_processing = False
    corpus_item.save()

    #send of an email to notify the user
    send_document_done_email(corpus_item.text_file.user, corpus_item.title)

    print 'corpus has been processed'

def grab_consolidated_filtered_list_from_collection_and_filter(corpus_collection, filter):
    # grab the word tokens

    if filter['name'] == 'default':
        filter['filter_data'] = settings.DEFAULT_FILTER
    if filter['name'] == 'none':
        filter['filter_data'] = settings.NONE_FILTER

    corpus_items = CorpusItem.objects.filter(corpusitemcollection=corpus_collection)
    sentence_lists = [Sentence.objects.filter(corpus_item=corpus_item) for corpus_item in corpus_items]
    token_lists = []
    for sentence_list in sentence_lists:
        token_lists += [WordToken.objects.filter(sentence=sentence) for sentence in sentence_list]

    filtered_tokens = []
    for token_list in token_lists:
        qs = select_only_desired_pos_tags(token_list, filter['filter_data']['pos'])
        qs = filter_out_named_entities(qs, filter['filter_data']['ner'])
        qs = filter_out_stopwords(qs, filter['filter_data']['stopwords'])
        filtered_tokens += list(qs)
    return filtered_tokens

def dump_collection_to_plain_text(corpus_collection, filter):
    """
    Takes in a collection and a filter and returns the filtered tokens as a space separated string
    :param corpus_collection:
    :param filter:
    :return:
    """
    tokens = grab_consolidated_filtered_list_from_collection_and_filter(corpus_collection, filter)
    output_string = " ".join([token.original_text for token in tokens])
    return output_string

def parse_locked_text_upload(text_file):

    parsed_text = text_file.read().split(" ")
    return parsed_text

def save_locked_collection(text_file, title):
    CorpusItemCollection(
        title=title,
        user=text_file.user,
        locked=True
    ).save()

    collection = CorpusItemCollection.objects.last()
    parsed_list = parse_locked_text_upload(text_file.file.file)
    counter = 0
    for token in parsed_list:
        LockedWordToken(
            collection=collection,
            word=token,
            token_index=counter,
        ).save()
        counter += 1
    return collection



def create_download_of_parsed_collection(corpus_collection, filter):
    """
    Create the csv file for the list of topics
    :param topics_list:
    :return:
    """
    filename = 'something.csv'
    response = HttpResponse(content_type='text')
    response['Content-Disposition'] = 'attachment; filename=' + '"' + filename + '"'
    body = dump_collection_to_plain_text(corpus_collection, filter)
    response.write(body)
    print 'sending resonse', response
    return response


