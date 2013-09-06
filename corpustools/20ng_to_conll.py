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


"""Converts a newsgroup file (as in the 20 Newsgroups collection) to the conll2
format."""

import os.path
import re
from langtools.nltk.nltktools import NltkTools
from langtools.utils import cmd_utils
from langtools.utils.file_utils import *
from langtools.io.conll2.conll_iter import FieldedDocument

re_pat = re.compile(r"^[\s>]+", re.UNICODE)

# Decoding is not required as NltkTools.tag_raw() handles that for utf-8.
def read_stream(ins):
    """Reads a stream. Returns a {field:raw text} map, with a Body field. The
    title is the content of the subject header field."""
    fields = {}
    for line in ins:
        line = line.strip()
        if len(line) == 0:
            break
        if line.startswith("Subject:"):
            fields['Title'] = line[8:]
    
    fields['Body'] = u' '.join(re_pat.sub("", line.strip().replace(u'\ufffd', ' ')) for line in ins)
    return fields

def read_file(infile):
    """Reads a file. Returns a {field:raw text} map, with a Body field. If title
    is true, a Title field will be added too."""
    with FileReader(infile, replace=True).open() as ins:
        return read_stream(ins)

def write_doc(doc, outs):
    """Writes the document to outs. A header line is written, then the
    Title field (if any), then the body."""
    outs.write(u"%%#PAGE\t{0}\n".format(doc.title))
    if 'Title' in doc.fields:
        outs.write(u"%%#Field\tTitle\n")
        write_text(doc.fields['Title'], outs)
    outs.write(u"%%#Field\tBody\n")
    write_text(doc.fields['Body'], outs)
            
def write_text(text, outs):
    for token in text:
        outs.write(u"\t".join(token))
        outs.write("\n")

if __name__ == '__main__':
    import sys
    
    try:
        params, args = cmd_utils.get_params_sing(sys.argv[1:], 'i:o:m:ta', 'i', 0)
        if not os.path.isdir(params['i']):
            raise ValueError('Input must be a directory of files.')
    except ValueError as err:
        print('Error: {0}'.format(err))
        print(('Usage: {0} -i input_dir [-o output_file] -m [hunpos_model] ' +
            '[-a]').format(sys.argv[0]))
        print('       input_dir: the directory with the input text files.')
        print('       hunpos_model: the hunpos model file.')
        print('       output_file: the conll2 output file. If omitted, the result will')
        print('                    be written to stdout.')
        print('       hunpos_model: the hunpos model file.')
        print('       -a: the output is appended to output_file, instead of overwriting it.')
        sys.exit()
    
    if 'o' in params:
        output_mode = 'a' if 'a' in params else 'w'
        out = FileWriter(params['o'], output_mode).open()
    else:
        out = StreamWriter(sys.stdout)
    
    nt = NltkTools(pos=True, stem=True, tok=True, pos_model=params.get('m'))
    for infile in (os.path.join(d, f) for d, _, fs in os.walk(params['i']) for f in fs):
        print "File " + infile
        doc = FieldedDocument(infile)
        doc.fields = {}
        for field, raw_text in read_file(infile).iteritems():
            doc.fields[field] = nt.tag_raw(raw_text)
        write_doc(doc, out)
    
    if 'o' in params:
        out.close()
