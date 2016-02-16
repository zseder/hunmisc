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

def sentence_iterator(input):
    """converts a tsv-format stream to a generator of lists of lists"""
    curr_sen = []
    while True:
        line = input.readline()
        if not line:
            break
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
def get_np_case(chunk):
    nouns = [tok for tok in chunk if 'NOUN' in tok[1]]
    if nouns == []:
        # If an NP contains no noun, we assume its rightmost element
        # to be the head
        head_kr = chunk[-1][1]
    else:
        head_kr = nouns[-1][1]
    if 'CAS' not in head_kr:
        case = '<CAS<NOM>>'
    else:
        case = cas_patt.findall(head_kr)[0]
    return case

def get_pp_case(chunk):
    postps = [tok for tok in chunk if 'POSTP' in tok[1]]
    if postps == []:
        head = '???'
    else:
        head = postps[-1][2].lower()
    return '<'+head+'>'

def get_chunk_case(chunk, cat):
    if cat not in ('NP', 'PP'):
        return cat
    elif cat == 'NP':
        case = get_np_case(chunk)
    else:
        case = get_pp_case(chunk)
    return cat+case

def collapse_chunks(sen):
    """converts chunks within a sentence into single tokens bearing the
    chunk tag (and its case, if applicable) as their analysis"""
    new_sen = []
    for chunk in toks_to_chunks(sen):
        if chunk[0][-1] == 'O':
            new_sen.append(chunk[0])
        else:
            chunk_cat = chunk[0][-1].split('-')[-1]
            chunk_cat = chunk_cat.split('<')[0]  # some datasets already have case # nopep8
            chunk_text = '_'.join([tok[0] for tok in chunk])
            cased_chunk_tag = get_chunk_case(chunk, chunk_cat)
            new_sen.append([chunk_text, cased_chunk_tag, cased_chunk_tag])
    return new_sen

def toks_to_chunks(sen, strict=False):
    """converts a list of tokens to a list of chunks, where out-of-chunk
    tokens constitute chunks on their own. If strict is set to True,
    tagging must conform to BIE1 standards, otherwise an exception is raised"""
    new_sen = []
    curr_chunk = []
    # print sen
    for tok in sen:
        # print tok
        if tok[-1] == 'O':
            if curr_chunk != [] and strict:
                raise InvalidTaggingError
            new_sen.append([tok])
            continue
        chunk_part, chunk_type = tok[-1].split('-')
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

def get_dependencies(sen, tok_field=1, lemma_field=2, msd_field=3,
                     gov_field=-2, dep_field=-1):
    pass
