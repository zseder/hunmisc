import sys
import logging

def read_bie1_sentence(sentence, chunk_field):
    """BIE1 or BI format reader
    a @param sentence input is a list of tokens, a token is an iterable,
    and @param chunk_field is the index of which chunk we want to read
    output is a sentence that is a list of chunks or out of chunk-tokens

    Example:
    [(token1_tag1, token1_tag2, token1_tagX, ...),
     ([(tokeninchunk1_tag1, tokeninchunk1_tagX,...),
       ...
      ], name_of_chunk),
     (token_out_of_chunk_again_tag1, ...),
     ...
    ]
    """
    result = []
    active_chunk = None
    for tok in sentence:
        # close active chunk first if needed
        if tok[chunk_field][0] in ["O", "1", "B"]:
            if active_chunk is not None:
                result.append(tuple(active_chunk))
                active_chunk = None

        token_if_append = tuple(tok[:chunk_field]) + tuple(tok[chunk_field+1:])

        # no-chunk token is simple
        if tok[chunk_field] == "O":
            result.append(tuple(tok))
        # 1-chunks are gonna be one-length chunks
        elif tok[chunk_field].startswith("1-"):
            result.append([[token_if_append], tok[chunk_field][2:]])
        elif tok[chunk_field][0] == "B":
            active_chunk = [[], tok[chunk_field][2:]]

        if tok[chunk_field][0] in ["B", "I", "E"]:
            if active_chunk is None:
                logging.warning("there is an improper use of I or E tag " +
                                "in the sentence:\n" +
                                "\n".join(("\t".join(tok) for tok in sentence)
                                         ))
                active_chunk = [[], tok[chunk_field][2:]]

            active_chunk[0].append(token_if_append)

    # close final chunks if stayed any;# It's not done by "E"-tags,
    # because of being more robust, handle BI-only tagging too
    if active_chunk is not None:
        result.append(tuple(active_chunk))

    return result

def read_bie1_corpus(f, chunk_field=-1):
    sentences = []
    sentence = []
    for l in f:
        le = l.strip().split("\t")
        if len(l.strip()) == 0:
            if len(sentence) > 0:
                sentences.append(read_bie1_sentence(sentence, chunk_field))
            sentence = []
        else:
            sentence.append(le)

    # close final sentence, if there were no empty line before EOF
    if len(sentence) > 0:
        sentences.append(read_bie1_sentence(sentence, chunk_field))

def test1():
    read_bie1_corpus(file(sys.argv[1]), int(sys.argv[2]))

def test2():
    pass

if __name__ == "__main__":
    test1()
    test2()

