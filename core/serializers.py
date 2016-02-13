from rest_framework import serializers
from core.models import *


class TextFileSerializer(serializers.ModelSerializer):

    class Meta:
        model = TextFile


class CorpusItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = CorpusItem

class CorpusItemCollectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = CorpusItemCollection

    def to_representation(self, instance):
        return {
            "id" : instance.id,
            "title" : instance.title,
            "items": CorpusItemSerializer(instance.corpus_items, many=True).data
        }

class WordTokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = WordToken


class CorpusItemFilterSerializer(serializers.ModelSerializer):

    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)

    class Meta:
        model = CorpusItemFilter


