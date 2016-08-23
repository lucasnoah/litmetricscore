from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField


class TextFile(models.Model):
    """
    An uploaded .txt file containing a source text to be parsed by corenlp
    """

    user = models.ForeignKey(User, to_field='id')
    file = models.FileField(upload_to='')



class CorpusItem(models.Model):
    """
    represents the parsed version of a text file
    """

    title = models.CharField(max_length=150)
    text_file = models.ForeignKey(TextFile)
    user = models.ForeignKey(User)
    public = models.BooleanField(default=False)
    is_processing = models.BooleanField(default=True)



class CorpusItemCollection(models.Model):
    """
    represents a collection of corpus items grouped together for processing
    """
    title = models.CharField(max_length=100)
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True)
    corpus_items = models.ManyToManyField(CorpusItem, blank=True)
    locked = models.BooleanField(default=False)


class CorpusItemFilter(models.Model):

    """
    Describes how a CorpusItemCollection should be filtered before being sent to modeling
    """

    user = models.ForeignKey(User)
    name = models.CharField(max_length=150)
    filter_data = JSONField()
    models.ForeignKey(CorpusItemCollection)


class Sentence(models.Model):
    """
    Each CorpusItem breaks down into a set of sentences
    """

    index = models.IntegerField()
    corpus_item = models.ForeignKey(CorpusItem)


class WordToken(models.Model):
    """
    Each sentence breaks down into a set of word tokens.
    """

    after = models.CharField(max_length=100)
    before = models.CharField(max_length=100)
    character_offset_begin = models.IntegerField()
    character_offset_end = models.IntegerField()
    index = models.IntegerField()
    lemma = models.CharField(max_length=100)
    ner = models.CharField(max_length=25)
    original_text = models.CharField(max_length=100)
    pos = models.CharField(max_length=12)
    speaker = models.CharField(max_length=25, blank=True)
    word = models.CharField(max_length=100)
    is_stopword = models.BooleanField(default=False)
    sentence = models.ForeignKey(Sentence)
    wordnet_id = models.CharField(max_length=50)


class LockedWordToken(models.Model):
    """
    An alternative stripped down word token used for logging manually uploaded collections from the user.
    """

    collection = models.ForeignKey(CorpusItemCollection)
    word = models.CharField(max_length=150)
    token_index = models.IntegerField()


class SentenceDependency(models.Model):
    """
    Represents a dependency parse for a sentence.  Each parse describes a relationship between two tokens and the middle
    word that governs those dependencies.  Each sentence also has multiple parse types of the same format.
    """

    type = models.CharField(max_length=30)
    dep = models.CharField(max_length=25)
    dependent = models.IntegerField()
    dependent_gloss = models.CharField(max_length=100)
    governor = models.IntegerField()
    governor_gloss = models.CharField(max_length=100)




