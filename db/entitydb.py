import logging
import cPickle

import dawg

def intdict_to_list(d):
    return [k for k, v in sorted(d.iteritems(), key=lambda x: x[1])]

class EntityDB(object):
    def __init__(self):
        self.__init_caches()
        self.d = {}
        self.values = []

    def __init_caches(self):
        # "freebase" -> 0
        self.src_cache = {}

        # "Person" -> 0
        self.type_cache = {}

        # "en" -> 0
        self.lang_cache = {}

        # ("en", "Person") -> 0
        # actually (0,0) -> 0
        self.lang_type_cache = {}

        # ("freebase", ("en", "Person")) -> 0
        # actually (0,0) -> 0
        self.src_lang_type_cache = {}

    def compact_value(self, value, src):
        if value is None or type(value) == list and len(value) == 0:
            # if no valid list, used for typeless sources
            if len(value) == 0:
                src = self.src_cache.setdefault(src, len(self.src_cache))
                return self.src_lang_type_cache.setdefault(
                    (src, -1), len(self.src_lang_type_cache))

        if type(value) == list:
            return [self.compact_value(v, src) for v in value]

        elif type(value) == tuple and len(value) == 2:
            lang, type_ = value
            lang = self.lang_cache.setdefault(lang, len(self.lang_cache))
            type_ = self.type_cache.setdefault(type_, len(self.type_cache))

            pair = lang, type_
            lang_type_pair = self.lang_type_cache.setdefault(
                pair, len(self.lang_type_cache))

            src = self.src_cache.setdefault(src, len(self.src_cache))
            pair = src, lang_type_pair
            src_langtype_pair = self.src_lang_type_cache.setdefault(
                pair, len(self.src_lang_type_cache))

            return src_langtype_pair

    def fill_dict(self, pairs, src):
        for pair in pairs:
            key, value = pair
            key = key.lower()
            if not key in self.d:
                self.d[key] = len(self.values)
                self.values.append(set())
            compact_value = self.compact_value(value, src)
            if type(compact_value) is list:
                self.values[self.d[key]] |= set(compact_value)
            else:
                self.values[self.d[key]].add(compact_value)

    
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
        self.src_cache = intdict_to_list(self.src_cache)
        self.type_cache = intdict_to_list(self.type_cache)
        self.lang_cache = intdict_to_list(self.lang_cache)
        self.lang_type_cache = intdict_to_list(self.lang_type_cache)
        self.src_lang_type_cache = intdict_to_list(self.src_lang_type_cache)

        logging.info("Compactizing values...")
        self.compactize_values()

        logging.info("Creating dawg...")
        self.dawg = dawg.IntCompletionDAWG(self.d)
        del self.d
        logging.info("compactizing done.")

    def dump(self, pickle_f, dawg_fb):
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
         
