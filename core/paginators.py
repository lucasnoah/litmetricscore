from rest_framework.pagination import PageNumberPagination

class TokenPagination(PageNumberPagination):

    page_size = 700
    page_size_query_param = 'page_size'
    max_page_size = 500

