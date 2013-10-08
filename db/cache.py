import sys

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



