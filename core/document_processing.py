from core.models import *
from core.nlp_server import *
from sentence_parsers import *
from litmetricscore.celery import app
from vard.interface import *

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


