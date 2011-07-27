"""Contains stream and file handler classes that accept unicode tokens."""

import os
import os.path

def ensure_dir(dir_name):
    """Checks if C{dir_name} directory exists, and if not, creates it.
    @return C{True} on success; C{False} otherwise."""
    if not os.path.isdir(dir_name):
        if os.path.exists(dir_name):
            return False
        else:
            os.mkdir(dir_name)
    return True

class StreamHandler(object):
    def __init__(self, stream, encoding='utf-8'):
        self.stream = stream
        self.encoding = encoding
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
    
    def __del__(self):
        self.close()
    
    def close(self):
        """Closes the stream."""
        if self.stream:
            self.stream.close()
            self.stream = None

class StreamReader(StreamHandler):
    def __init__(self, stream, encoding='utf-8', replace=False):
        StreamHandler.__init__(self, stream, encoding)
        self.uni_errors = 'replace' if replace else 'ignore'
    
    def __iter__(self):
        """Iterates through the lines in the stream."""
        for line in self.stream:
            yield line.decode(self.encoding, self.uni_errors)
        return
    
class StreamWriter(StreamHandler):
    def __init__(self, stream, encoding='utf-8'):
        StreamHandler.__init__(self, stream, encoding)
    
    def write(self, text):
        """Writes C{text} to the file in the correct encoding."""
        self.stream.write(text.encode(self.encoding))
    
class FileHandler(object):
    def __init__(self, file_name, file_mode='r'):
        """Guess."""
        self.file_name = file_name
        self.file_mode = file_mode
    
    def open(self):
        """Opens the file."""
#        self.stream = codecs.getreader(self.encoding)(open(self.file_name, 'r'))
        self.stream = open(self.file_name, self.file_mode)
        return self
    
class FileReader(StreamReader, FileHandler):
    def __init__(self, file_name, encoding='utf-8', replace=False):
        """Guess."""
        StreamReader.__init__(self, None, encoding, replace)
        FileHandler.__init__(self, file_name, 'r')
        
class FileWriter(StreamWriter, FileHandler):
    def __init__(self, file_name, file_mode, encoding='utf-8'):
        """Guess."""
        if file_mode not in ['a', 'w', 'ab', 'wb', 'r+', 'r+b']:
            raise ArgumentError
        StreamWriter.__init__(self, None, encoding)
        FileHandler.__init__(self, file_name, file_mode)
        