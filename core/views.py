from  rest_framework import viewsets
from core.serializers import *
from core.models import *
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from core.document_processing import initial_document_dump, save_locked_collection
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import *
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from core.document_processing import create_download_of_parsed_collection

class TextFileViewSet(viewsets.ModelViewSet):

    serializer_class = TextFileSerializer
    queryset = TextFile.objects.all()
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (IsAuthenticated,)

    def create(self, request):
        self.request.data['user'] = self.request.user.id
        serializer = TextFileSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        title = self.request.data['title']
        serializer.save()

        text_file = TextFile.objects.last()
        print 'collection', self.request.data.get('collection'), self.request.data.get('collection') == 'true'
        if not self.request.data.get('collection') == 'true':
            #create a corpus item
            corpus_item = CorpusItem.objects.create(
                title=title,
                user=text_file.user,
                text_file=text_file,
                public=False,
                is_processing=True
            )

            corpus_item = CorpusItem.objects.last()

            initial_document_dump.delay(text_file.id, corpus_item.id)

        else:
            save_locked_collection(text_file, title=title)

        return Response(status=200)


class CorpusItemViewSet(viewsets.ModelViewSet):

    serializer_class = CorpusItemSerializer
    queryset = CorpusItem.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        print 'Im a pony'
        return CorpusItem.objects.filter(user=user)


class CorpusItemCollectionViewset(viewsets.ModelViewSet):

    serializer_class = CorpusItemCollectionSerializer
    queryset = CorpusItemCollection.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return CorpusItemCollection.objects.filter(user=user)

    def create(self, request):

        self.request.data['user'] = self.request.user.id
        c = CorpusItemCollectionSerializer(data=self.request.data)
        c.is_valid(raise_exception=True)
        c.save()
        collections = CorpusItemCollection.objects.filter(user=self.request.user)
        serializer = CorpusItemCollectionSerializer(collections, many=True)
        return Response(status=201, data=serializer.data)

    @list_route(['POST'])
    def add_items(self, request, pk=None):
        corpus_items = CorpusItem.objects.filter(pk__in=self.request.data['corpusItems'])
        collection = CorpusItemCollection.objects.get(pk=self.request.data['corpusCollection'])
        for c in corpus_items:
            collection.corpus_items.add(c)
        collection.save()
        collection = CorpusItemCollection.objects.get(pk=self.request.data['corpusCollection'])
        collection_serializer= CorpusItemCollectionSerializer(collection)


        return Response(status=201, data = collection_serializer.data)

    @list_route(['POST'])
    def remove_item(self, request, pk=None):
        item = CorpusItem.objects.get(pk=self.request.data['item'])
        collection = CorpusItemCollection.objects.get(pk=self.request.data['collection'])
        collection.corpus_items.remove(item)
        collection.save()
        collection = CorpusItemCollection.objects.get(pk=self.request.data['collection'])

        collection_serializer = CorpusItemCollectionSerializer(collection)
        return Response(status=200, data=collection_serializer.data)

    @list_route(['POST'])
    def export(self, request, pk=None):
        collection = self.request.data.get('collection_id')
        filter = self.request.data.get('filter')
        print 'the filter', filter
        return create_download_of_parsed_collection(collection, filter)


class WordTokenViewSet(viewsets.ModelViewSet):

    queryset = WordToken.objects.all()
    serializer_class = WordTokenSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        corpus_id = self.request.query_params['corpus_id']
        corpus_item = CorpusItem.objects.get(pk=corpus_id)
        print corpus_item
        qs = WordToken.objects.filter(sentence__corpus_item=corpus_item)
        print qs
        return qs


    @detail_route(['PATCH'])
    def update_token(self, request, pk=None):
        token = WordToken.objects.get(pk=pk)
        if token.sentence.corpus_item.user == self.request.user:
            token.pos = self.request.data['pos']
            token.ner = self.request.data['ner']
            token.original_text = self.request.data['original_text']
            token.lemma = self.request.data['lemma']
            token.save()
            token = WordToken.objects.get(pk=pk)
            serializer = WordTokenSerializer(token)
            return Response(status=200, data=serializer.data)

        else:
            return Response(status=403, data='Not your token bro.')




class CorpusItemFilterViewSet(viewsets.ModelViewSet):

    queryset = CorpusItemFilter.objects.all()
    serializer_class = CorpusItemFilterSerializer

    def get_queryset(self):
        qs = CorpusItemFilter.objects.filter(user=self.request.user)
        return qs

    def perform_create(self, serializer):
        instance = serializer.save(user=self.request.user)