import sys
from collections import defaultdict
import logging

"""
This scripts collects all incoming paths that are built of only redirect and
disambiguation pages
Circles are detected and skipped, only a stderr message warns the user.

Formats (description of what a line should contain)(TAB separated inputs):
  page_ids:
    id namespace title is_redirect
  links:
    src_id src_namespace tgt_title
  redirect_pages:
  disambig_pages:
  normal_pages:
    title
"""

logging.basicConfig(level=logging.INFO)

page_ids_file = file(sys.argv[1])
links_file = file(sys.argv[2])
redirect_pages_file = file(sys.argv[3])
disambig_pages_file = file(sys.argv[4])
normal_pages_file = file(sys.argv[5])
is_reverse = bool(sys.argv[6])

def read_to_set(f):
    s = set()
    for l in f:
        l = l.strip()
        s.add(l)
    return s

redirect_pages = read_to_set(redirect_pages_file)
disambig_pages = read_to_set(disambig_pages_file)
normal_pages = read_to_set(normal_pages_file)

def read_links(f, page_ids, reverse=False):
    links = defaultdict(set)
    c = 0
    for l in f:
        c += 1
        if c % 1000000 == 0:
            sys.stderr.write("%f read.\n" % (c / 1000000.0))
        le = l.strip().split("\t")
        src_id = int(le[0])
        if le[1] != "0":
            continue
        try:
            tgt_title = le[2]
        except IndexError:
            continue
        try:
            tgt_id = page_ids[tgt_title]
        except KeyError:
            continue
        if not reverse:
            links[tgt_id].add(src_id)
        else:
            links[src_id].add(tgt_id)
    return links

def read_ids(f):
    title_to_id = {}
    id_to_title = {}
    for l in f:
        le = l.strip().split("\t")
        title_to_id[le[2]] = int(le[0])
        id_to_title[int(le[0])] = le[2]
    return title_to_id, id_to_title

title_to_id, id_to_title = read_ids(page_ids_file)
dr_pages = set(title_to_id[page] for page in (redirect_pages | disambig_pages) if page in title_to_id)
del redirect_pages
del disambig_pages
links = read_links(links_file, title_to_id)

sys.stderr.write("%d pages to process\n" % len(normal_pages))
c = 0
for page in normal_pages:
    c += 1
    if c % 10000 == 0:
        sys.stderr.write("%d pages processed\n" % c)
    try:
        page_id = title_to_id[page]
    except KeyError:
        sys.stderr.write("No id found for page: %s\n" % page)
        continue
    
    #logging.info("Computing page: %s" % page)
    in_out_pairs = set()
    processed = set()
    to_be_processed = set()
    for neighbour in links[page_id]:
        if neighbour in dr_pages:
            in_out_pairs.add((neighbour, page_id))
            to_be_processed.add(neighbour)
    
    while len(to_be_processed) > 0:
        logging.debug(repr(to_be_processed))
        actual_processed_node = to_be_processed.pop()
        
        if actual_processed_node in processed:
            sys.stderr.write("There is a circle at \"%s\" started from \"%s\"\n" % (id_to_title[actual_processed_node], page))
            continue
        
        for neighbour in links[actual_processed_node]:
            if neighbour == actual_processed_node:
                continue
            if neighbour in dr_pages:
                in_out_pairs.add((neighbour, actual_processed_node))
                to_be_processed.add(neighbour)
        
        processed.add(actual_processed_node)
    
    print "%%#PAGE\t%s" % page
    for pair in in_out_pairs:
        src, tgt = pair
        print "%s\t%s" % (id_to_title[src], id_to_title[tgt])
    print

