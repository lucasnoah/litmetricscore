# -*- coding: UTF-8 -*-
from topic_modeling.models import *
from rest_framework import serializers
from core.serializers import CorpusItemCollectionSerializer
import json

class TopicTupleSerializer(serializers.ModelSerializer):

    class Meta:
        model = TopicTuple


class TopicSerializer(serializers.ModelSerializer):

    class Meta:
        model = Topic

    def to_representation(self, instance):
        return{
            "tuples": TopicTupleSerializer(TopicTuple.objects.filter(topic=instance), many=True).data,
            "u_mass": instance.u_mass or None
        }


class TopicModelGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = TopicModelGroup

    def to_representation(self, instance):

        return {
            "id": instance.id,
            "created": instance.created,
            "topics": TopicSerializer(Topic.objects.filter(topic_model_group=instance), many=True).data,
            "collections": CorpusItemCollectionSerializer(instance.collections.all(), many=True).data,
            "method": instance.method,
            "options": json.loads(instance.options)
        }


class LsiResultSerializer(serializers.ModelSerializer):

    class Meta:
        model = LsiResult

    def to_representation(self, instance):

        return {
            "query_term": instance.query_term,
             "results": json.loads(instance.results),
             "collections": CorpusItemCollectionSerializer(instance.collections.all(), many=True).data,
             "created": instance.created
        }
