from topic_modeling.models import *
from rest_framework import serializers
from core.serializers import CorpusItemCollectionSerializer


class TopicTupleSerializer(serializers.ModelSerializer):

    class Meta:
        model = TopicTuple


class TopicSerializer(serializers.ModelSerializer):

    class Meta:
        model = Topic

    def to_representation(self, instance):
        return{
            "tuples": TopicTupleSerializer(TopicTuple.objects.filter(topic=instance), many=True).data
        }

class TopicModelGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = TopicModelGroup

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'created': instance.created,
            'topics': TopicSerializer(Topic.objects.filter(topic_model_group=instance), many=True).data,
            'collections': CorpusItemCollectionSerializer(instance.collections.all(), many=True).data

        }