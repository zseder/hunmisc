"""Saves a (LSA) model to a file in text format so that it can be imported to
other languages / framework."""

import sys
import numpy
#from gensim import corpora, models
from gensim.models import LsiModel
from langtools.utils.file_utils import FileWriter

#model_mapping = {'tfidf': models.TfidfModel, 'tf-idf': models.TfidfModel,
#                 'lsa': models.LsiModel, 'lsi': models.LsiModel,
#                 'lda': models.LdaModel}
                 
def export_model(model_file, out_file):
    """Saves the model. The output will be utf-8 encoded."""
#    model = model_mapping[model_type].load(model_file)
    model = LsiModel.load(model_file)
    with FileWriter(out_file, 'w').open() as out:
        out.write(u"{0}\t{1}\n".format(model.numTerms, model.numTopics))
        for term in xrange(model.numTerms):
            word = model.id2word.id2token[term].decode("utf-8")
            while len(word) > 0 and not word[-1].isalnum():
                word = word[0:-1]
            out.write(u"{0}\n".format(word))
            out.write(u"{0}\n".format(u"\t".join(str(f) for f in
                    numpy.asarray(model.projection.u.T[:, term]).flatten())))

if __name__ == '__main__':
    export_model(sys.argv[1], sys.argv[2])
