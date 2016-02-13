from topic_modeling.models import *
from rest_framework import serializers

class TopicModelGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = TopicModelGroup

class TopicSerializer(serializers.ModelSerializer):

    class Meta:
        model = Topic


class TopicTuple(serializers.ModelSerializer):

    class Meta:
        model = TopicModelGroup
