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


"""This script counts entropy for characters in a corpus.
usage:
    python entropy.py corpus [data_field freq_field [split_char]]
    mandatory:
    @corpus: input file

    optional
    @data_field: integer, where the words are in the input. Default=0
    @freq_field: integer, where the (relative) frequencies are int the input,
                 Default=1
    @split_char: where the characters are splitted, useful for morpheme entropy
"""

import sys
import math
from collections import defaultdict

def normalize_dict(d):
    sum_ = float(sum(d.itervalues()))
    return dict([(k, v / sum_) for k, v in d.iteritems()])

def read_corp(f, data_field, freq_field):
    corp = {}
    for l in f:
        le = l.split("\t")
        try:
            word = le[data_field]
            freq = float(le[freq_field])
        except IndexError:
            continue
        corp[word] = freq
    corp = normalize_dict(corp)
    return corp

def char_dist(corp, splitter=None):
    dist = defaultdict(float)
    for w in corp:
        chars = (w.split(splitter) if splitter is not None else w)
        for char in chars:
            dist[char] += corp[w]
    dist = normalize_dict(dist)
    return dist

def entropy(dist):
    return sum([-prob * math.log(prob, 2) for _, prob in dist.iteritems()
               if prob > 0.0])

def main():
    inp_filename = sys.argv[1]
    data_field = 0
    freq_field = 1
    split_char = None
    if len(sys.argv) > 3:
        data_field = int(sys.argv[2])
        freq_field = int(sys.argv[3])
    if len(sys.argv) > 4:
        split_char = sys.argv[4]

    corp = read_corp(open(inp_filename), data_field, freq_field)
    dist = char_dist(corp, split_char)
    ent = entropy(dist)
    print ent

if __name__ == "__main__":
    main()
