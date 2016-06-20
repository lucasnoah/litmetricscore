from django.conf import settings

import jsonrpclib


def parse_core_nlp_text(string):
    url = settings.CORE_NLP_SERVER_URL
    headers = {'content-type': 'application/json'}
    print 'sending to corenlp server'
    try:
        server = jsonrpclib.Server(url)
        output = server.foo(string)
    except Exception as e:
        print e
    print 'returning from corenlp server'
    return output