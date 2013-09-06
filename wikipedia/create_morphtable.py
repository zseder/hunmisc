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


"""
Runs ocamorph and creates the bloody morphtable for hundisambig.
Parameters: the configuration file, the output file and the input files.
"""
import logging

from optparse import OptionParser
from langtools.wikipedia.wikitext_to_conll import WikipediaParser
from langtools.utils.language_config import LanguageTools
from langtools.utils.huntool_wrapper import Ocamorph, OcamorphAnalyzer

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
        self.ocamorph = Ocamorph(self.lt.config['ocamorph_runnable'],
                                 self.lt.config['ocamorph_model'],
                                 self.lt.config.get('ocamorph_encoding', 'iso-8859-2'))
        self.morph_analyzer = OcamorphAnalyzer(self.ocamorph)

    def process_tokens(self, actual_title, tokens, templates):
        logging.info("TITLE " + actual_title)
        for sentence in tokens:
            for token in sentence:
                # Well, that's it for loose coupling
                self.morph_set.add(self.morph_analyzer.replace_stuff(token[0]))
#                self.morph_set.add(token[0])

    def print_tokens(self):
        sorted_words = sorted(self.morph_set)
        for i in xrange(0, len(sorted_words), 25):
            analyzed = [sen for sen in self.morph_analyzer.analyze([sorted_words[i : i + 25]])][0]
#            analyzed = list(analyzed)
#            print "ANAL", analyzed
            self.table_file.write(u"\n".join("\t".join(token) for token in analyzed).encode(self.ocamorph._encoding))
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

