"""
Copyright 2011-13 Attila Zseder
Email: zseder@gmail.com

This file is part of hunmisc project
url: https://github.com/zseder/hunmisc

hunmisc is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
"""


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
