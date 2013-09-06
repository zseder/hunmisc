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


"""Extracts interlanguage title correspondence information from the
interlanguage links file, an SQL dump."""

import re
from optparse import OptionParser

from langtools.wikipedia.search_disambig_redirect_paths import read_ids

_INSERT_PATTERN = re.compile(r'^(\s*INSERT INTO `redirect` VALUES)')
# Source id, namespace, target title (_), stuff
_TUPLE_PATTERNS = {}
_TUPLE_PATTERNS['hu'] = re.compile(r"\s*[(](\d+)\s*,\s*(\d+)\s*,\s*'(.+?)'\s*,.+?,\s*'.+?'\s*[)]\s*")
_TUPLE_PATTERNS['en'] = re.compile(r"\s*[(](\d+)\s*,\s*-?(\d+)\s*,\s*'(.+?)'\s*[)]\s*")

def extract(redirect_file, id_to_title, tuple_pattern, reverse=False):
    """
    Extracts the mapping.
    @param redirect_file the SQL dump.
    @param id_to_title a page id -> title mapping in the source language.
    @param tuple_pattern the tuple part of the insert command, language-dependent
    @param reverse if @c True, the returned map is inverted.
    @return a map of {redirect page title : target page title}.
    """
    with open(redirect_file, 'r') as infile:
        for line in infile:
            m = _INSERT_PATTERN.search(line)
            if m is not None:
                index = len(m.group(1))
                s = tuple_pattern.search(line[index:])
                while s is not None:
                    # Namespace must be 0
                    if int(s.group(2)) == 0:
                        try:
                            src_title = id_to_title[int(s.group(1))].replace('_', ' ')
                            tgt_title = s.group(3).replace('_', ' ').replace(r'\"', '"').replace(r"\'", "'")
                            if not reverse:
                                yield (src_title, tgt_title)
                            else:
                                yield (tgt_title, src_title)
                        except KeyError, ke:
                            sys.stderr.write("Unknown id {0}\n".format(s.group(1)))
                            pass
                    index += len(s.group(0))
                    s = tuple_pattern.search(line[index:])

if __name__ == '__main__':
    import sys
    option_parser = OptionParser()
    option_parser.add_option("-r", "--reverse", dest="reverse",
            action="store_true", default=False,
            help="reverse direction (page to redirect)")
    option_parser.add_option("-l", "--language", dest="language",
            help="the Wikipedia language code. Default is en.", default="en")
    options, args = option_parser.parse_args()

    if len(args) != 2:
        sys.stderr.write("Usage: {0} [options] redirect_file pages_file\n".format(__file__))
        sys.exit()

    try:
        pattern = _TUPLE_PATTERNS[options.language]
    except KeyError:
        sys.stderr.write("Language must be one of {0}!\n\n".format(
            _TUPLE_PATTERNS.keys()))
        sys.exit()

    import gc
    gc.disable()
    sys.stderr.write("Starting...\n")
    links_file  = args[0]
    id_to_title = read_ids(open(args[1], 'r'))[1]
    sys.stderr.write("Id to title read...\n")
    reverse     = options.reverse
    gc.enable()

    for i, t in enumerate(extract(links_file, id_to_title, pattern, reverse)):
        if i % 100000 == 0:
            sys.stderr.write("{0} redirects written.\n".format(i))
        print "{0}\t{1}".format(*t)
    sys.stderr.write("Done.\n")

