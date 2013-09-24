import sys
import logging
from entitydb import EntityDB
import gzip

try:
    from hunmisc.corpustools import dbpedia
    from hunmisc.corpustools import freebase
except ImportError:
    sys.stderr.write("Hunmisc (https://github.com/zseder/hunmisc/) " +
                     "has to be in pythonpath\n")
    sys.exit(-1)

def gen_freebase_results(f):
    for res in freebase.parse(f):
        word, langs, domains = res
        l = []
        for lang in langs:
            for domain in domains:
                l.append((lang, domain))
        
        if len(word) == 0:
            sys.stderr.write("Freebase parser provided empty string\n")
            continue
        
        yield word, l

def gen_dbpedia_results(f, lang):
    for res in dbpedia.parse(f):
        word, categories = res
        category = dbpedia.select_main_category(categories)

        if len(word) == 0:
            sys.stderr.write("dbpedia parser provided empty string\n")
            continue

        yield word, [(lang, category)]

def add_geonames_list_file(f):
    for l in f:
        l = l.strip().decode("utf-8")
        le = l.split("\t")
        if len(le) != 3:
            continue

        entity, lang, type_ = le
        yield entity, [(lang, type_)]

def add_simple_list_file(f):
    for l in f:
        l = l.strip().decode("utf-8")
        yield l, [(None, None)]

def main():
    entity_db = EntityDB()
    freebase_dump_gzip_f = sys.argv[1]
    dbpedia_en_f = sys.argv[2]
    dbpedia_de_f = sys.argv[3]
    geo_f = sys.argv[4]
    gerword_def_f = sys.argv[5]
    gerword_undef_f = sys.argv[6]

    with gzip.open(freebase_dump_gzip_f) as f:
        entity_db.fill_dict(gen_freebase_results(f), "freebase")

    with open(dbpedia_en_f) as f:
        entity_db.fill_dict(gen_dbpedia_results(f, "en"), "dbpedia")
    with open(dbpedia_de_f) as f:
        entity_db.fill_dict(gen_dbpedia_results(f, "de"), "dbpedia")

    with open(geo_f) as f:
        entity_db.fill_dict(add_geonames_list_file(f), "geonames")

    with open(gerword_def_f) as f:
        entity_db.fill_dict(add_simple_list_file(f), "german_wikt_defined")

    with open(gerword_undef_f) as f:
        entity_db.fill_dict(add_simple_list_file(f), "german_wikt_undefined")

    with open('words.dawg.compact', 'wb') as dawg_fb:
        with open("entities.pickle", "w") as pickle_f:
            entity_db.dump(pickle_f, dawg_fb)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s : %(module)s (%(lineno)s) - %(levelname)s - %(message)s")
    main()
