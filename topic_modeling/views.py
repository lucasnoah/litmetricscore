from rest_framework import viewsets
from topic_modeling.models import *
from topic_modeling.serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import list_route
from rest_framework.response import Response
from core.models import *
from topic_modeling.python_based import topic_modeling_celery_task
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


