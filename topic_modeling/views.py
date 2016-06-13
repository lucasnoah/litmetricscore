from rest_framework import viewsets
from topic_modeling.models import *
from topic_modeling.serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import list_route
from rest_framework.response import Response
from core.models import *
from topic_modeling.python_based import topic_modeling_celery_task, hdp_celery_task, lsi_celery_task
from topic_modeling.utils import grab_topic_tuple_sets_for_topic_modeling_group, create_topic_list,\
    create_csv_from_topics_list
import json

####HELPER FUNCTIONS####


####VIEWSETS####


class TopicModelViewSet(viewsets.ModelViewSet):

    queryset = TopicModelGroup.objects.all()
    serializer_class = TopicModelGroupSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = TopicModelGroup.objects.filter(user=self.request.user)
        return queryset


    @list_route(['POST'])
    def model_topics(self, request, pk=None):

        print self.request.data
        user = self.request.user
        modeling_options = self.request.data['options']

        collection_data = self.request.data['collections']

        topic_modeling_celery_task.delay(collection_data,modeling_options, user.id)

        return Response(status=200)

    @list_route(['POST'])
    def lsi_model_topics(self, request, pk=None):
        user = self.request.user
        modeling_options = self.request.data['options']

        collection_data = self.request.data['collections']

        lsi_celery_task.delay(collection_data, modeling_options, user.id)
        return Response(status=200)

    @list_route(['POST'])
    def hdp_model_topics(self, request, pk=None):
        user = self.request.user
        modeling_options = self.request.data['options']

        collection_data = self.request.data['collections']

        hdp_celery_task.delay(collection_data, modeling_options, user.id)
        return Response(status=200)

    @list_route(['POST'])
    def download_topics_csv(self, request, pk=None):
        topic_id = request.data['topic_id']
        try:
            topic_group = grab_topic_tuple_sets_for_topic_modeling_group(topic_id)
        except Exception:
            return Response(status=403, data='Topic was not found, please login or try another topic')

        csv_response = create_csv_from_topics_list(create_topic_list(topic_group))
        return csv_response





