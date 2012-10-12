"""
Runs ocamorph and creates the bloody morphtable for hundisambig.
Parameters: the configuration file, the output file and the input files.
"""
import logging

from optparse import OptionParser
from langtools.wikipedia.wikitext_to_conll import WikipediaParser
from langtools.utils.language_config import LanguageTools

class WikitextToMorphTable(WikipediaParser):
    """
    Parses Wikipedia files and creates a morphtable from them.
    """
    def __init__(self, lt, config_file, table_file):
        """
        @param table_file an open output stream.
        """
        WikipediaParser.__init__(self, lt, config_file)
        self.table_file = table_file
        self.morph_set = set()

    def process_tokens(self, actual_title, tokens, templates):
        logging.info("TITLE " + actual_title)
        for sentence in tokens:
            for token in sentence:
                # Well, that's it for loose coupling
                self.morph_set.add(self.lt.pos_tagger.morph_analyzer.replace_stuff(token[0]))

    def print_tokens(self):
        sorted_words = sorted(self.morph_set)
        for i in xrange(0, len(sorted_words), 25):
            analyzed = self.lt.pos_tagger.morph_analyzer._ocamorph.tag(sorted_words[i : i + 25])
#            analyzed = self.lt.pos_tagger.pos_tag(sorted_words[i : i + 25])
            self.table_file.write(u"\n".join("\t".join(token) for token in analyzed).encode(self.lt.pos_tagger.ocamorph._encoding))
            self.table_file.write("\n")
        self.table_file.flush()

    def close(self):
        if self.table_file is not None:
            self.table_file.close()
            self.table_file = None

    def __del__(self):
        self.close()

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-l", "--language", dest="language",
                      help="the Wikipedia language code. Default is en.", default="en")
    options, args = parser.parse_args()

    lt = LanguageTools(args[0], options.language)
    output = file(args[1], 'w')

    w = WikitextToMorphTable(lt, args[0], output)
    for input_file in args[2:]:
        w.process_file(file(input_file, 'r'))
    w.print_tokens()

