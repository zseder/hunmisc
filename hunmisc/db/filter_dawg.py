import sys
from hunmisc.db.entitydb import EntityDB
from unidecode import unidecode
import re

class ModifyEBD():

    def __init__(self, dir_old, dir_new, needed_sources_list=None):
        
        self.dir_old = dir_old
        self.dir_new = dir_new
        if needed_sources_list != None:
            self.needed_sources = set(needed_sources_list)
        self.compile_regexes()    

    def compile_regexes(self):
        
        self.e_inserter = lambda x: re.compile(
            u"(\xe4|\xf6|\xfc)", re.UNICODE).sub("\g<1>e", x)

    def modify_edb(self, modifier):

        orig_edb = EntityDB.load_from_files(self.dir_old)
        altered_edb = EntityDB()
        for e in orig_edb.dawg.keys():
            types = orig_edb.get_type(e)
            for type_ in types:
                src, data = type_
                needed, e_, data_, src_ = modifier((e, data, src))
                if e_ == '':
                    continue
                if needed:
                    altered_edb.add_entity(e_, data_, src_)
        altered_edb.dump_to_files(self.dir_new)

    def filter_edb_based_on_source(self, needed_sources):

        self.modify_edb(lambda x: (x[2] in needed_sources, x[0], x[1], x[2]))   
    
    def unidecode_entities(self):

        self.modify_edb(lambda x: 
                        (True, unidecode(self.e_inserter(x[0])), x[1], x[2]))

def main():

    dir_old = sys.argv[1]
    dir_new = sys.argv[2]
    a = ModifyEBD(dir_old, dir_new)
    a.unidecode_entities()
 
if __name__ == "__main__":
    main()
