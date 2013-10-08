import logging
import cPickle

import dawg

import cache

def intdict_to_list(d):
    return [k for k, v in sorted(d.iteritems(), key=lambda x: x[1])]

class EntityDB(object):
    def __init__(self, sources=None):
        self.__init_caches(sources)
        self.d = {}
        self.values = []
        self.to_keep = None

    def add_to_keep_list(self, to_keep):
        self.to_keep = set(to_keep)

    def __init_caches(self, sources):
        self.caches = {}
        
        if sources is None:
            sources = []

        for source in sources:
            self.caches[source] = cache.init_cache(source)

    def fill_dict(self, pairs, src):
        for pair in pairs:
            key, value = pair
            key = key.lower()
            if self.to_keep is not None:
                if key not in self.to_keep:
                    continue

            if not key in self.d:
                self.d[key] = len(self.values)
                self.values.append(set())
            compact_value = self.caches[src].store(value)
            self.values[self.d[key]].add((src, compact_value))

    def compactize_values(self):
        self.values = [frozenset(s) for s in self.values]

        first = {self.values[0]: 0}
        shifts = [0]
        for i in xrange(1, len(self.values)):
            s = self.values[i]
            if s in first:
                shifts.append(shifts[-1] - 1)
            else:
                first[s] = i
                shifts.append(shifts[-1])

        to_del = set()
        for w, i in self.d.iteritems():
            s = self.values[i]
            self.d[w] = first[s] + shifts[first[s]]
            if first[s] != i:
                to_del.add(i)

        self.values = [self.values[vi] for vi in xrange(len(self.values))
                      if vi not in to_del]

    def compactize(self):
        for cache in self.caches.itervalues():
            cache.finalize()

        logging.info("Compactizing values...")
        self.compactize_values()

        logging.info("Creating dawg...")
        self.dawg = dawg.IntCompletionDAWG(self.d)
        del self.d
        logging.info("compactizing done.")

    def dump(self, pickle_f, dawg_fb):
        self.to_keep = None
        self.compactize()
        self.dawg.write(dawg_fb)
        del self.dawg
        cPickle.dump(self, pickle_f, 2)

    @staticmethod
    def load(pickle_f, dawg_fn):
        entity_db = cPickle.load(pickle_f)
        entity_db.dawg = dawg.IntCompletionDAWG()
        entity_db.dawg.load(dawg_fn)
        return entity_db

    def get_type(self, name):
        if name not in self.dawg:
            return None
        try:
            value_index = self.dawg[name]
            res = []
            values = self.values[value_index]
            for src_lang_type_i in values:
                src_i, lang_type_i = self.src_lang_type_cache[src_lang_type_i]

                src = self.src_cache[src_i]
                lang_i, type_i = self.lang_type_cache[lang_type_i]
                lang = self.lang_cache[lang_i]
                type_ = self.type_cache[type_i]
                res.append((src, lang, type_))
            return res
        except IndexError:
            logging.error("There is an error in compact EntityDB")
            logging.exception("IndexError")
         
