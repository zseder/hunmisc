"""Extracts interlanguage title correspondence information from the
interlanguage links file, an SQL dump."""

import re
from optparse import OptionParser

from langtools.wikipedia.search_disambig_redirect_paths import read_ids

_INSERT_PATTERN = re.compile(r'^(\s*INSERT INTO `langlinks` VALUES)')
_TUPLE_PATTERN  = re.compile(r"\s*[(](\d+)\s*,\s*'(.+?)'\s*,\s*'(.+?)'[)]\s*")

def extract(inter_file, id_to_title, target_lang=None):
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
                        yield (s.group(1), s.group(2), s.group(3))
                    index += len(s.group(0))
                    s = _TUPLE_PATTERN.search(line[index:])

if __name__ == '__main__':
    import sys
    option_parser = OptionParser()
    if len(sys.argv) != 3:
        sys.stderr.write("Usage: {0} interlink_file pages_file\n".format(__file__))
        sys.exit()

    for t in extract(sys.argv[1], None, 'en'):
        print "{0}\t{1}\t{2}".format(*t)
