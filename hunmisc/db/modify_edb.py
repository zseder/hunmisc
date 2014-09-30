import sys
from unidecode import unidecode
import re

from hunmisc.db.entitydb import EntityDB


class ModifyEBD():

    def __init__(self, edb_old, edb_new, needed_sources_list=None):
        self.orig_edb = edb_old
        self.new_edb = edb_new
        if needed_sources_list is not None:
            self.needed_sources = set(needed_sources_list)
        self.compile_regexes()

    def compile_regexes(self):
        self.e_inserter = lambda x: re.compile(
            u"(\xe4|\xf6|\xfc)", re.UNICODE).sub("\g<1>e", x)

    def modify_edb(self, modifier):
        for e in self.orig_edb.dawg.keys():
            types = self.orig_edb.get_type(e)
            for type_ in types:
                src, data = type_
                needed, e_, data_, src_ = modifier((e, data, src))
                if e_ == '':
                    continue
                if needed:
                    self.new_edb.add_entity(e_, data_, src_)

    def filter_edb_based_on_source(self, needed_sources):
        self.modify_edb(lambda x: (x[2] in needed_sources, x[0], x[1], x[2]))

    def unidecode_entities(self):
        self.modify_edb(lambda x:
                        (True, unidecode(self.e_inserter(x[0])), x[1], x[2]))


def main():

    dir_old = sys.argv[1]
    dir_new = sys.argv[2]
    edb = EntityDB()
    a = ModifyEBD(EntityDB.load(dir_old), edb)
    a.unidecode_entities()
    edb.dump(dir_new)


if __name__ == "__main__":
    main()
