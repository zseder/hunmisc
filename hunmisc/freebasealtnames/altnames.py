"""computes alternative names from input dictionaries (results from
clueweb12facc_to_mention.py)
"""

import argparse
import cPickle
import sys


def get_argparser():
    ap = argparse.ArgumentParser()
    ap.add_argument("d1", help="string to entity dict")
    ap.add_argument("d2", help="entity to string dict")
    ap.add_argument("-o", "--output", help="output. if not given: stdout",
                    default=sys.stdout)
    ap.add_argument("--min-str-entity", default=10, type=int,
                    help="filter (str, entity) pairs with less mentions")
    ap.add_argument("--min-str-ratio", default=0.005, type=float,
                    help="filter entities for a mention when this entity " +
                    "gets less than this ratio")
    ap.add_argument("--min-str-sum", default=100, type=int,
                    help="filter mentions with less total count")
    ap.add_argument("--min-entity-sum", default=1000, type=int,
                    help="filter entities with less total count")
    ap.add_argument("--min-fraction", default=0.1, type=float,
                    help="filter (str, entity) pairs if they cover less " +
                    "than this ratio for a given entity")
    ap.add_argument("--lower", help="lowercasing. needs utf-8 input",
                    action="store_true")
    return ap


class AltNames(object):
    def __init__(self, d1, d2, min_str_sum, min_str_entity, min_str_ratio,
                 min_entity_sum, min_fraction, lower):
        self.d1 = d1
        self.d2 = d2
        self.mss = min_str_sum
        self.mse = min_str_entity
        self.msr = min_str_ratio
        self.mes = min_entity_sum
        self.mf = min_fraction
        if lower:
            self.d1 = self.lower_dict(d1, 0)
            self.d2 = self.lower_dict(d2, 1)
        else:
            self.d1, self.d2 = d1, d2

    def lower_dict(self, d, whichkey):
        newd = {}
        for k1old in d:
            if whichkey == 0:
                k1 = k1old.lower()
            else:
                k1 = k1old

            if k1 not in newd:
                newd[k1] = {}

            for k2old in d[k1old]:
                if whichkey == 1:
                    k2 = k2old.lower()
                else:
                    k2 = k2old
                newd[k1][k2] = newd[k1].get(k2, 0) + d[k1old][k2old]
        return newd

    def compute_neededs(self):
        self.needed_mentions = set(m for m in self.d1.iterkeys()
                                   if sum(self.d1[m].itervalues()) >= self.mss)
        self.needed_entities = dict((e, sum(self.d2[e].itervalues())) for e in
                                    self.d2.iterkeys() if
                                    sum(self.d2[e].itervalues()) >= self.mes)

    def get_altnames(self):
        self.compute_neededs()
        d1 = self.d1
        d = {}
        for m in d1:
            if m not in self.needed_mentions:
                continue
            s = float(sum(d1[m].itervalues()))
            best_e = max(d1[m].iteritems(), key=lambda x: x[1])
            e, c = best_e
            if e not in self.needed_entities:
                continue
            if c < self.mse:
                continue
            if c / s < self.msr:
                continue
            if float(c) / self.needed_entities[e] < self.mf:
                continue

            if e not in d:
                d[e] = []
            d[e].append(m)
        return d


def main():
    a = get_argparser().parse_args()
    d1 = cPickle.load(open(a.d1))
    d2 = cPickle.load(open(a.d2))
    an = AltNames(d1, d2, a.min_str_sum, a.min_str_entity, a.min_str_ratio,
                  a.min_entity_sum, a.min_fraction, a.lower)
    altnames = an.get_altnames()
    ostream = (open(a.output, "w") if type(a.output) == str else a.output)
    for e in altnames:
        ostream.write(u"{0}\t{1}\n".format(e,
            "\t".join(altnames[e])).encode("utf-8"))


if __name__ == "__main__":
    main()
