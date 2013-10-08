import sys

def init_cache(name):
    if name in ["freebase", "dbpedia"]:
        return LangTypeCache()
    else:
        return DictValueCache()

class DictValueCache(object):
    """This class (and children) implements a store, and supplementary data
    for dawgs are being kept here. EntityDB will create these objects,
    and put values here.
    One source (like freebase, movie list) should have its own cache.
    If there is a smarter cache than default, it can be implemented as an
    inherited class from this base.
    The only requirement for data to be stored is to be hashable.
    """
    def __init__(self):
        self.cache = {}
    
    def store(self, data):
        if data not in self.cache:
            self.cache[data] = len(self.cache)
        return self.cache[data]

    def finalize(self):
        self.cache = [v[0] for v in 
            sorted(lambda x: x[1], self.cache.iteritems(), reverse=True)]

    def get(self, index):
        if type(index) == int and type(self.cache) == dict:
            sys.stderr.write("cache is not finalized yet\n")
            return
        return self.cache[index]

class LangTypeCache(DictValueCache):
    def __init__(self):
        self.lang_cache = {}
        self.type_cache = {}

    def store(self, data):
        if type(data) != tuple and len(data) != 2:
            sys.stderr.write("LangTypeCache accepts 2-tuple data\n")
            return

        lang, type_ = data
        if lang not in self.lang_cache:
            self.lang_cache[lang] = len(self.lang_cache)
        if type_ not in self.type_cache:
            self.type_cache[type_] = len(self.type_cache)

        DictValueCache.store(self, 
            (self.lang_cache[lang], self.type_cache[type_]))

    def finalize(self):
        DictValueCache.finalize(self)
        self.lang_cache = [v[0] for v in 
            sorted(lambda x: x[1], self.lang_cache.iteritems(), reverse=True)]
        self.type_cache = [v[0] for v in 
            sorted(lambda x: x[1], self.type_cache.iteritems(), reverse=True)]



