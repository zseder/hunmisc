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
Contains a wrapper for the pexpect library, and some class that were taken
from huntools.py and re-based on AbstractPexpectClass instead of 
AbstractSubprocessClass.

@warning These classes are here for reference, they are too slow to be of any
actual use.
"""

import pexpect

class AbstractPexpectClass:
    """
    Wraps the pexpect library. Use this instead of subprocess_wrapper.py if you
    want to avoid deadlocks with interactive programs.
    """
    def __init__(self, runnable, encoding='utf-8'):
        self._runnable = runnable
        self._encoding = encoding
        self._closed   = True
        self._spawned  = None
        self.options   = []

    def start(self):
        """Starts the runnable. Echo is set to @c False."""
        if self._closed:
            self._spawned = pexpect.spawn(self._runnable, self.options)
            self._spawned.setecho(False)
            self._closed = False

    def stop(self):
        """Stops the runnable."""
        if not self._closed:
            self._spawned.close()
            self._closed = True

    def __enter__(self):
        """Calls start() if we are not running already."""
        if self._closed:
            self.start()

    def __exit__(self, exc_type, exc_value, traceback):
        """Calls stop() if we are running."""
        if not self._closed:
            self.stop()

    def __del__(self):
        """Calls stop() if we are still running."""
        if not self._closed:
            self.stop()

class LineByLineTagger(AbstractPexpectClass):
    def __init__(self, runnable, encoding):
        AbstractPexpectClass.__init__(self, runnable, encoding)

    def send_line(self, line):
        self._spawned.sendline(line.encode(self._encoding, 'xmlcharrefreplace') + "\n")

    def recv_line(self):
        return self._spawned.readline().strip().decode(self._encoding)

    def send_and_recv_lines(self, lines):
        for line in lines:
            self.send_line(line)
            yield self.recv_line()

    def tag(self, lines):
        if self._closed:
            self.start()
        return self.send_and_recv_lines(lines)

class SentenceTagger(AbstractPexpectClass):
    """
    Tags sentence by sentence in conll format
    ie. one token per line, attributes separated by tab (or @sep),
    empty line on sentence end
    """
    def __init__(self, runnable, encoding, tag_index=-1, sep="\t", isep="\t", osep="\t"):
        AbstractPexpectClass.__init__(self, runnable, encoding)
        self._tag_index = tag_index
        self.sep = sep
        self.isep = sep
        self.osep = sep
        self.isep = isep
        self.osep = osep

    def send(self, tokens):
        """
        send tokens to _process.stdin after encoding
        excepts only one sentence
        """
        self.tuple_mode = isinstance(tokens[0], tuple)
        for token in tokens:
            # differentiate between already tagged and raw tokens
            if self.tuple_mode:
                token_str = self.isep.join(token)
            else:
                token_str = token
            token_to_send = token_str.encode(self._encoding, 'xmlcharrefreplace')
            from datetime import datetime
#            print "WRITING", datetime.now().time(), token_str.encode('utf-8')
#            sys.stdout.flush()
            self._spawned.sendline(token_to_send)
        self._spawned.sendline()

    def recv_and_append(self, tokens):
        tagged_tokens = []
        for token in tokens:
            line = self._spawned.readline()
            decoded = line.decode(self._encoding).strip()
            from datetime import datetime
#            print "LINE:", datetime.now().time(), token.encode('utf-8') + " >" + decoded.encode('utf-8') + "<"
#            sys.stdout.flush()
            if len(decoded) == 0:
                continue
            tagged = decoded.split(self.osep)
#            print "TOKEN: " + unicode(token).encode('utf-8')
#            print "TAGGED: " + unicode(tagged).encode('utf-8')
            tag = tagged[self._tag_index]
            if self.tuple_mode:
                tagged_tokens.append(token + (tag,))
            else:
                tagged_tokens.append((token, tag))

        # is it last reading necessary?
        self._spawned.readline()

        return tagged_tokens
    
    def tag_sentence(self, tokens):
        if self._closed:
            self.start()

        self.send(tokens)
        result = self.recv_and_append(tokens)
        return result

    def tag_sentences(self, sentences):
        for sentence in sentences:
            yield self.tag_sentence(sentence)

class Hundisambig2(SentenceTagger2):
    def __init__(self, runnable, model, morphtable=None, encoding="LATIN2"):
        SentenceTagger2.__init__(self, runnable, encoding, 1)
        self._model = model
        self._morphtable = morphtable
        self.__set_default_options()

    def __set_default_options(self):
        o = []
        o += ["--morphtable", self._morphtable]
        o += ["--tagger-model", self._model]
        o += ["--decompounding", "no"]  # Let's not bother with decompounding

        self.options = o
    
    def set_morphtable(self, mt):
        if self._closed:
            print "SETTING morphtable"
            import sys
            sys.stdout.flush()
            self._morphtable = mt
        else:
            raise Exception("morphtable can be changed only while not running")
        self.__set_default_options()

