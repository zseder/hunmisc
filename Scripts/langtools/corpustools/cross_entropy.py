import sys
import math
import re
"""This script calculates cross-entropy between two frequency lists. Zero frequencies, as well as words that are only present in one of the two files are discarded. Probability mass discarded in data1 is printed.
Usage:
    python entropy.py file1 file2 data_field freq_field
"""
def cross_entropy(q, p):
    qsum = float(sum(q.itervalues()))
    psum = float(sum(p.itervalues()))
    filtered_p = dict([(word, count) for (word, count) in p.iteritems()
                        if word in q and q[word] != 0])
    filtered_p_sum = float(sum(filtered_p.itervalues()))
    filtered_p_norm = dict([(w, count / filtered_p_sum) 
                            for w, count in filtered_p.iteritems()])
    qnorm = dict([(w, freq/qsum) for w, freq in q.iteritems()])
    pnorm = dict([(w, freq/psum) for w, freq in p.iteritems()])

    not_covered = 1.0 - sum([prob for (word, prob) in pnorm.iteritems()
                        if word in qnorm and qnorm[word] != 0])

    ce = 0
    for word, p_prob in filtered_p_norm.iteritems():
        q_prob = qnorm[word]
        ce += p_prob*math.log(p_prob/q_prob, 2)

    return ce, not_covered

if __name__ == '__main__':

    q = dict([(word, float(freq))
               for (word, freq) in [re.split("\s", line.rstrip())
                                    for line in file(sys.argv[1])]])
    p = dict([(word, float(freq))
               for (word, freq) in [re.split("\s", line.rstrip())
                                    for line in file(sys.argv[2])]])
    ce, uncovered = cross_entropy(q, p)
    print uncovered, ce
