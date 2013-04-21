import sys
import math
"""This script calculates cross-entropy between two frequency lists. Zero frequencies, as well as words that are only present in one of the two files are discarded.
Usage:
    python entropy.py file1 file2 data_field freq_field
"""
def main(s1, s2, w_field, f_field):
    freqs1 = dict([(l[w_field], int(l[f_field]))
                   for l in [line.strip().split() for line in s1]
                   if int(l[f_field])>0])
    freqs2 = dict([(l[w_field], int(l[f_field]))
                   for l in [line.strip().split() for line in s2]
                   if l[w_field] in freqs1 and int(l[f_field])>0])

    freqs1 = dict([(word, int(freq)) for (word, freq) in freqs1.iteritems()
                   if word in freqs2])
    sys.stderr.write('kept {0} words\n'.format(len(freqs1)))
    total1 = float(sum(freqs1.values()))
    total2 = float(sum(freqs2.values()))
    ce = 0
    for word, f1 in freqs1.iteritems():
        p1 = f1/total1
        p2 = freqs2[word]/total2
        ce += p1*math.log(p1/p2, 2)

    return ce

if __name__ == '__main__':
    print main(file(sys.argv[1]), file(sys.argv[2]),
               int(sys.argv[3]), int(sys.argv[4]))
