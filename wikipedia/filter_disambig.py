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

