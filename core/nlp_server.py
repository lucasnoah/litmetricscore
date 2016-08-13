from django.conf import settings

import jsonrpclib


def parse_core_nlp_text(string):
    """"
    :param string:
    :return:
    """
    url = settings.CORE_NLP_SERVER_URL
    headers = {'content-type': 'application/json'}
    try:
        server = jsonrpclib.Server(url)
        output = server.foo(string)
    except Exception as e:
        print e
    return output