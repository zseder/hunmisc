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


from subprocess import Popen, PIPE

class AbstractSubprocessClass(object):
    """
    Simple abstract wrapper class for commands that need to be
    called with Popen and communicate with them
    """
    def __init__(self, runnable, encoding="utf-8", options=None):
        self._runnable = runnable
        self._encoding = encoding
        self._closed = True
        if isinstance(options, list):
            self.options = options
        elif options is None:
            self.options = []
        else:
            raise ValueError('AbstractSubprocessClass: options must be a list')

    def start(self):
        #print self._runnable
        #print self.options
        self._process = Popen([self._runnable] + self.options,
                              stdin=PIPE, stdout=PIPE, stderr=PIPE)
        self._closed = False

    def stop(self):
        if not self._closed:
            # HACK: communicate() sometimes blocks here
            self._process.terminate()
        self._closed = True

    def __exit__(self, exc_type, exc_value, traceback):
        if not self._closed:
            self.stop()

    def __del__(self):
        if not self._closed:
            self.stop()
