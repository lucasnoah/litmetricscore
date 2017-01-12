from topic_modeling.python_based import CollectionParser
from core.models import CorpusItemCollection
from django.conf import settings
import uuid
import string
from django.utils.crypto import get_random_string
import itertools, operator


class ExportManager:
    """
    Handles raw text and csv exporting.
    """

    def __init__(self, collection, filter, export_type):

        self.export_types = {
            # raw text, no delimiters, no punctuation: meet spot see spot run spot is fast then spot got hit by a car he was not fast enough
            "raw_text": {"function": self.export_raw_text,
                         "wordnet": False},
            # True text with delimiters: Meet spot. See Spot run. ~ Spot is fast.  Then Spot got hit by a car. He wasn't fast enough.
            "true_text": {"function": self.export_true_text,
                         "wordnet": False},
            # Pipe delimited chunked text every (4) words: meet spot see spot | run spot is fast | then spot got hit | by a car he | was not fast enough
            "pipe_four": {"function": self.export_pipe_four,
                         "wordnet": False},
            # Pipe delimited chunked by sentence: meet spot. | see spot run. | spot is fast. | then spot got hit by a car. | he was not fast enough
            "pipe_sentence": {"function": self.export_pipe_sentence,
                            "wordnet": False},
            # Pipe delimited with filter tags etc: form is token-POS-WordSenseID, if filter includes substituting Named Entities, then the export would replace pronouns with referents: meet-v-1.0 spot-np | see-v-1.0
            "pipe_tagged": {"function": self.export_pipe_tagged,
                         "wordnet": True}
        }

        try:
            self.export_funct = self.export_types[export_type]
        except KeyError:
            raise IOError('not a real exort typsssse')

        wordnet_status = self.export_funct['wordnet']

            # overide the collections filter wordnet status.  This should probably live somewhere else in the future.
        self.tokens = CollectionParser(collection['id'], filter, wordnet_status=wordnet_status).get_tokens()


    def upload_data_to_s3(self, export_string):
        import boto3
        s3 = boto3.resource('s3')
        print s3.meta.client.head_bucket(Bucket= settings.AWS_BUCKET_NAME)
        filename = get_random_string() + ".txt"
        s3.Object(settings.AWS_BUCKET_NAME, filename).put(Body=export_string, Key=filename, ACL='public-read')
        s3 = boto3.client('s3')
        url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': settings.AWS_BUCKET_NAME,
                'Key': filename
            }
        )
        return url


    def export_raw_text(self):
        output_string = " ".join([token.word for token in self.tokens if token.word not in list(string.punctuation)])
        print "OUTPUT STRING", output_string
        return self.upload_data_to_s3(output_string)

    def export_true_text(self):
        output_string = " ".join([token.word for token in self.tokens])
        print "OUTPUT STRING", output_string
        return self.upload_data_to_s3(output_string)

    def export_pipe_four(self):
        # select tokens without punctuation
        tokens = [token.word for token in self.tokens if token.word not in list(string.punctuation)]
        # chunk it
        chunks = [tokens[i:i + 4] for i in xrange(0, len(tokens), 4)]
        chunk_list = []
        # join chunks into strings
        for chunk in chunks:
            raw = " ".join(chunk)
            chunk_list.append(raw)

        # join stringed chunks into big string
        output_string = " | ".join(chunk_list)

        print output_string

        return self.upload_data_to_s3(output_string)

    def export_pipe_sentence(self):
        get_attr = operator.attrgetter('sentence')
        sentence_list = [list(g) for k, g in itertools.groupby(sorted(self.tokens, key=get_attr), get_attr)]
        sentence_string_chunks = []
        for sentence in sentence_list:
            raw_chunk = " ".join(sorted([x.word for x in sentence], key=lambda x: x.id ))
            sentence_string_chunks.append(raw_chunk)
        output_string = " | ".join(sentence_string_chunks)
        print output_string
        return self.upload_data_to_s3(output_string)


    def export_pipe_tagged(self):
        tokens = [token.word + "-" + token.pos+ "-" + token.wordnet_id for token in self.tokens if token.word not in list(string.punctuation)]
        output_string = " | ".join(tokens)
        print output_string
        return self.upload_data_to_s3(output_string)

    def do_export(self):
        return self.export_funct.get('function')()
