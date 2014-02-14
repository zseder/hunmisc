import sys
from entitydb import EntityDB

def create_filtered(dir_old, dir_new, needed_sources):
    
    orig_edb = EntityDB.load_from_files(dir_old)
    filtered_edb = EntityDB()
    for e in orig_edb.dawg.keys(): 
        types = orig_edb.get_type(e)
        for type_ in types:
            src, data = type_
            print src
            if src in needed_sources:
                filtered_edb.add_entity(e, data, src)  
    filtered_edb.dump_to_files(dir_new) 

def main():

    dir_old = sys.argv[1]
    dir_new = sys.argv[2]
    needed_sources = set(sys.argv[3:])
    create_filtered(dir_old, dir_new, needed_sources)
 
if __name__ == "__main__":
    main()
