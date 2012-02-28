"""Defines classes that handle the various tools."""

from langtools.utils.huntools import Ocamorph, Hundisambig, MorphAnalyzer
from langtools.nltk.nltktools import NltkTools

class ToolWrapper(object):
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

class SentenceTokenizerWrapper(ToolWrapper):
    def sen_tokenize(self, raw):
        """Tokenizes the raw text into sentences."""
        pass

class WordTokenizerWrapper(ToolWrapper):
    def word_tokenize(self, sen):
        """Tokenizes the sentence into words."""
        pass

class OcamorphWrapper(PosTaggerWrapper, LemmatizerWrapper):
    """Wrapper class for ocamorph.

    This class requires the following parameters:
    - ocamorph_runnable: the ocamorph runnable;
    - ocamorph_model: the ocamorph model file;
    - ocamorph_encoding: the encoding used by the ocamorph and hundisambig
                         model files. The default is iso-8859-2;
    - hundisambig_runnable: the hundisambig runnable;
    - hundisambig_model: the hundisambig model file.

    @warning This determines the POS tag of the words as well as their lemmas
             in both the pos_tag() and the lemmatize() methods. To avoid adding
             adding the same fields twice, call only one of the methods; e.g.
             either specify OcamorphWrapper as a pos_tagger or a lemmatizer in
             the configuration file, but NOT BOTH."""
    def __init__(self, params):
        ocamorph = Ocamorph(params['ocamorph_runnable'],
                            params['ocamorph_model'],
                            params.get('ocamorph_encoding', 'iso-8859-2'))
        hundisambig = Hundisambig(params['hundisambig_runnable'],
                                  params['hundisambig_model'],
                                  params.get('ocamorph_encoding', 'iso-8859-2'))
        self.morph_analyzer = MorphAnalyzer(ocamorph, hundisambig)

    def add_pos_and_stems(self, tokens):
        """Adds POS tags and lemmatizes the words in @c tokens."""
        for sen_i, sen in enumerate(tokens):
            # TODO The API expects [sentences+], but it can only handle one :(
            ret = list(self.morph_analyzer.analyze([[word[0] for word in sen]]))[0]
            for tok_i, _ in enumerate(sen):
                spl = ret[tok_i][1].rsplit('|', 2)
                tokens[sen_i][tok_i].append(spl[2])
                tokens[sen_i][tok_i].append(spl[0])

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

