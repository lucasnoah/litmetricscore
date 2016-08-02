ner_list = ['PERSON', 'LOCATION', 'ORGANIZATION', 'MISC', 'MONEY', 'NUMBER', 'ORDINAL', 'PERCENT', 'DATE', 'TIME', 'DURATION','SET']

def select_only_desired_pos_tags(qs, pos_tag_list):
    """
    remove unwanted pos tags from query set
    """
    filtered = qs.filter(pos__in=pos_tag_list)
    return filtered


def filter_out_named_entities(qs, named_entity_choice):
    """
    remove name entities from queryset
    """

    if named_entity_choice:
        return qs.exclude(ner__in=ner_list)

    else:
        return qs


def filter_out_stopwords(qs, stopword_set):
    """
    remove stopwords from queryset
    """
    #stopword_set.replace(" ", "")
    stopword_set = stopword_set.split(",")
    print len(stopword_set)
    return qs.exclude(original_text__in=stopword_set)


def tag_words_with_wordsense_id(bag_of_tokens, use_lemmas):
    """
    Take a query_set and return its wordnet sense tagged output with an option to use either to word or the lemma
     as a base
    """
    if use_lemmas:
        return [(token.lemma + str(token.wordnet_id)) for token in bag_of_tokens]

    else:
        return [(token.word + str(token.wordnet_id)) for token in bag_of_tokens]


def return_untagged_queryset_as_word_list(bag_of_tokens, use_lemmas):
    """
    Execute the queryset and return a list of either words or lemmas in its place
    """
    if use_lemmas:
        return [token.lemma for token in bag_of_tokens]
    else:
        return[token.word for token in bag_of_tokens]



