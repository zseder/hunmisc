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


import os
import re
import sys
from collections import defaultdict

import nltk
from nltk.tokenize.punkt import PunktSentenceTokenizer
from nltk.tokenize.punkt import PunktWordTokenizer
from nltk.tag.hunpos import HunposTagger
from nltk.stem.wordnet import WordNetLemmatizer

from nltk.corpus.reader.wordnet import NOUN, VERB, ADJ, ADV


_penn_to_major_pos = {"JJ": ADJ, "JJR": ADJ, "JJS": ADJ,
                     "NN": NOUN, "NNS": NOUN, "NNP": NOUN, "NNPS": NOUN,
                     "RB": ADV, "RBR": ADV, "RBS": ADV,
                     "VB": VERB, "VBD": VERB, "VBG": VERB, "VBN": VERB, "VBP": VERB, "VBZ": VERB}
penn_to_major_pos = defaultdict(lambda: NOUN)
penn_to_major_pos.update(_penn_to_major_pos)

class NltkTools:
    _abbrevPattern  = re.compile(r"([\w][\w]?[.]){2,}$", re.UNICODE)
    _datePattern    = re.compile(r"(^|\s)(?:[\d]{2}){1,2}[.]$", re.UNICODE)
    _cleanerPattern = re.compile("(\w\w)([.?,:;!])(\w)(\w)", re.UNICODE)

    def __init__(self, tok=False, wtok=False, stok=False, pos=False, stem=False,
                 pos_model=None, abbrev_set=None, stok_model = None):
        """@param abbrev_set: a set of frequent abbreviations."""
        if tok:
            wtok = True
            stok = True

        if wtok:
            self.wordTokenizer = PunktWordTokenizer()
            #self.punktSplitter = re.compile(r"^([\w\d]+)([.?,:;!])$", re.UNICODE)
            self.punktSplitter = re.compile(r"^(.+)([.?,:;!])$", re.UNICODE)
            # Bragantino,2006.In fix this shit
        if stok:
            if stok_model is not None:
                try:
                   self.senTokenizer = stok_model
                except LookupError:
                    sys.stderr.write("WARNING: tokenizer cannot be loaded")
                    sys.stderr.write("WARNING: using an untrained sen_tokenizer")
                    self.senTokenizer = PunktSentenceTokenizer()
            else:        
                try:
                    self.senTokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
                except LookupError:
                    sys.stderr.write("WARNING: english tokenizer cannot be loaded, nltk.data does not contain in!")
                    sys.stderr.write("WARNING: using an untrained sen_tokenizer")
                    self.senTokenizer = PunktSentenceTokenizer()
        
        self.abbrev_set = (set(abbrev_set) if abbrev_set is not None else set())
        
        if pos:
            if pos_model is not None:
                self.posTagger = HunposTagger(pos_model, encoding="utf-8")
            else:
                self.posTagger = HunposTagger(os.path.join(os.environ['HUNPOS'], 'english.model'), encoding="utf-8")
        if stem:
            self.stemmer = WordNetLemmatizer()

    def tokenize(self, raw):
        """Runs sentence and then word tokenization. Does some abbreviation-
        detection to fix false sentence endings."""
        sentences = self.sen_tokenize(raw)
        tokens = [self.word_tokenize(sen) for sen in sentences]
        for i in reversed(xrange(len(tokens) - 1)):
            if ( self.is_abbrev(tokens[i][-1])
                 or NltkTools._abbrevPattern.match(tokens[i][-1]) is not None
                 and not NltkTools.starts_with_upper(tokens[i + 1][0])):
                tokens[i].extend(tokens[i + 1])
                tokens.pop(i + 1)
        return tokens
        

    def sen_tokenize(self, raw):
        """Tokenizes the raw text into sentences."""
        raw = NltkTools.cleanup_puncts(raw)
        return self.senTokenizer.tokenize(raw)

    def filter_long_sentences(self, raw, length=1024):
        """Filters "sentences" (non-whitespace character sequences longer than
        length) from the text."""
        # TODO: This looks nice but it is too generous with memory use
        return ' '.join(filter(lambda x: len(x) <= length, re.split(r"\s+", raw)))
        
    def sen_abbr_tokenize(self, raw):
        """Tokenizes the raw text into sentences, and tries to handle problems
        caused by abbreviations and such."""
        sentences = self.sen_tokenize(raw)
        for i in reversed(xrange(len(sentences) - 1)):
            if (NltkTools._abbrevPattern.search(sentences[i]) is not None
                    and not NltkTools.starts_with_upper(sentences[i + 1])):
                sentences[i] = ' '.join(sentences[i:i+2])
                sentences.pop(i + 1)
        return sentences

    @staticmethod
    def starts_with_upper(text):
        """Checks if the sentence starts with an upper case letter."""
        t = text.lstrip()
        return len(t) > 0 and t[0].isupper()
    
    @staticmethod
    def cleanup_puncts(raw):
        pos = 0
        cleaner = NltkTools._cleanerPattern.search(raw[pos:])
        while cleaner:
            if cleaner.group(2) == "." and not cleaner.group(3)[0].isupper():
                pos = cleaner.end()
            elif cleaner.group(1)[-1].isdigit() and cleaner.group(3)[0].isdigit():
                pos = cleaner.end()
            else:
                changed_part_string = cleaner.expand(r"\1\2 \3\4")
                raw = raw[:cleaner.start()] + changed_part_string + raw[cleaner.end():]
                pos = cleaner.end()
            cleaner = NltkTools._cleanerPattern.search(raw, pos)
        return raw
    
    def is_abbrev(self, tok):
        return tok in self.abbrev_set

    def word_tokenize(self, sen):
        """Tokenizes the sentence to words and splits the sentence ending
        punctuation mark from the last word and adds it as the last token."""
        tokens = self.wordTokenizer.tokenize(sen)
        if len(tokens) == 0:
            return []
        punktMatchObject = self.punktSplitter.match(tokens[-1])
        if punktMatchObject is not None and not self.is_abbrev(tokens[-1]):
            tokens = tokens[:-1] + list(punktMatchObject.groups())
        return tokens

    def pos_tag(self, sentokens):
        return self.posTagger.tag(sentokens)

    def stem(self, tokens):
        return ((tok, pos, self.stemmer.lemmatize(tok, penn_to_major_pos[pos])) for tok, pos in tokens)
        
    def tag_raw(self, raw_text):
        """Convenience method for tagging (a line of) raw text. The NltkTools
        instance must have been initialized with C{pos=True, stem=True, tok=True}.
        It is a generator: returns attribute array of one word at a time. The
        attributes are the word, the pos tag and the stem."""
        sens = self.tokenize(raw_text)
        pos_tagged = list(self.pos_tag(sen) for sen in sens)
        stemmed = list(self.stem(pos_tagged_sen) for pos_tagged_sen in pos_tagged)
        for sen in stemmed:
            for tok in sen:
                yield tok
            yield []
        return
    
if __name__ == "__main__":
    nt = NltkTools(pos=True, stem=True, tok=True)
    
    for l in sys.stdin:
        l = l.decode("utf-8").rstrip()
        sens = nt.tokenize(l)
        pos_tagged = list(nt.pos_tag(sen) for sen in sens)
        stemmed = list(nt.stem(pos_tagged_sen) for pos_tagged_sen in pos_tagged)
        for sen in stemmed:
            for tok in sen:
                print u"\t".join(tok).encode("utf-8")
            print

