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

_INSERT_PATTERN = re.compile(r'^(\s*INSERT INTO `langlinks` VALUES)')
_TUPLE_PATTERN  = re.compile(r"\s*[(](\d+)\s*,\s*'(.+?)'\s*,\s*'(.+?)'[)]\s*")

def extract(inter_file, id_to_title, target_lang=None, reverse=False):
    """
    Extracts the mapping.
    @param inter_file the SQL dump.
    @param id_to_title a page id -> title mapping in the source language.
    @param target_lang the language code of the target language.
    @return a map of {source language title: target language title}.
    """
    with open(inter_file, 'r') as infile:
        for line in infile:
            m = _INSERT_PATTERN.search(line)
            if m is not None:
                index = len(m.group(1))
                s = _TUPLE_PATTERN.search(line[index:])
                while s is not None:
                    if target_lang is None or s.group(2) == target_lang:
                        try:
                            src_title = id_to_title[int(s.group(1))].replace('_', ' ')
                            tgt_title = s.group(3).replace(r'\"', '"').replace(r"\'", "'")
                            if not reverse:
                                yield (src_title, tgt_title)
                            else:
                                yield (tgt_title, src_title)
                        except KeyError, ke:
                            sys.stderr.write("Unknown id {0}\n".format(s.group(1)))
                            pass
                    index += len(s.group(0))
                    s = _TUPLE_PATTERN.search(line[index:])

if __name__ == '__main__':
    import sys
    option_parser = OptionParser()
    option_parser.add_option("-l", "--language", dest="language",
            help="the target language code. Default is None (all)", default=None)
    option_parser.add_option("-r", "--reverse", dest="reverse",
            action="store_true", default=False,
            help="reverse direction (target to source language)")
    options, args = option_parser.parse_args()

    if len(args) != 2:
        sys.stderr.write("Usage: {0} [options] interlink_file pages_file\n".format(__file__))
        sys.exit()

    import gc
    gc.disable()
    links_file  = args[0]
    id_to_title = read_ids(open(args[1], 'r'))[1]
    language    = options.language
    reverse     = options.reverse
    gc.enable()

    for t in extract(links_file, id_to_title, language, reverse):
        print "{0}\t{1}".format(*t)

