"""
Copyright 2011-13 Attila Zseder
Email: zseder@gmail.com

This file is part of hunmisc project
url: https://github.com/zseder/hunmisc

hunmisc is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
"""


"""Miscellaneous tools for handling TSV formatted corpora.
Most functions assume that the first two fields of a file
correspond to word form and POS-tag/morph-analysis respectively, while the last
column is mostly expected to contain sequential tags such as chunk or NER tags.
"""
import re

class InvalidTaggingError(Exception):
    pass

def sentence_iterator(input, comment_tag=None):
    """converts a tsv-format stream to a generator of lists of lists
    if comment_tag is not None, lines starting with comment_tag are ignored
    (but do not count as sentence breaks)"""
    curr_sen = []
    while True:
        line = input.readline()
        if not line:
            break
        if comment_tag and line.startswith(comment_tag):
            continue
        if line == '\n':
            if curr_sen == []:
                # consecutive empty lines between sentences are tolerated
                continue
            yield curr_sen
            curr_sen = []
            continue
        curr_sen.append(line.strip().split('\t'))
    if curr_sen != []:
        yield curr_sen

cas_patt = re.compile('<CAS<...>>')
def get_np_case(chunk, kr_field=1):
    nouns = [tok for tok in chunk if 'NOUN' in tok[kr_field]]
    if nouns == []:
        # If an NP contains no noun, we assume its rightmost element
        # to be the head
        head_kr = chunk[-1][kr_field]
    else:
        head_kr = nouns[-1][kr_field]
    if 'CAS' not in head_kr:
        case = '<CAS<NOM>>'
    else:
        case = cas_patt.findall(head_kr)[0]
    return case

def get_pp_case(chunk, kr_field=1, lemma_field=2):
    postps = [tok for tok in chunk if 'POSTP' in tok[kr_field]]
    if postps == []:
        head = '???'
    else:
        head = postps[-1][lemma_field].lower()
    return '<' + head + '>'

def get_chunk_case(chunk, cat, kr_field=1, lemma_field=2):
    if cat not in ('NP', 'PP'):
        return cat
    elif cat == 'NP':
        case = get_np_case(chunk, kr_field)
    else:
        case = get_pp_case(chunk, kr_field, lemma_field)
    return cat + case

def collapse_chunks(sen, word_field=0, kr_field=1,
                    lemma_field=2, chunk_field=-1):
    """converts chunks within a sentence into single tokens bearing the
    chunk tag (and its case, if applicable) as their analysis"""
    new_sen = []
    for chunk in toks_to_chunks(sen, chunk_field):
        if chunk[0][chunk_field] == 'O':
            new_sen.append(chunk[0])
        else:
            chunk_cat = chunk[0][chunk_field].split('-')[-1]
            if chunk_cat.find('<') != -1:  # some datasets already have case
                cased_chunk_tag = chunk_cat
            else:
                chunk_cat = chunk_cat.split('<')[0]
                cased_chunk_tag = get_chunk_case(chunk, chunk_cat,
                                                 kr_field, lemma_field)
            chunk_text = '_'.join([tok[word_field] for tok in chunk])
            new_sen.append([chunk_text, cased_chunk_tag, cased_chunk_tag])
    return new_sen

def toks_to_chunks(sen, strict=False, chunk_field=-1):
    """converts a list of tokens to a list of chunks, where out-of-chunk
    tokens constitute chunks on their own. If strict is set to True,
    tagging must conform to BIE1 standards, otherwise an exception is raised"""
    new_sen = []
    curr_chunk = []
    # print sen
    for tok in sen:
        # print tok
        if tok[chunk_field] == 'O':
            if curr_chunk != [] and strict:
                raise InvalidTaggingError
            new_sen.append([tok])
            continue
        chunk_part, chunk_type = tok[chunk_field].split('-')
        if chunk_part in ('B', '1'):
            if curr_chunk != [] and strict:
                raise InvalidTaggingError
        else:
            if curr_chunk == [] and strict:
                raise InvalidTaggingError

        curr_chunk.append(tok)
        if chunk_part in ('E', '1'):
            new_sen.append(curr_chunk)
            curr_chunk = []

    if curr_chunk != [] and strict:
        raise InvalidTaggingError

    return new_sen

def print_sen(sen):
    for tok in sen:
        print '\t'.join(tok)
    print

def collapse_chunks_in_corp(stream):
    for sen in sentence_iterator(stream):
        print_sen(collapse_chunks(sen))

def get_dependencies(sen, id_field=0, word_field=1, lemma_field=2, msd_field=3,
                     gov_field=-2, dep_field=-1):
    id_to_toks = {"0": {"lemma": "ROOT", "tok": "ROOT", "msd": None}}
    for tok in sen:
        i = tok[id_field]
        if '.' in i or '-' in i:
            continue
        word, gov, dep = (tok[word_field], tok[gov_field], tok[dep_field])
        lemma = None if lemma_field is None else tok[lemma_field]
        msd = None if msd_field is None else tok[msd_field]
        id_to_toks[i] = {
            'tok': word, 'lemma': lemma, 'msd': msd, 'gov': gov, 'dep': dep}
    deps = []
    for i, t in id_to_toks.iteritems():
        if t['lemma'] == 'ROOT':
            continue
        gov = id_to_toks[t['gov']]
        deps.append({
            "type": t['dep'].lower(),
            "gov": {
                'id': t['gov'], "word": gov['tok'], "lemma": gov['lemma'],
                'msd': gov['msd']
            },
            "dep": {
                'id': i, "word": t['tok'], "lemma": t['lemma'],
                'msd': t['msd']
            }
        })

    return deps
