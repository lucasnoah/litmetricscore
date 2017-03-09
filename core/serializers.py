from rest_framework import serializers
from core.models import *


class TextFileSerializer(serializers.ModelSerializer):

    class Meta:
        model = TextFile


class CorpusItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = CorpusItem

    def to_representation(self, instance):
        return {
            'title':  instance.title,
            'public': instance.public,
            'is_processing': instance.is_processing,
            'token_count': WordToken.objects.filter(sentence__corpus_item=instance).count(),
            'id': instance.id
        }

class CorpusItemCollectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = CorpusItemCollection

    def to_representation(self, instance):
        return {
            "id" : instance.id,
            "title" : instance.title,
            "items": CorpusItemSerializer(instance.corpus_items, many=True).data,
            "locked": instance.locked,
            "show": instance.show
        }

class WordTokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = WordToken


class CorpusItemFilterSerializer(serializers.ModelSerializer):

    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)

    class Meta:
        model = CorpusItemFilter


