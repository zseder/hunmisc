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


"""Contains stream and file handler classes that accept unicode tokens."""
## TODO: clean this up; if we have StreamHandlers, maybe we do not need this
##       file, as we have to encode/decode anyway.


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
    
    def __del__(self):
        self.close()

    def close(self):
        """Closes the stream."""
        if self.stream:
            self.stream.close()
            self.stream = None

class StreamReader(StreamHandler):
    def __init__(self, stream, encoding='utf-8'):
        StreamHandler.__init__(self, stream, encoding)
    
    def __iter__(self):
        """Iterates through the lines in the stream."""
        for line in self.stream:
            yield line.decode(self.encoding)
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
        self.stream = open(self.file_name, self.file_mode, encoding = self.encoding)
        return self
    
class FileReader(StreamReader, FileHandler):
    def __init__(self, file_name, encoding='utf-8'):
        """Guess."""
        StreamReader.__init__(self, None, encoding)
        FileHandler.__init__(self, file_name, 'r')
        
class FileWriter(StreamWriter, FileHandler):
    def __init__(self, file_name, encoding='utf-8'):
        """Guess."""
        StreamWriter.__init__(self, file_name, encoding)
        FileHandler.__init__(self, file_name, 'w')

class FileReader(FileStreamHandler):
    def __init__(self, file_name, encoding = 'utf-8'):
        """Guess."""
        FileStreamHandler.__init__(self, file_name, encoding)
        
    def open(self):
        """Opens the file for reading."""
        self.stream = open(self.file_name, 'r', encoding = self.encoding)
        return self
    
    def __iter__(self):
        """Iterates through the lines in the file."""
        return self.stream.__iter__()
    
class FileWriter(FileStreamHandler):
    def __init__(self, file_name, encoding = 'utf-8'):
        """Guess."""
        FileStreamHandler.__init__(self, file_name, encoding)
        
    def open(self):
        """Opens the file for writing."""
        self.stream = open(self.file_name, 'w', encoding = self.encoding)
        return self
    
    def write(self, text):
        """Writes C{text} to the file in the correct encoding."""
        self.stream.write(text)

