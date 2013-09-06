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


#!/usr/bin/python
"""Splits a conll corpus into two parts, usually train and test
by walking through all the sentences and doing NO random to be uniform
(ask Gabor or Daniel why)
@ratio is an integer, and tells in how many sentences there is one
       test sentence
@set_off is an integer and "shifts" the counter
"""

import sys
def main(ratio, set_off):
    curr_sen = []
    c = 0
    for line in sys.stdin:
        if line =='\n':
            print_sen(curr_sen, c, ratio, set_off)
            curr_sen = []
        else:
            curr_sen.append(line)
            c += 1

def print_sen(sen, c, ratio, set_off):
    if (c + set_off) % ratio == 0:
        for line in sen:
            print line,
        print    
    else:
        for line in sen:
            sys.stderr.write(line)
        sys.stderr.write('\n')

if __name__=='__main__':
    main(int(sys.argv[1]), int(sys.argv[2]))
