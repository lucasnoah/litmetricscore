from django.conf import settings

import jsonrpclib

def chunk_string_into_parts(chunk_size, input_string):
    chunks = []
    off_set = 0
    number_of_chunks = len(input_string) / chunk_size
    pass

def parse_core_nlp_text(string):
    url = settings.CORE_NLP_SERVER_URL
    headers = {'content-type': 'application/json'}

    server = jsonrpclib.Server(url)


    return server.foo(string)