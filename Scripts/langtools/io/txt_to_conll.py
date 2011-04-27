"""Converts a text file (optionally with a title) to the conll2 format."""

import os.path
from langtools.nltk.nltktools import NltkTools
from langtools.utils import cmd_utils
from langtools.utils.file_utils import *
from langtools.io.conll2.conll_iter import WikiPage

# TODO: rename WikiPage to ConllDocument
# TODO: encoding!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

def read_stream(ins, title=False):
    """Reads a stream. Returns a {field:raw text} map, with a Body field. If title
    is true, a Title field will be added too."""
    fields = {}
    if title:
        for line in ins:
            line = line.strip()
            if len(line) > 0:
                fields['Title'] = line
                break
    fields['Body'] = ' '.join(line.strip() for line in ins)
    return fields

def read_file(infile, title=False):
    """Reads a file. Returns a {field:raw text} map, with a Body field. If title
    is true, a Title field will be added too."""
    return read_stream(FileReader(infile).open(), title)

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
            '[-t] [-a]').format(sys.argv[0]))
        print('       input_dir: the directory with the input text files.')
        print('       hunpos_model: the hunpos model file.')
        print('       output_file: the conll2 output file. If omitted, the result will')
        print('                    be written to stdout.')
        print('       hunpos_model: the hunpos model file.')
        print('       -t: If specified, the first non-empty line of the the text files are')
        print('           considered to be titles, and will be processed accordingly.')
        print('       -a: the output is appended to output_file, instead of overwriting it.')
        sys.exit()
    
    if 'o' in params:
        output_mode = 'a' if 'a' in params else 'w'
        out = FileWriter(params['o'], output_mode).open()
    else:
        out = StreamWriter(sys.stdout)
    
    nt = NltkTools(pos=True, stem=True, tok=True, pos_model=params.get('m'))
    for infile in filter(os.path.isfile, [os.path.join(params['i'], infile)
                                          for infile in os.listdir(params['i'])]):
        doc = WikiPage(infile)
        doc.fields = {}
        for field, raw_text in read_file(infile, True).iteritems():
            doc.fields[field] = nt.tag_raw(raw_text)
        write_doc(doc, out)
    
    if 'o' in params:
        out.close()
