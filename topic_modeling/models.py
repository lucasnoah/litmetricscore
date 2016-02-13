from django.db import models
from django.contrib.auth.models import User
from core.models import *


class TopicModelGroup(models.Model):
    user = models.ForeignKey(User)
    input_data = models.TextField()
    collections = models.ManyToManyField(CorpusItemCollection)


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




