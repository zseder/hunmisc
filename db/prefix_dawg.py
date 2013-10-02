from collections import defaultdict

import dawg
import marisa_trie

class PrefixDawg(object):
    def __init__(self, compdawg):
        self.create_from_other(compdawg)

    def create_from_other(self, compdawg):
        d = defaultdict(set)
        for full in compdawg.keys():
            spl = full.split(" ")
            for length in xrange(len(spl), 0, -1):
                s = " ".join(spl[:length])
                d[s].add(full)
        d = dict([(k, v.pop()) for k, v in d.iteritems() if len(v) == 1])

        self.trie = marisa_trie.BytesTrie(((k, v.encode("utf-8"))
                                    for k, v in d.iteritems()))
        self.dawg = dawg.BytesDAWG(((k, v.encode("utf-8"))
                                    for k, v in d.iteritems()))


