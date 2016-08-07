from core.models import Sentence, WordToken, SentenceDependency
import json
import nltk
from core.pywsd.lesk import simple_lesk
ENGLISH_STOPWORDS = nltk.corpus.stopwords.words('english')


def sentences_to_dict(json_data):
    """
    load sentences into python format
    :param json_data:
    :return:
    """
    d = json.loads(json_data)
    return d['sentences']


def create_and_save_a_sentence(sentence_dict, corpus_item):
    """
    Create a new sentence and import info from a sentence dict.
    :param sentence_dict:
    :param corpus_item:
    :return:
    """
    sentence = Sentence()
    sentence.index = sentence_dict['index']
    sentence.corpus_item = corpus_item
    return sentence.save()


def check_if_word_is_stopword(word):
    if word.lower() in ENGLISH_STOPWORDS:
        return True
    else:
        return False

def create_and_save_word_token(token_dict, sentence):
    """
    creates and saves a word token from a word token dict and a sentence object.
    :param token_dict:
    :param sentence:
    :return:
    """
    wt = WordToken(
        after = token_dict['after'],
        before = token_dict['before'],
        character_offset_begin = token_dict['characterOffsetBegin'],
        character_offset_end = token_dict['characterOffsetEnd'],
        index = token_dict['index'],
        lemma = token_dict['lemma'],
        ner = token_dict['ner'],
        original_text=token_dict['originalText'],
        pos=token_dict['pos'],
        word=token_dict['word'],
        is_stopword=check_if_word_is_stopword(token_dict['word']),
        sentence=sentence
    )
    return wt


def create_and_save_sentence_dependency(type, dependecy_dict, sentence):
    """
    parses a sentence dependency into an ORM object and saves its.
    :param type:
    :param dependecy_dict:
    :param sentence:
    :return:
    """
    sd = SentenceDependency()
    sd.type = type
    sd.dep = dependecy_dict['dep']
    sd.governor = dependecy_dict['governor']
    sd.governor_gloss = dependecy_dict['governorGloss']
    sd.dependent = dependecy_dict['dependent']
    sd.dependent_gloss = dependecy_dict['dependentGloss']
    return sd.save()


class SentenceHandler(object):
    """
    Class to handle the parsing tasks for recieved sentences
    """

    def __init__(self, sentence_dict, corpus_item):
        self.sentence_dict = sentence_dict
        self.corpus_item = corpus_item




    def create_sentence(self):
        """
        create the sentece object and make a self referece to it for later use in the handler
        :return:
        """
        s = create_and_save_a_sentence(self.sentence_dict, self.corpus_item)
        self.sentence = Sentence.objects.last()


    def save_word_tokens(self):
        for token in self.sentence_dict['tokens']:
            create_and_save_word_token(token, self.sentence).save()

    def create_bulk_list_of_word_tokens(self):
            tokens = []
            for token in self.sentence_dict['tokens']:
                tokens.append(create_and_save_word_token(token, self.sentence))
            return tokens

    def tag_tokens_with_wordnet_sense(self, tokens):
        sentence = rebuild_sentence_from_tokens(tokens)
        for token in tokens:
            token.wordnet_id = set_disambiguated_wordnet_lemma_for_word(sentence, token.original_text)
        return tokens

    def save_sentence_dependecy_parses(self, parse_type_string):
        for parse in self.sentence_dict[parse_type_string]:
            create_and_save_sentence_dependency(parse_type_string, parse, self.sentence)


    def process_sentence(self):
        self.create_sentence()
        tokens = self.create_bulk_list_of_word_tokens()
        tagged_tokens = self.tag_tokens_with_wordnet_sense(tokens)
        return tagged_tokens
        #for pt in parse_types:
        #    self.save_sentence_dependecy_parses(pt)




def rebuild_sentence_from_tokens(tokens):
    """
    Rebuild a sentence from the list of it's tokens and return the rebuilt string.
    :param tokens:
    :return: sentence
    """

    sentence = tokens[0].original_text
    counter = 1

    while counter < len(tokens):
        for item in tokens:
            if item.index == counter + 1:
                sentence = tokens[counter].original_text + tokens[counter].after + sentence
        counter = counter +  1
    return sentence


def set_disambiguated_wordnet_lemma_for_word(rebuilt_sentence, token_text):
    s = simple_lesk(rebuilt_sentence, token_text)
    return s.lemmas()[0].name()
