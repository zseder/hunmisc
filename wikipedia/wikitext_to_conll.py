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


"""Parameters: the configuration file, the input file, the two outputs: the
pages and the templates files."""
# TODO: ' to separate token (currently it is not removed from the beginning of
#       words).

import sys
import logging
from optparse import OptionParser

from langtools.wikipedia.wikiparser import WikipediaParser
from langtools.utils.language_config import LanguageTools

class WikitextToConll(WikipediaParser):
    def __init__(self, lt, config_file, pages_file, templates_file):
        """
        @param pages_file the output file stream to which the page text is written.
        @param templates_file templates are written to this file stream.
        """
        WikipediaParser.__init__(self, lt, config_file)
        self.pages_f     = pages_file
        self.templates_f = templates_file

    def process_tokens(self, actual_title, tokens, templates):
        """Tags and lemmatizes the tokens, then prints the result into the
        first output file."""
        logging.debug("TITLE " + actual_title)
        # POS tag and lemmatize the data
        self.lt.pos_tag(tokens)
        self.lt.lemmatize(tokens)

        # Print the tagged tokens
        self.pages_f.write(u"{0}\t{1}\n".format(
                WikipediaParser.page_separator, actual_title).encode("utf-8"))

        self.pages_f.write(u"%%#Field\tTitle\n")
        self.print_tokens([tokens[0]])

        # TODO: redirect.
        # elif starter and l.startswith("REDIRECT"):
        #   print "%%#Redirect"
        if len(templates) > 0:
            self.pages_f.write(u"%%#Templates\t{0}\n".format(
                    u",".join((t.strip().replace("\n", "") for t in templates))).encode("utf-8"))
        self.pages_f.write(u"%%#Field\tBody\n")
        self.print_tokens(tokens[1:])

    def print_tokens(self, tokens):
        """Prints @p tokens to the page content file."""
        for sen in tokens:
            for t in sen:
                try:
                    self.pages_f.write(u"\t".join(t).encode("utf-8") + "\n")
                except UnicodeError, ue:
                    print "Trying to print: "
                    for w in t:
                        if isinstance(w, unicode):
                            print w.encode('utf-8')
                        else:
                            print w
                    raise ue
            self.pages_f.write("\n")

    def process_templates(self, actual_title, s):
        """Prints the templates into the second output file."""
        from mwlib.expander import get_templates

        self.templates_f.write(u"{0} {1}\n".format(
                WikipediaParser.page_separator, actual_title).encode("utf-8"))
        if not WikitextToConll.write_templates_into_f(s, self.templates_f):
            sys.stderr.write(u"Problems with templates and mwparser: {0}\n".format(
                             actual_title).encode("utf-8"))
        return get_templates(s)

    @staticmethod
    def write_templates_into_f(raw, f):
        """Extracts the templates from the raw text and writes them to the file @p f."""
        from mwlib.templ.misc import DictDB
        from mwlib.expander import get_template_args
        from mwlib.templ.evaluate import Expander
        from mwlib.templ.parser import parse
        from mwlib.templ.nodes import Template
        
        e=Expander('', wikidb=DictDB())  
        todo = [parse(raw, replace_tags=e.replace_tags)]
        result = True
        while todo:
            n = todo.pop()
            if isinstance(n, basestring):
                continue

            if isinstance(n, Template) and isinstance(n[0], basestring):
                d = get_template_args(n, e)
                f.write(u"Template\t{0}\n".format(unicode(n[0]).strip().replace("\n", "")).encode("utf-8"))
                for i in range(len(d)):
                    try:
                        f.write(unicode(d[i]).encode("utf-8") + "\n")
                    except TypeError:
                        result = False
                    except AttributeError:
                        # handling some mwlib bug. it raises this exception somehow
                        result = False
                f.write("\n")
            todo.extend(n)
        return result

    def close(self):
        if self.pages_f is not None:
            self.pages_f.close()
            self.templates_f.close()
            self.pages_f = None
            self.templates_f = None

    def __del__(self):
        #WikipediaParser.__del__(self)  # Doesn't work
        self.close()

if __name__ == '__main__':
    option_parser = OptionParser()
    option_parser.add_option("-l", "--language", dest="language",
            help="the Wikipedia language code. Default is en.", default="en")
    options, args = option_parser.parse_args()

    lt = LanguageTools(args[0], options.language)
    input_file = open(args[1], "r")
    pages_file = open(args[2], "w")
    templates_file = open(args[3], "w")

    w = WikitextToConll(lt, args[0], pages_file, templates_file)
    w.process_file(input_file)

    #import cProfile
    #cProfile.run("main()")

