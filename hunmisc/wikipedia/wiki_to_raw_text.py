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


import sys
from optparse import OptionParser

from langtools.wikipedia.wikiparser import WikipediaParser
from langtools.utils.language_config import LanguageTools

class WikitextToRawText(WikipediaParser):
    """Parses Wikipedia markup dump to raw text."""
    def __init__(self, lt, config_file, pages_file):
        """
        @param pages_file the output file stream to which the page text is written.
        """
        WikipediaParser.__init__(self, lt, config_file)
        self.pages_f     = pages_file

    def process_tokens(self, actual_title, tokens, templates):
        """Tags and lemmatizes the tokens, then prints the result into the
        first output file."""

        # Print the tagged tokens
        self.pages_f.write(u"{0}\t{1}\n".format(
                WikipediaParser.page_separator, actual_title).encode("utf-8"))

        self.pages_f.write(u"%%#Field\tTitle\n")
        self.print_tokens([tokens[0]])

        # TODO: redirect.
        # elif starter and l.startswith("REDIRECT"):
        #   print "%%#Redirect"
        self.pages_f.write(u"%%#Field\tBody\n")
        self.print_tokens(tokens[1:])

    def print_tokens(self, tokens):
        """Prints @p tokens to the page content file."""
        for sen in tokens:
            for token in sen:
                try:
                    self.pages_f.write(token[0].encode("utf-8") + " ")
                except UnicodeError, ue:
                    print "Trying to print: "
                    for w in token:
                        if isinstance(w, unicode):
                            print w.encode('utf-8')
                        else:
                            print w
                    raise ue
            self.pages_f.write("\n")
        self.pages_f.write("\n")

if __name__ == '__main__':
    option_parser = OptionParser()
    option_parser.add_option("-l", "--language", dest="language",
            help="the Wikipedia language code. Default is en.", default="en")
    options, args = option_parser.parse_args()

    if len(args) != 3:
        print "Usage: {0} [options] config_file input_file output_file".format(__file__)
        sys.exit()

    lt = LanguageTools(args[0], options.language)
    input_file = open(args[1], "r")
    pages_file = open(args[2], "w")

    w = WikitextToRawText(lt, args[0], pages_file)
    w.process_file(input_file)

    #import cProfile
    #cProfile.run("main()")

