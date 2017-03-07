from rest_framework import viewsets
from topic_modeling.models import *
from topic_modeling.serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import list_route
from rest_framework.response import Response
from core.models import *
from topic_modeling.python_based import topic_modeling_celery_task, hdp_celery_task, lsi_celery_task, mallet_celery_task
from topic_modeling.utils import grab_topic_tuple_sets_for_topic_modeling_group, create_topic_list,\
    create_csv_from_topics_list
import json

####HELPER FUNCTIONS####


####VIEWSETS####


class TopicModelViewSet(viewsets.ModelViewSet):

    """
    Endpoints for sending Corpus Item Collections to topic modeling endpoints and for representing topic modeling
    results
    """

    queryset = TopicModelGroup.objects.all()
    serializer_class = TopicModelGroupSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = TopicModelGroup.objects.filter(user=self.request.user)
        return queryset


    @list_route(['POST'])
    def model_topics(self, request, pk=None):
        """
        Send a collection to be modeled via the standard Gensim Lda Model
        ---
        parameters_strategy: replace
        omit_parameters:
            - path
        parameters:
            - name: collections
              description: a list of collection id's and filters
              required: true
              type: list

        consumes:
            - application/json

        {

              collections: [
                {
                  collectionId: int,
                  filterId: int
                },
                {
                  collectionId: int,
                  filterId: int
                }
              ],

              options: {
                   alpha: string',
                    chunking: bool,
                    gamma_threshold: float,
                    iterations: int,
                    lemmas: bool,
                    minimum_probability: float,
                    numTopics: int,
                    top_n: int,
                    wordNetSense: bool
              },

              filter: 'none' or 'default' or int
            }
        """

        user = self.request.user
        modeling_options = self.request.data['options']
        collection_data = self.request.data['collections']
        topic_modeling_celery_task.delay(collection_data,modeling_options, user.id)
        return Response(status=200)

    @list_route(['POST'])
    def lsi_model_topics(self, request, pk=None):
        """
        Find related words using gensim LSI for any given CorpusItemCollection and a search term.
        """
        user = self.request.user
        modeling_options = self.request.data['options']
        collection_data = self.request.data['collections']
        lsi_celery_task(collection_data, modeling_options, user.id)
        return Response(status=200)

    @list_route(['POST'])
    def hdp_model_topics(self, request, pk=None):
        """
        Use the gensim HDP automatic Model to create a set of topics from a collection
        """
        user = self.request.user
        modeling_options = self.request.data['options']
        collection_data = self.request.data['collections']
        hdp_celery_task.delay(collection_data, modeling_options, user.id)
        return Response(status=200)

    @list_route(['POST'])
    def mallet_model_topics(self, request, pk=None):
        """
        Use mallet to create a set of topics.
        """
        user = self.request.user
        modeling_options = self.request.data['options']
        collection_data = self.request.data['collections']
        mallet_celery_task.delay(collection_data, modeling_options, user.id)
        return Response(status=200)

    @list_route(['POST'])
    def download_topics_csv(self, request, pk=None):
        """
        Download the topic modeling results in a a .csv format for a single set of topic modeling results.
        """
        topic_id = request.data['topic_id']
        try:
            topic_group = grab_topic_tuple_sets_for_topic_modeling_group(topic_id)
        except Exception:
            return Response(status=403, data='Topic was not found, please login or try another topic')
        csv_response = create_csv_from_topics_list(create_topic_list(topic_group))
        return csv_response

    @list_route(['GET'])
    def lsi_results(self, request, pk=None):
        """
        List all the LSI results for a particular user.
        """
        results = LsiResult.objects.filter(user=self.request.user)
        serializer = LsiResultSerializer(results, many=True)
        return Response(status=200, data=serializer.data)






