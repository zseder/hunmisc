"""This script needs 20 tgz files to be downloaded from here:
http://lemurproject.org/clueweb12/FACC1/ and then extracted from
tgz. The folder structure should look like
ClueWeb12_??/
    ??????/
        *.tsv.gz


Output will be two dictionaries: possible mentions->entityid and reverse
"""

import os
import logging
import argparse
import cPickle

from hunmisc.xzip import gzip_open


def yield_valid_filenames(path):
    for actual_dir, _, filenames in os.walk(path):
        for fn in filenames:
            if fn.endswith("tsv.gz"):
                abspath = "{0}/{1}".format(actual_dir, fn)
                yield abspath


def yield_filepaths(path):
    filenum = len([_ for _ in yield_valid_filenames(path)])
    c = 1
    for fn in yield_valid_filenames(path):
        logging.info("Processing {0}/{1} file: {2}".format(
            c, filenum, fn))
        yield fn
        c += 1


def yield_triplets(istream):
    for l in istream:
        le = l.decode("utf-8").split("\t")
        if len(le) != 8:
            continue
        mention = le[2]
        conf = float(le[5])
        entity = le[7]
        yield mention, conf, entity


def build_first_dict(input_folder, minconf):
    d = {}
    for f in yield_filepaths(input_folder):
        for triplet in yield_triplets(gzip_open(f)):
            m, c, e = triplet
            if c < minconf:
                continue
            if m not in d:
                d[m] = {}
            d[m][e] = d[m].get(e, 0) + 1
    return d


def reverse_dict(d):
    rd = {}
    for k in d:
        for k2 in d[k]:
            if k2 not in rd:
                rd[k2] = {}
            rd[k2][k] = d[k][k2]


def get_argparser():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="input folder")
    ap.add_argument("output", help="output 1 file name")
    ap.add_argument("--output-reverse", help="output 2 file name")
    ap.add_argument("-m", "--minconf", default=0.98,
                    help="minimum confidence")
    return ap

def main():
    arguments = get_argparser().parse_args()
    input_folder = arguments.input
    out1 = arguments.output
    minconf = arguments.minconf
    d = build_first_dict(input_folder, minconf)
    cPickle.dump(d, open(out1, "wb"), -1)
    if arguments.output_reverse is not None:
        d2 = reverse_dict(d)
        cPickle.dump(d2, open(arguments.output_reverse, "wb"), -1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
