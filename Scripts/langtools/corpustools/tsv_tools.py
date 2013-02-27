"""Miscellaneous tools for handling TSV formatted corpora.
Most functions assume that the first two fields of a file
correspond to word form and POS-tag/morph-analysis respectively, while the last column is mostly expected to contain sequential tags such as chunk or NER tags."""
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
            if curr_sen==[]:
                #consecutive empty lines between sentences are tolerated
                continue
            yield curr_sen
            curr_sen = []
            continue
        curr_sen.append(line.strip().split())
    if curr_sen!=[]:
        yield curr_sen

def get_np_case(chunk):
    nouns = [tok for tok in chunk if 'NOUN' in tok[1]]
    if nouns == []:
        """If an NP contains no noun, we assume its rightmost element
        to be the head"""
        head_kr = chunk[-1][1]
    else:
        head_kr = nouns[-1][1]
    if 'CAS' not in head_kr:
        case = '<CAS<NOM>>'
    else:
        case = re.findall('<CAS<...>>', head_kr)[0]
    return case

def get_pp_case(chunk):
    postps = [tok for tok in chunk if 'POSTP' in tok[1]]
    if postps == []:
        head = '???'
    else:
        head = postps[-1][0]
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
        chunk_cat = chunk[0][-1].split('-')[-1] # this works for O too
        chunk_text = '_'.join([tok[0] for tok in chunk])
        cased_chunk_tag = get_chunk_case(chunk, chunk_cat)
        new_sen.append([chunk_text, cased_chunk_tag])
    return new_sen

def toks_to_chunks(sen, strict=False):
    """converts a list of tokens to a list of chunks, where out-of-chunk
    tokens constitute chunks on their own. If strict is set to True,
    tagging must conform to BIE1 standards, otherwise an exception is raised"""
    new_sen = []
    curr_chunk = []
    for tok in sen:
        if tok[-1] == 'O':
            if curr_chunk!=[] and strict:
                raise InvalidTaggingError
            new_sen.append([tok])
            continue
        chunk_part, chunk_type = tok[-1].split('-')
        if chunk_part in ('B', '1'):
            if curr_chunk!=[] and strict:
                raise InvalidTaggingError
        else:
            if curr_chunk == [] and strict:
                raise InvalidTaggingError

        curr_chunk.append(tok)
        if chunk_part in ('E', '1'):
            new_sen.append(curr_chunk)
            curr_chunk = []

    if curr_chunk!=[] and strict:
        raise InvalidTaggingError
            
    return new_sen    

def print_sen(sen):
    for tok in sen:
        print '\t'.join(tok)
    print

def collapse_chunks_in_corp(stream):
    for sen in sentence_iterator(stream):
        print_sen(collapse_chunks(sen))
