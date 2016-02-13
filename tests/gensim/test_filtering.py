from django.test import TestCase
from core.models import *
import os
from topic_modeling.filters import *
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
test_text_file = PROJECT_ROOT + '/tests/testbook.txt'

import factory


class WordTokenFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WordToken
        django_get_or_create = ('sentence', 'lemma', 'pos', 'word')

    after = 'a'
    before = 'b'
    character_offset_begin = 1
    character_offset_end = 2
    index = 1
    lemma = 'dog'
    ner = 'O'
    original_text = 'doggy'
    pos = 'NN'
    speaker = 'one'
    word = 'dog'
    is_stopword = False
    sentence = ''
    wordnet_id=0



class TestFilters(TestCase):


    def setUp(self):

        #user
        self.user = User.objects.create_user('lucas')

        #text file
        self.text_file = TextFile.objects.create(file=test_text_file, user= self.user)

        # three corpus items
        self.corpus_item_one = CorpusItem.objects.create(
            title='item1',
            text_file=self.text_file,
            user=self.user,
        )

        self.corpus_item_two = CorpusItem.objects.create(
            title='item2',
            text_file=self.text_file,
            user=self.user,
        )

        self.corpus_item_three = CorpusItem.objects.create(
            title='item3',
            text_file=self.text_file,
            user=self.user,
        )

        #create sentences for each corpus item
        self.sentence_one = Sentence.objects.create(
            index=1,
            corpus_item=self.corpus_item_one
        )

        self.sentence_two = Sentence.objects.create(
            index=1,
            corpus_item=self.corpus_item_two
        )

        self.sentence_three = Sentence.objects.create(
            index=1,
            corpus_item=self.corpus_item_three
        )

        # two corpus collections

        self.corpus_collection_one = CorpusItemCollection.objects.create(
            title='collection_one',
            user=self.user
        )

        self.corpus_collection_two = CorpusItemCollection.objects.create(
            title='collection_two',
            user=self.user
        )


    def test_that_it_can_filter_pos_tags_correctly(self):
        WordTokenFactory(sentence=self.sentence_one, lemma='dog', pos="NN", word='doggy', ner='O')
        WordTokenFactory(sentence=self.sentence_one, lemma='running', pos="ADJ", word='run', ner='O')
        WordTokenFactory(sentence=self.sentence_one, lemma='running', pos="JJ", word='run', ner='O')
        all = WordToken.objects.all()
        filtered = select_only_desired_pos_tags(all, ['NN', 'ADJ'])
        self.assertEqual(len(filtered), 2)


    def test_that_it_can_remove_named_entities(self):
        WordTokenFactory(sentence=self.sentence_one, lemma='dog', pos="NN", word='doggy', ner='PERSON')
        WordTokenFactory(sentence=self.sentence_one, lemma='running', pos="ADJ", word='run', ner='LOCATION')
        WordTokenFactory(sentence=self.sentence_one, lemma='running', pos="JJ", word='run', ner='O')
        all = WordToken.objects.all()
        filtered = filter_out_named_entities(all, True)
        self.assertEqual(len(filtered),1)

    def test_that_it_can_remove_stopwords(self):
        WordTokenFactory(sentence=self.sentence_one, lemma='and', pos="NN", word='and', ner='PERSON')
        WordTokenFactory(sentence=self.sentence_one, lemma='the', pos="ADJ", word='run', ner='LOCATION')
        WordTokenFactory(sentence=self.sentence_one, lemma='dog', pos="JJ", word='run', ner='O')
        all = WordToken.objects.all()
        filtered = filter_out_stopwords(all, ['and', 'the'])
        self.assertEqual(len(filtered),1)

    def test_tagging_words_with_wordsense_id(self):
        WordTokenFactory(sentence=self.sentence_one, lemma='and', pos="NN", word='ands', ner='PERSON')
        all = WordToken.objects.all()
        tagged_with_lemmas = tag_words_with_wordsense_id(all, True)
        tagged_without_lemmas = tag_words_with_wordsense_id(all, False)
        self.assertEqual(tagged_with_lemmas[0], 'and0')
        self.assertEqual(tagged_without_lemmas[0], 'ands0')

    def test_queryset_execution(self):
        WordTokenFactory(sentence=self.sentence_one, lemma='and', pos="NN", word='ands', ner='PERSON')
        all = WordToken.objects.all()
        executed_with_lemmas = return_untagged_queryset_as_word_list(all, True)
        executed_with_words = return_untagged_queryset_as_word_list(all, False)
        self.assertEqual(executed_with_lemmas, ['and'])
        self.assertEqual(executed_with_words,['ands'])















