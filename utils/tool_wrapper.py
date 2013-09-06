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


"""Defines classes that handle the various tools."""

import os.path
import re
import logging

from langtools.utils.huntool_wrapper import Hundisambig
from langtools.utils.huntool_wrapper import MorphAnalyzer, HundisambigAnalyzer
from langtools.utils.huntool_wrapper import LineByLineTagger
from langtools.nltk.nltktools import NltkTools
from langtools.string.xstring import remove_quot_and_wiki_crap_from_word, is_quote_or_garbage

from itertools import chain

class ToolWrapper(object):
    def __init__(self, params):
        pass

class PosTaggerWrapper(ToolWrapper):
    def pos_tag(self, tokens):
        """POS tags the text. @p tokens is a list^3: fields per words in
        sentences. Adds the POS tag as a new field to each word."""
        pass

class LemmatizerWrapper(ToolWrapper):
    def lemmatize(self, tokens):
        """Lemmatizes the text. @p tokens is a list^3: fields per words in
        sentences. Adds the lemma as a new field to each word."""
        pass

class TokenizerBase(ToolWrapper):
    """Base class for word and sentence tokenizers. It includes a few basic
    tools that are likely to be useful for any tokenizer. Namely:
    - a set of patterns that may cause problems at the end of a sentence
    - an abbreviation pattern already in the set
    - a set of abbreviations read from a file, the name of which is specified
      as the 'abbrevs' property.
    """
    _abbrevPattern  = re.compile(r"(?:^|\s)([\w][\w]?[.]){2,}$", re.UNICODE)

    def __init__(self, params):
        abbrevs = params.get('abbrevs')
        self.abbrevs = {}
        if abbrevs is not None:
            for l in file(abbrevs):
                hashmark = l.find('#')
                if hashmark != -1:
                    l = l[0:hashmark]
                parts = l.strip().decode('utf-8').split("\t")
                if len(parts[0]) > 0:
                   self.abbrevs[parts[0]] = True if len(parts) > 1 else False
        self.patterns = set([TokenizerBase._abbrevPattern])

    def _match_patterns(self, token):
        """Checks if @p token matches any of the dangerous patterns."""
        for pattern in self.patterns:
            if pattern.search(token) is not None:
                return True
        return False
        
class SentenceTokenizerWrapper(TokenizerBase):
    """
    Base class for sentence tokenizers. Above the helper fields and methods
    in TokenizerBase, this class also defines the following method:
    - the method _join_sentences used to correct tokenization for sentence
      tokenizers that got a bit too carried away with their task. Uses the
      items above to join parts of incorrectly split sentences together.
    """
    def __init__(self, params):
        TokenizerBase.__init__(self, params)

    def sen_tokenize(self, raw):
        """Tokenizes the raw text into sentences. Returns a list of strings."""
        pass

    def _join_sentences(self, sentences):
        """Joins parts of incorrectly split sentences if the first part ends
        in an abbreviation or one of the 'dangerous' patterns and the next
        starts with a lower-case letter."""
        for i in reversed(xrange(len(sentences) - 1)):
            if self._join_condition(sentences, i):
                sentences[i] = ' '.join(sentences[i : i + 2])
                sentences.pop(i + 1)

    def _join_condition(self, sentences, current):
        """If this method returns @c True, _join_sentences joins the two current
        and the next sentence."""
        end_with_abbrev = self._end_in_abbrev(sentences[current])
        if end_with_abbrev is not None:
            if end_with_abbrev or not NltkTools.starts_with_upper(sentences[current + 1]):
                return True
            return False
        else:
            return (self._match_patterns(sentences[current]) and
                    NltkTools.starts_with_upper(sentences[current + 1]))

    def _end_in_abbrev(self, part):
        """
        Returns the abbreviation type:
        - None, if the word is not an abbreviation;
        - True/False, depending on whether the abbreviation joins sentence
          chunks even if the second chunk starts with an uppercase letter.
        """
        last_word = part.rsplit(None, 1)[-1]
        abbrev_type = self.abbrevs.get(last_word, None)
        return abbrev_type

class WordTokenizerWrapper(TokenizerBase):
    def __init__(self, params):
        TokenizerBase.__init__(self, params)

    def word_tokenize(self, sen):
        """Tokenizes the sentence into words."""
        pass

    def _is_abbrev(self, token):
        """Returns true if @p token is abbreviation."""
        return (token in self.abbrevs or
                TokenizerBase._abbrevPattern.search(token) is not None)

class HundisambigWrapper(PosTaggerWrapper, LemmatizerWrapper):
    def __init__(self, params):
        hundisambig = Hundisambig(params['hundisambig_runnable'],
                                  params['hundisambig_model'],
                                  params['hundisambig_morphtable'],
                                  params.get('ocamorph_encoding', 'iso-8859-2'),
                                  True)
        self.morph_analyzer = HundisambigAnalyzer(hundisambig)

    def add_pos_and_stems(self, tokens):
        """Adds POS tags and lemmatizes the words in @c tokens."""
        for sen_i, sen in enumerate(tokens):
            if sen == []:
                continue
            # TODO The API expects [sentences+], but it can only handle one :(
            ret = list(self.morph_analyzer.analyze([[word[0] for word in sen]]))[0]
            for tok_i, _ in enumerate(sen):
                try:
                    spl = ret[tok_i][1].rsplit('|', 2)
                    tokens[sen_i][tok_i].append(spl[2])
                    tokens[sen_i][tok_i].append(spl[0])
                except Exception, e:
                    logging.warning("Exception:", str(e))
                    logging.warning(unicode(sen[tok_i]).encode('utf-8'))

    def pos_tag(self, tokens):
        """POS tags AND lemmatizes @p tokens."""
        self.add_pos_and_stems(tokens)

    def lemmatize(self, tokens):
        """POS tags AND lemmatizes @p tokens."""
        self.add_pos_and_stems(tokens)

class HunposPosTagger(PosTaggerWrapper):
    """
    Wraps NltkTools, which wraps HunPos as a POS tagger :).
    
    In order for NLTK to find the hunpos executable, the $HUNPOS environment
    variable must point to the directory with the hunpos-tag executable in it.

    The following parameters are used:
    - hunpos_model: the hunpos model file. Default is $HUNPOS/english.model;
    - hunpos_encoding: the encoding used by the hunpos model file. Default is
      iso-8859-1.
    """
    def __init__(self, params):
        self.nt = NltkTools(pos=True, pos_model=params['hunpos_model'])
        self.encoding = params.get('hunpos_encoding', 'iso-8859-1')

    def pos_tag(self, tokens):
        for sen_i, sen in enumerate(tokens):
            tagged_sen = self.nt.pos_tag([tok[0].encode(self.encoding) for tok in sen])
            for tok_i, tagged_tok in enumerate(tagged_sen):
                try:
                    tok, pos = [x.decode(self.encoding) for x in tagged_tok]
                except ValueError:
                    continue
                tokens[sen_i][tok_i].append(pos)

class NltkToolsStemmer(LemmatizerWrapper):
    """
    Wraps the NltkTools stemmer. It currently uses WordnetLemmatizer,
    which is English only.

    @warning This is the original implementation as used in our English
             Wikipedia parser. No effort has been made to clean up the
             code, or to fix the hardwired indexing, etc. The data must
             be already POS tagged, and the POS field must be the last one.
    """
    def __init__(self, params):
        self.nt = NltkTools(stem=True)

    def lemmatize(self, tokens):
        # HACK
        for sen_i, sen in enumerate(tokens):
            stemmed = self.nt.stem(((tok[0], tok[-1]) for tok in sen))
            hard_stemmed = self.nt.stem((((tok[0][0].lower() + tok[0][1:] if tok[0][0].isupper() and tok[0][1:].islower() else tok[0]), tok[-1]) for tok in sen))
            for tok_i, (tok_stemmed, tok_hard_stemmed) in enumerate(zip(stemmed, hard_stemmed)):
                tokens[sen_i][tok_i].append(tok_stemmed[2])
                tokens[sen_i][tok_i].append(tok_hard_stemmed[2])

class NltkToolsTokenizer(SentenceTokenizerWrapper, WordTokenizerWrapper):
    """
    Wraps the NltkTools sentence and word tokenizer.

    The only parameter used is
    - abbrevs: a file that lists abbreviations and other problematic tokens
               that, because they include punctuation marks, can be  mistaken
               for a sentence ending. Optional.
    """
    def __init__(self, params):
        SentenceTokenizerWrapper.__init__(self, params)
        WordTokenizerWrapper.__init__(self, params)
        self.nt = NltkTools(tok=True, abbrev_set=self.abbrevs)

    def sen_tokenize(self, raw):
        """@note Does not use the abbrev_set."""
        sentences = self.nt.sen_tokenize(raw)
        self._join_sentences(sentences)
        return sentences

    def word_tokenize(self, sen):
        tokens = self.nt.wordTokenizer.tokenize(sen)
        if len(tokens) == 0:
            return []

        # Punctuation handling
        tokens = list(chain.from_iterable([w for w in remove_quot_and_wiki_crap_from_word(token)] for token in tokens))
        last_token, read_last = self.__get_last_token(tokens)
        punktMatchObject = self.nt.punktSplitter.match(tokens[last_token])
        if punktMatchObject is not None and not self._is_abbrev(tokens[last_token]):
            tokens = tokens[:last_token] + list(punktMatchObject.groups()) + read_last
        return tokens

    def __get_last_token(self, tokens):
        last_token = -1
        while len(tokens) > last_token * -1 and is_quote_or_garbage(tokens[last_token]):
            last_token -= 1
        read_last = tokens[last_token + 1:] if last_token != -1 else []
        return last_token, read_last

class HunknownSentenceTokenizer(SentenceTokenizerWrapper, LineByLineTagger):
    """
    The Java-based sentence tokenizer Eszter found in her hunpos directory.

    This class uses a modified version of the Tokenizer.java file that only
    performs sentence tokenization.

    Parameters:
    - hunknown_basedir: the directory of the hunknown "package";
    - hunknown_conf: the configuration file for the hunknown sentece tokenizer.
                     The default is ${hunknown_basedir}/huntools.conf;
    - hunknown_encoding: the encoding used by the hunknown program. Must agree
                         with the encoding parameter in the hunknown
                         configuration file. The default is iso-8859-2.
    """
    _datePattern = re.compile(r"(?:^|\s)(?:[\d]{2}){1,2}[.]$", re.UNICODE)
    _romanNumberPattern = re.compile(r"(?:^|\s)[IVXLCDM]+[.]$",
                                     re.UNICODE | re.IGNORECASE)
    _emptyLines = re.compile(ur"[\n\r]+")

    def __init__(self, params):
        SentenceTokenizerWrapper.__init__(self, params)
        self.patterns.add(HunknownSentenceTokenizer._datePattern)
        self.patterns.add(HunknownSentenceTokenizer._romanNumberPattern)

        basedir = params['hunknown_basedir']
        runnable = os.path.join(basedir, 'bin', 'tokenize')
        config  = params.get('hunknown_conf')
        if config is None:
            config = os.path.join(basedir, 'huntools.conf')
        encoding = params.get('hunknown_encoding', 'iso-8859-2')

        LineByLineTagger.__init__(self, runnable, encoding)
        self.options = [config]

    def sen_tokenize(self, raw):
        raw = HunknownSentenceTokenizer._emptyLines.sub("\n", raw.strip())
        if len(raw) == 0:
            return []
        # send_and_recv_lines puts a [] around the reply
        sentences = list(self.tag([raw + "\n"]))[0]
        self._join_sentences(sentences)
        return sentences

    def _join_condition(self, sentences, current):
        b = super(HunknownSentenceTokenizer, self)._join_condition(
                sentences, current)
        return b or HunknownSentenceTokenizer._romanNumberPattern.search(
                sentences[current]) is not None

    def recv_line(self):
        """Receives lineS from the process. The first line is always the number
        of consecutive lines."""
        ret = []
        num_lines = int(LineByLineTagger.recv_line(self))
        for i in xrange(num_lines):
            ret.append(LineByLineTagger.recv_line(self))
        return ret

