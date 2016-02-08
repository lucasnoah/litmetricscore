from django.db import models
from django.contrib.auth.models import User



class TopicModelGroup(models.Model):
    user = models.ForeignKey(User)




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

