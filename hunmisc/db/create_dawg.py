import sys
import logging
from collections import defaultdict

from hunmisc.db.entitydb import EntityDB
from hunmisc.corpustools import dbpedia
from hunmisc.corpustools import freebase
from hunmisc.xzip import gzip_open

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

        yield word, (lang, category)

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

def gen_entity_type_pairs(f):
    for l in f:
        le = l.strip().decode("utf-8").split("\t")
        if len(le) == 2:
            yield le[0], tuple(le[1].split(","))

def add_freebase(freebase_dump_gzip_f, entity_db):
    f = gzip_open(freebase_dump_gzip_f)
    c = 0
    for entity, data in gen_freebase_pairs(f):
        for dat in data:
            entity_db.add_entity(entity, dat, "freebase")
        c += 1
        if c % 1000000 == 0:
            logging.info("freebase: {0}".format(c))


def add_dbpedia(dbpedia_en_f, dbpedia_de_f, entity_db):
    with open(dbpedia_en_f) as f:
        for entity, data in gen_dbpedia_pairs(f, "en"):
            entity_db.add_entity(entity, data, "dbpedia")

    with open(dbpedia_de_f) as f:
        for entity, data in gen_dbpedia_pairs(f, "de"):
            entity_db.add_entity(entity, data, "dbpedia")

def add_geonames(geo_f, entity_db):
    with open(geo_f) as f:
        for entity, data in gen_geoname_pairs(f):
            entity_db.add_entity(entity, data, "geonames")

def add_wikt(gerword_def_f, gerword_undef_f, entity_db):
    with open(gerword_def_f) as f:
        for entity, data in gen_entity_type_pairs(f):
            entity_db.add_entity(entity, data, "german_wikt_defined")

    with open(gerword_undef_f) as f:
        for entity, data in gen_entity_type_pairs(f):
            entity_db.add_entity(entity, data, "german_wikt_undefined")

def add_unambig_freebase(freebase_unambig_types_f, entity_db):
    f = open(freebase_unambig_types_f)
    fb_d = defaultdict(set)
    for l in f:
        le = l.rstrip().split("\t")
        if len(le) != 8: continue
        t = le[7]
        mention = le[0].decode("utf-8").lower()
        if len(mention) > 0:
            fb_d[mention].add((t, "en"))

        en_entity = le[4].decode("utf-8").lower()
        if len(en_entity) > 0:
            fb_d[en_entity].add((t, "en"))

        de_entity = le[5].decode("utf-8").lower()
        if len(de_entity) > 0:
            fb_d[de_entity].add((t, "de"))

    for k in fb_d:
        types = set(t for t, l in fb_d[k])
        if len(types) == 1:
            for t, l in fb_d[k]:
                entity_db.add_entity(k, (t, l), "freebase_unambig")

def main():
    entity_db = EntityDB()
    freebase_notable_types_f = sys.argv[1]
    dbpedia_en_f = sys.argv[2]
    dbpedia_de_f = sys.argv[3]
    geo_f = sys.argv[4]
    gerword_def_f = sys.argv[5]
    gerword_undef_f = sys.argv[6]
    prefix_dawg_fn = sys.argv[-1]
    dawg_fn = sys.argv[-2]
    entities_fn = sys.argv[-3]
    if len(sys.argv) > 10:
        with open(sys.argv[7]) as f:
            entity_db.add_to_keep_list(
                [l.strip().decode("utf-8").lower() for l in f.readlines()])

    add_unambig_freebase(freebase_notable_types_f, entity_db)
    #add_freebase(freebase_dump_gz_f, entity_db)
    #add_dbpedia(dbpedia_en_f, dbpedia_de_f, entity_db)
    #add_geonames(geo_f, entity_db)
    add_wikt(gerword_def_f, gerword_undef_f, entity_db)

    with open(dawg_fn, 'wb') as dawg_fb:
        with open(entities_fn, "w") as pickle_f:
            with open(prefix_dawg_fn, "wb") as pd_fb:
                entity_db.dump(pickle_f, dawg_fb, pd_fb)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s : %(module)s (%(lineno)s) - %(levelname)s - %(message)s")
    main()
