from django.conf import settings

import jsonrpclib

def parse_core_nlp_text(string):
    url = settings.CORE_NLP_SERVER_URL
    headers = {'content-type': 'application/json'}

    server = jsonrpclib.Server(url)

    return server.foo(string)