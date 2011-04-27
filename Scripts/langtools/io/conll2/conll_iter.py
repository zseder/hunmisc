"""Wraps the conll reader in an iterable interface."""
from threading import Thread
import sys
if sys.version_info[0] >= 3:
    from queue import Queue
    from conll_reader3 import *
else:
    from Queue import Queue
    from conll_reader import *

class FieldedDocument(object):
    """Represents a wiki page. It has the following fields:
    - title: the page title;
    - fields: a set of {field name -> word list} mappings, where a word entry
              consists of all its attributes;
    - redirect: a boolean telling if the page is a redirect page;
    - templates: a list of the templates."""
    def __init__(self, title):
        self.title = title
        self.fields = {}
        self.redirect = False
        self.templates = None

class ConllDocumentConverter(DefaultConllCallback):
    """A C{ConllCallback} that puts C{FieldedDocument} objects in a queue."""
    def __init__(self, queue):
        self.queue = queue
        self.page = FieldedDocument(None)
        self.words = []
    
    def documentStart(self, title):
        """Called when the document header C{##%PAGE} is met.
        @param title: the title of the document."""
        self.page = FieldedDocument(title)
    
    def templates(self, templates):
        """Notifies the callback of the templates present in the document.
        @param templates: a list of the templates defined."""
        self.page.templates = templates

    def redirect(self):
        """Notifies the callback that this page is a redirect."""
        self.page.redirect = True
    
    def fieldStart(self, field):
        """Signals that start of a field.
        @param field: the name of the field."""
        DefaultConllCallback.fieldStart(self, field)
        self.words = []
    
    def word(self, attributes):
        """Called for each word (self, and punctuation mark as well).
        @param attributes: the attributes that belong to the current word."""
        self.words.append(attributes)
    
    def sentenceEnd(self):
        """Signals the end of the current sentence."""
        self.words.append([])
    
    def fieldEnd(self):
        """Signals the end of the current field."""
        if self.cc_field is not None:
            self.page.fields[self.cc_field] = self.words
        DefaultConllCallback.fieldEnd(self)
    
    def documentEnd(self):
        """Signals that the current document has been fully read."""
        self.queue.put(self.page, True)

class ConllIter(object):
    """Provides an iterable interface to C{ConllReader} via
    C{ConllDocumentConverter}."""
    EOF = None
    """The item put into the queue once all records have been read."""
    
    def __init__(self, reader, charset='utf-8'):
        """@param reader a C{ConllReader} object. A C{ConllDocumentConverter}
        callback is added to it; otherwise it is not abused."""
        self.reader = reader
        self.queue = Queue(16)
        self.callback = ConllDocumentConverter(self.queue)
        self.reader.addCallback(self.callback)
        self.charset = charset
    
    def read(self, files):
        """Reads the files in a separate thread."""
        rt = ConllIter.ReaderThread(self, files)
        rt.start()
    
    def __iter__(self):
        while True:
            item = self.queue.get(True)
            if item != ConllIter.EOF:
                yield item
            else:
                return
    
    class ReaderThread(Thread):
        """Sends C{files} to C{reader}."""
        def __init__(self, parent, files):
            Thread.__init__(self)
            self.parent = parent
            self.files = files
            
        def run(self):
            for input_file in self.files:
                self.parent.reader.read(input_file, self.parent.charset)
            self.parent.queue.put(ConllIter.EOF, True)
    
if __name__ == '__main__':
    import sys
    queue = Queue(16)
#    reader = ConllReader([ConllDocumentConverter(queue)])
#    for input_file in sys.argv[1:]:
#        reader.read(input_file, 'utf-8')
#    while not queue.empty():
#        page = queue.get()
#        print u'{0}({1}): {2}'.format(page.title, page.redirect, page.templates)
        
    reader = ConllReader()
    it = ConllIter(reader, 'utf-8')
    it.read(sys.argv[1:])
    for page in it:
        print page.title
