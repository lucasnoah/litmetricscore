from django.db import models
from django.contrib.auth.models import User
from core.models import *


class TopicModelGroup(models.Model):
    user = models.ForeignKey(User)
    input_data = models.TextField()
    collections = models.ManyToManyField(CorpusItemCollection)
    created = models.DateTimeField(auto_now_add=True)
    method = models.CharField(max_length=30, default='lda')
    options = models.TextField()


class Topic(models.Model):
    """
    Represents as single calculated topic
    """

    topic_model_group = models.ForeignKey(TopicModelGroup)


class TopicTuple(models.Model):
    """
    represents a word in a topic modeling topic
    """

    weight = models.FloatField()
    word = models.CharField(max_length=150)
    topic = models.ForeignKey(Topic)

    def __unicode__(self):
        return self.word + ' | ' + str(self.weight)


class LsiResult(models.Model):
    """
    Represents the return results and query options for a an LSI query.
    """

    query_term = models.CharField(max_length=200)
    results = models.TextField()
    user = models.ForeignKey(User)
    collections = models.ManyToManyField(CorpusItemCollection)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(self.created)


