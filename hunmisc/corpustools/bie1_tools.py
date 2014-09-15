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


import sys
import logging

def parse_bie1_sentence(sentence, chunk_field):
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

        if chunk_field == -1:
            token_if_append = tuple(tok[:chunk_field])
        else:
            token_if_append = tuple(tok[:chunk_field]) + tuple(tok[chunk_field+1:])

        # no-chunk token is simple
        if tok[chunk_field] == "O":
            result.append((token_if_append,"O"))
        # 1-chunks are gonna be one-length chunks
        elif tok[chunk_field].startswith("1-"):
            result.append(([token_if_append], tok[chunk_field][2:]))
        elif tok[chunk_field][0] == "B":
            active_chunk = [[], tok[chunk_field][2:]]

        if tok[chunk_field][0] in ["B", "I", "E"]:
            if active_chunk is None:
                logging.warning("there is an improper use of I or E tag")
                logging.debug(" in the sentence:\n" +
                                "\n".join(("\t".join(tok) for tok in sentence)
                                         ))
                active_chunk = [[], tok[chunk_field][2:]]
            else:
                # if new chunk is different than old chunk, save it and create
                # a new one
                if active_chunk[1] != tok[chunk_field][2:]:
                    result.append(tuple(active_chunk))
                    active_chunk = [[], tok[chunk_field][2:]]

            active_chunk[0].append(token_if_append)

    # close final chunks if stayed any;# It's not done by "E"-tags,
    # because of being more robust, handle BI-only tagging too
    if active_chunk is not None:
        result.append(tuple(active_chunk))

    return result

def read_bie1_corpus(f, chunk_field=-1, sep="\t"):
    sentences = []
    sentence = []
    for l in f:
        le = l.strip().split(sep)
        if len(l.strip()) == 0:
            if len(sentence) > 0:
                sentences.append(parse_bie1_sentence(sentence, chunk_field))
            sentence = []
        else:
            sentence.append(le)

    # close final sentence, if there were no empty line before EOF
    if len(sentence) > 0:
        sentences.append(parse_bie1_sentence(sentence, chunk_field))
    return sentences

def write_chunked_sen(of, sen, sep, s_tag=False):
    for chunk in sen:
        if chunk[1] == "O":
            of.write("{0}{1}{2}\n".format(sep.join(chunk[0]), sep, "O"))
        elif type(chunk[0]) == list:
            if len(chunk[0]) == 1:
                of.write("{0}{1}{2}\n".format(sep.join(chunk[0][0]), sep,
                    "{0}-{1}".format(("S" if s_tag else "1") ,chunk[1])))
            else:
                #first
                of.write("{0}{1}{2}\n".format(sep.join(chunk[0][0]), sep,
                                              "B-{0}".format(chunk[1])))
                # in-between
                for tok in chunk[1:-1]:
                    of.write("{0}{1}{2}\n".format(sep.join(tok[0]), sep,
                                                  "I-{0}".format(chunk[1])))

                # last
                of.write("{0}{1}{2}\n".format(sep.join(chunk[0][-1]), sep,
                                              "E-{0}".format(chunk[1])))
        else:
            raise ValueError("Sentence is not in good format: {0}".format(repr(sen)))

def write_chunked_corp(of, corp, sep="\t", s_tag=False):
    for s in corp:
        write_chunked_sen(of, s, sep, s_tag)
        of.write("\n")

def test1():
    read_bie1_corpus(file(sys.argv[1]), int(sys.argv[2]))

def test2():
    pass

if __name__ == "__main__":
    test1()
    test2()

