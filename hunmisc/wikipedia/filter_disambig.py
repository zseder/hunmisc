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


"""Filters disambiguation pages from Wikipedia documents."""
import sys
from optparse import OptionParser

from langtools.io.conll2.conll_reader import ConllReader
from langtools.io.conll2.conll_iter import ConllIter
from langtools.io.conll2.fielded_document_filter import *
from langtools.utils.cascading_config import CascadingConfigParser

class TitleDisambigFilter(FieldedDocumentFilter):
    """Filters disambiguation documents by title."""
    def __init__(self, patterns):
        """
        @param patterns the string patterns that hint at the page being a
                        disambiguation page.
        """
        self.patterns = patterns

    def accept(self, document):
        for pattern in self.patterns:
            if pattern in document.title:
                return False
        return True

if __name__ == '__main__':
    option_parser = OptionParser()
    option_parser.add_option("-l", "--language", dest="language",
            help="the Wikipedia language code. Default is en.", default="en")
    options, args = option_parser.parse_args()

    config_parser = CascadingConfigParser(args[0])
    config = dict(config_parser.items(options.language + '-wikimedia'))

    # Filters
    multi_filter = MultiFilter()
    templates = config.get('disambig_templates', '')
    if len(templates) > 0:
        template_filter = TemplateFilter([t.strip().decode('utf-8') for t in templates.split(',')])
        multi_filter.add(template_filter)
    titles = config.get('disambig_title', '')
    if len(titles) > 0:
        titles_filter = TitleDisambigFilter([t.strip().decode('utf-8') for t in titles.split(',')])
        multi_filter.add(titles_filter)

    reader = ConllReader()
    it = ConllIter(reader, 'utf-8')
    it.read(args[1:])
    for page in it:
        if multi_filter.accept(page):
            sys.stdout.write(unicode(page).encode('utf-8'))
        else:
            sys.stderr.write("Discarding " + page.title.encode('utf-8') + "\n")
            sys.stderr.flush()
    sys.stdout.flush()

