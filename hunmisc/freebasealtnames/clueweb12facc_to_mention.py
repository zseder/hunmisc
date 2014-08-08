"""This script needs 20 tgz files to be downloaded from here:
http://lemurproject.org/clueweb12/FACC1/ and then extracted from
tgz and then possibly rezipped one by one.
The folder structure should look like
ClueWeb12_??/
    ??????/
        *.tsv.gz
        or
        *.tsv


Output will be two dictionaries: possible mentions->entityid and reverse
"""

import os
import logging
import argparse
import cPickle
import multiprocessing

from hunmisc.xzip import gzip_open


def yield_valid_filenames(path):
    for actual_dir, _, filenames in os.walk(path):
        for fn in filenames:
            if fn.endswith("tsv.gz") or fn.endswith("tsv"):
                abspath = "{0}/{1}".format(actual_dir, fn)
                yield abspath


def yield_filepaths(path):
    for fn in yield_valid_filenames(path):
        yield fn


def yield_triplets(istream):
    for l in istream:
        le = l.decode("utf-8").rstrip().split("\t")
        if len(le) != 8:
            continue
        mention = le[2]
        conf = float(le[5])
        entity = le[7]
        yield mention, conf, entity


def filename_to_dict(args):
    fn, minconf, lower = args
    d = {}
    f = (gzip_open(fn) if fn.endswith(".gz") else open(fn))
    for triplet in yield_triplets(f):
        m, c, e = triplet
        if lower:
            m = m.lower()

        if c < minconf:
            continue
        if m not in d:
            d[m] = {}
        d[m][e] = d[m].get(e, 0) + 1
    return d


def merge_dicts(dicts, total):
    d = {}
    c = 0
    for smalldict in dicts:
        for k1 in smalldict:
            if k1 not in d:
                d[k1] = {}
            for k2 in smalldict[k1]:
                d[k1][k2] = d[k1].get(k2, 0) + smalldict[k1][k2]
        c += 1
        logging.info("{}/{} done.".format(c, total))
    return d


def build_first_dict_parallel(input_folder, minconf, lower):
    p = multiprocessing.Pool()
    fns = list(yield_filepaths(input_folder))
    d = {}
    res = p.imap(filename_to_dict, ((fn, minconf, lower) for fn in fns))
    d = merge_dicts(res, len(fns))
    return d


def build_first_dict(input_folder, minconf, lower):
    fns = list(yield_filepaths(input_folder))
    d = merge_dicts((filename_to_dict((f, minconf, lower))
                     for f in fns), len(fns))
    return d


def reverse_dict(d):
    rd = {}
    for k in d:
        for k2 in d[k]:
            if k2 not in rd:
                rd[k2] = {}
            rd[k2][k] = d[k][k2]
    return rd


def get_argparser():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="input folder")
    ap.add_argument("output", help="output 1 file name")
    ap.add_argument("--output-reverse", help="output 2 file name")
    ap.add_argument("-m", "--minconf", default=0.98,
                    help="minimum confidence")
    ap.add_argument("--lower", help="lowercasing",
                    type=bool, default=False)
    ap.add_argument("--parallel", help="running in parallel. default is True",
                    type=bool, default=True)
    return ap


def main():
    arguments = get_argparser().parse_args()
    input_folder = arguments.input
    out1 = arguments.output
    minconf = arguments.minconf
    lower = arguments.lower
    if arguments.parallel:
        d = build_first_dict_parallel(input_folder, minconf, lower)
    else:
        d = build_first_dict(input_folder, minconf, lower)
    cPickle.dump(d, open(out1, "wb"), -1)
    if arguments.output_reverse is not None:
        d2 = reverse_dict(d)
        cPickle.dump(d2, open(arguments.output_reverse, "wb"), -1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
