from collections import defaultdict
import logging
import cPickle
import os
import dawg

import cache


def intdict_to_list(d):
    return [k for k, v in sorted(d.iteritems(), key=lambda x: x[1])]


def generate_filenames_from_path(path):
    if os.path.exists(path):
        entitydb_fn = path + '/entitydb.pickle'
        main_dawg_fn = path + '/entities.dawg'
        prefix_dawg_fn = path + '/prefix.dawg'
    else:
        entitydb_fn = path + ".pickle"
        main_dawg_fn = path + '.main_dawg'
        prefix_dawg_fn = path + '.prefix_dawg'
    return entitydb_fn, main_dawg_fn, prefix_dawg_fn


class EntityDB(object):
    def __init__(self, sources=None, max_length=5):
        self.__init_caches(sources)
        self.d = {}
        self.values = []
        self.to_keep = None
        self.long_entities = defaultdict(set)
        self.max_l = max_length

    def add_to_keep_list(self, to_keep):
        self.to_keep = set(to_keep)

    def __init_cache(self, source):
        self.caches[source] = cache.init_cache(source)
        self.source_indices[source] = len(self.source_indices)
        self.source_names.append(source)

    def __init_caches(self, sources):
        self.caches = {}
        self.source_indices = {}
        self.source_names = []

        if sources is None:
            sources = []

        for source in sources:
            self.__init_cache(source)

        self.value_cache = cache.DictValueCache()

    def add_entity(self, entity, data, src):
        entity = entity.lower()
        if self.to_keep is not None:
            if entity not in self.to_keep:
                return

        if not entity in self.d:
            self.d[entity] = len(self.values)
            self.values.append(set())

        if src not in self.caches:
            self.__init_cache(src)

        compact_value = self.caches[src].store(data)
        compact_pair = self.value_cache.store((self.source_indices[src],
                                               compact_value))
        self.values[self.d[entity]].add(compact_pair)

        es = entity.split()
        if len(es) > self.max_l:
            self.long_entities[" ".join(es[:self.max_l])].add(entity)

    def finalize_values(self):
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

    def finalize_long_entities(self):
        logging.info("Creating prefix dawg...")
        self.long_values = {}
        self.long_entities = dawg.IntDAWG(
            (p, self.long_values.setdefault(frozenset(full),
                                            len(self.long_values)))
            for p, full in self.long_entities.iteritems())
        self.long_values = [k for k, _ in
                            sorted(self.long_values.iteritems(),
                                   key=lambda x: x[1])]

    def finalize(self):
        for cache in self.caches.itervalues():
            cache.finalize()
        self.value_cache.finalize()

        logging.info("Finalizing values...")
        self.finalize_values()

        logging.info("Creating main dawg...")
        self.dawg = dawg.IntCompletionDAWG(self.d)
        del self.d

        self.finalize_long_entities()

        logging.info("finalizing done.")

    def dump(self, *args):
        if len(args) == 3:
            self.dump_to_files(*args)
        elif len(args) == 1:
            self.dump_to_path(*args)

    def dump_to_files(self, pickle_f, dawg_fb, prefix_trie_fb):
        self.to_keep = None
        self.finalize()
        self.dawg.write(dawg_fb)
        del self.dawg

        self.long_entities.write(prefix_trie_fb)
        del self.long_entities
        cPickle.dump(self, pickle_f, 2)

    def dump_to_path(self, path):
        e_fn, md_fn, pd_fn = generate_filenames_from_path(path)
        with open(e_fn, "w") as pickle_f:
            with open(md_fn, 'wb') as dawg_fb:
                with open(pd_fn, "wb") as pd_fb:
                    self.dump(pickle_f, dawg_fb, pd_fb)

    @staticmethod
    def load_from_files(pickle_fn, dawg_fn, prefix_dawg_fn):
        entity_db = cPickle.load(open(pickle_fn, "rb"))
        entity_db.dawg = dawg.IntCompletionDAWG()
        entity_db.dawg.load(dawg_fn)
        entity_db.long_entities = dawg.IntDAWG()
        entity_db.long_entities.load(prefix_dawg_fn)
        return entity_db

    @staticmethod
    def load_from_path(path):
        e_fn, md_fn, pd_fn = generate_filenames_from_path(path)
        return EntityDB.load(e_fn, md_fn, pd_fn)

    @staticmethod
    def load(*args):
        if len(args) == 3:
            return EntityDB.load_from_files(*args)
        elif len(args) == 1:
            return EntityDB.load_from_path(*args)

    @staticmethod
    def create_from_list(file_name):
        db = EntityDB()
        entity_list = (line.strip().split('\t') for line in file(file_name))
        for entity, e_type in entity_list:
            db.add_entity(entity, None, e_type)
        return db

    def get_type(self, name):
        if name not in self.dawg:
            return None
        try:
            value_index = self.dawg[name]
            res = []
            values = self.values[value_index]
            for value_cache_index in values:
                src, value = self.value_cache.get(value_cache_index)
                src = self.source_names[src]
                res.append((src, self.caches[src].get(value)))
            return res
        except IndexError:
            logging.error("There is an error in compact EntityDB")
            logging.exception("IndexError")

    def get_ngrams_with_prefix(self, prefix):
        if prefix not in self.long_entities:
            return

        res = []
        for entity in self.long_values[self.long_entities[prefix]]:
            res.append((entity, self.get_type(entity)))
        return res
