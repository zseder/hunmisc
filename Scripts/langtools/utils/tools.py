"""Defines classes that handle the various tools."""

from langtools.utils.huntools import Ocamorph, Hundisambig, MorphAnalyzer

class ToolWrapper(object):
    pass

class OcamorphWrapper(object):
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

