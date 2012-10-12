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
