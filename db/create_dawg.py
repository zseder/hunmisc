import sys
import logging
import gzip

from hunmisc.db.entitydb import EntityDB
from hunmisc.corpustools import dbpedia
from hunmisc.corpustools import freebase

def gen_freebase_pairs(f):
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

def gen_dbpedia_pairs(f, lang):
    for res in dbpedia.parse(f):
        word, categories = res
        category = dbpedia.select_main_category(categories)

        if len(word) == 0:
            sys.stderr.write("dbpedia parser provided empty string\n")
            continue

        yield word, [(lang, category)]

def gen_geoname_pairs(f):
    for l in f:
        l = l.strip().decode("utf-8")
        le = l.split("\t")
        if len(le) != 3:
            continue

        entity, lang, type_ = le
        yield entity, (lang, type_)

def gen_simple_list_pairs(f):
    for l in f:
        l = l.strip().decode("utf-8")
        yield l, None

def main():
    entity_db = EntityDB(["freebase", "dbpedia", "geonames",
                         "german_wikt_defined", "german_wikt_undefined"])
    freebase_dump_gzip_f = sys.argv[1]
    dbpedia_en_f = sys.argv[2]
    dbpedia_de_f = sys.argv[3]
    geo_f = sys.argv[4]
    gerword_def_f = sys.argv[5]
    gerword_undef_f = sys.argv[6]
    dawg_fn = sys.argv[-1]
    entities_fn = sys.argv[-2]
    if len(sys.argv) > 9:
        with open(sys.argv[7]) as f:
            entity_db.add_to_keep_list(
                [l.strip().decode("utf-8") for l in f.readlines()])

    with gzip.open(freebase_dump_gzip_f) as f:
        for entity, data in gen_freebase_pairs(f):
            entity_db.add_entity(entity, data, "freebase")

    with open(dbpedia_en_f) as f:
        for entity, data in gen_dbpedia_pairs(f, "en"):
            entity_db.add_entity(entity, data, "dbpedia")

    with open(dbpedia_de_f) as f:
        for entity, data in gen_dbpedia_pairs(f, "de"):
            entity_db.add_entity(entity, data, "dbpedia")

    with open(geo_f) as f:
        for entity, data in gen_geoname_pairs(f):
            entity_db.add_entity(entity, data, "geonames")

    with open(gerword_def_f) as f:
        for entity, data in gen_simple_list_pairs(f):
            entity_db.add_entity(entity, data, "german_wikt_defined")

    with open(gerword_undef_f) as f:
        for entity, data in gen_simple_list_pairs(f):
            entity_db.add_entity(entity, data, "german_wikt_undefined")

    with open(dawg_fn, 'wb') as dawg_fb:
        with open(entities_fn, "w") as pickle_f:
            entity_db.dump(pickle_f, dawg_fb)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s : %(module)s (%(lineno)s) - %(levelname)s - %(message)s")
    main()
