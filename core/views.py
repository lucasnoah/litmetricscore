from  rest_framework import viewsets
from core.serializers import *
from core.models import *
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from core.document_processing import initial_document_dump, save_locked_collection
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import *
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from core.document_processing import create_download_of_parsed_collection, grab_consolidated_filtered_list_from_collection_and_filter
from core.paginators import TokenPagination

class TextFileViewSet(viewsets.ModelViewSet):

    """
    Text files represent a plain uploaded text without any processing at all. Use this endpoint to upload .txt files.
    """

    serializer_class = TextFileSerializer
    queryset = TextFile.objects.all()
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (IsAuthenticated,)

    def create(self, request):
        """
        Upload a text file and create a corresponding corpus collection. This also starts the celery task to begin
        processing the the uploading document.
        :param request:
        :return:
        """
        self.request.data['user'] = self.request.user.id
        serializer = TextFileSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        title = self.request.data['title']
        serializer.save()

        text_file = TextFile.objects.last()
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

            #pass vard options and plug in defaults where necisarry
            vard_options = {}
            if self.request.data['vard'] == 'true':
                vard_options['vard'] = True
                vard_options['fScore'] = self.request.data['fScore']
                vard_options['threshold'] = self.request.data['threshold']
            else:
                vard_options['vard'] = False

            initial_document_dump.delay(text_file.id, corpus_item.id, vard_options)

        else:
            print "saving locked collection"
            save_locked_collection.delay(text_file.id, title=title)


        return Response(status=200)


class CorpusItemViewSet(viewsets.ModelViewSet):

    """
    Corpus Items represent the master PK for a processed text.  Each text you upload creates a corpus item and all
    corresponding sentences and tokens are tied to this object.
    """

    serializer_class = CorpusItemSerializer
    queryset = CorpusItem.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return CorpusItem.objects.filter(user=user)

    @list_route(['GET'])
    def view_corpus(self, pk=None):

        corpus_item_id = self.request.data.get('coprus_item')
        sentences = Sentence.objects.filter(corpus_item__id=corpus_item_id)

        pass

class CorpusItemCollectionViewset(viewsets.ModelViewSet):

    """
    The Corpus Item Collection represents a set of corpus items grouped together so that they can be sent to
    the Topic Modeling methods as a single unit. Collections are oft paired with filters to help define custom token
    sets to send to the topic modeling workers.
    """

    serializer_class = CorpusItemCollectionSerializer
    queryset = CorpusItemCollection.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return CorpusItemCollection.objects.filter(user=user)

    def create(self, request):
        """
        Create a collection and tag it with a user.
        :param request:
        :return:
        """

        self.request.data['user'] = self.request.user.id
        c = CorpusItemCollectionSerializer(data=self.request.data)
        c.is_valid(raise_exception=True)
        c.save()
        collections = CorpusItemCollection.objects.filter(user=self.request.user)
        serializer = CorpusItemCollectionSerializer(collections, many=True)
        return Response(status=201, data=serializer.data)

    @list_route(['POST'])
    def add_items(self, request, pk=None):
        """
        Add corpus items to a collection
        :param request:
        :param pk:
        :return:
        """
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
        """
        Remove a corpus item for the collection
        :param request:
        :param pk:
        :return:
        """
        item = CorpusItem.objects.get(pk=self.request.data['item'])
        collection = CorpusItemCollection.objects.get(pk=self.request.data['collection'])
        collection.corpus_items.remove(item)
        collection.save()
        collection = CorpusItemCollection.objects.get(pk=self.request.data['collection'])

        collection_serializer = CorpusItemCollectionSerializer(collection)
        return Response(status=200, data=collection_serializer.data)

    @list_route(['POST'])
    def export(self, request, pk=None):
        """
        Export a filtered collection as a set of tokens separated by spaces in a .txt format.
        :param request:
        :param pk:
        :return:
        """

        # is a list of corpus items and id's
        collection = self.request.data.get('collection')
        # filter data
        filter = self.request.data.get('filter')
        # type of export
        export_type = self.request.data.get('export_type')
        from core.exporters import ExportManager
        em = ExportManager(collection, filter, export_type)
        url = em.do_export()
        # create_download_of_parsed_collection(collection['id'], filter)
        return Response(status=200, data={"url":url})


class WordTokenViewSet(viewsets.ModelViewSet):

    """
    Word Tokens represent individual words that have been parsed by the Stanford coreNLP server. Each Word Token has a
    variety of fields associated with it that can be used for filtering and other math functions.
    """

    queryset = WordToken.objects.all()
    serializer_class = WordTokenSerializer
    pagination_class = TokenPagination

    def get_queryset(self):
        corpus_id = self.request.query_params['corpus_id']
        corpus_item = CorpusItem.objects.get(pk=corpus_id)
        qs = WordToken.objects.filter(sentence__corpus_item=corpus_item)
        return qs


    @detail_route(['PATCH'])
    def update_token(self, request, pk=None):
        """
        Update fields in a single Word token
        :param request:
        :param pk:
        :return:
        """
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

    """
    Filters represent a set of filtering objects to apply to a CorpusItemCollection
    """

    queryset = CorpusItemFilter.objects.all()
    serializer_class = CorpusItemFilterSerializer

    def get_queryset(self):
        qs = CorpusItemFilter.objects.filter(user=self.request.user)
        return qs

    def perform_create(self, serializer):
        instance = serializer.save(user=self.request.user)

    @list_route(['POST'])
    def save_filter(self, pk=None):

        filter = CorpusItemFilter.objects.get(pk=self.request.data.get('id'))
        if self.request.user.id != filter.user.id:
            return Response(status=403)
        else:
            filter.filter_data = self.request.data.get('filter_data')
            filter.save()
            return Response(status=200)
