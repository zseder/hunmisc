import re
from subprocess_wrapper import AbstractSubprocessClass
from langtools.utils.misc import ispunct, isquot, print_logging

"""
TODO
- maybe a sentence, token, etc class hierarchy?
"""

class LineByLineTagger(AbstractSubprocessClass):
    def __init__(self, runnable, encoding):
        AbstractSubprocessClass.__init__(self, runnable, encoding)

    def send_line(self, line):
        self._process.stdin.write(line.encode(self._encoding, 'xmlcharrefreplace') + "\n")

    def recv_line(self):
        return self._process.stdout.readline().strip().decode(self._encoding)

    def send_and_recv_lines(self, lines):
        for line in lines:
            self.send_line(line)
            self._process.stdin.flush()
            yield self.recv_line()

    def tag(self, lines):
        if self._closed:
            self.start()
        return self.send_and_recv_lines(lines)

class SentenceTagger(AbstractSubprocessClass):
    """
    Tags sentence by sentence in conll format
    ie. one token per line, attributes separated by tab (or @sep),
    empty line on sentence end
    """
    def __init__(self, runnable, encoding, tag_index=-1, sep="\t", isep="\t", osep="\t"):
        AbstractSubprocessClass.__init__(self, runnable, encoding)
        self._tag_index = tag_index
        self.sep = sep
        self.isep = sep
        self.osep = sep
        self.isep = isep
        self.osep = osep
        
    def send(self, tokens):
        """
        send tokens to _process.stdin after encoding
        excepts only one sentence
        """
        self.tuple_mode = isinstance(tokens[0], tuple)
        try:
            for token in tokens:
                # differentiate between already tagged and raw tokens
                if self.tuple_mode:
                    token_str = self.isep.join(token)
                else:
                    token_str = token
                token_to_send = self.encode(token_str)
#                print "WRITING", token_str.encode('utf-8')
#                import sys
#                sys.stdout.flush()
                self._process.stdin.write(token_to_send)
                self._process.stdin.write("\n")
            self._process.stdin.write("\n")
            self._process.stdin.flush()
        except IOError, ioe:
            print "ERROR: ", str(ioe)
            print self._process.stderr.readline()
            raise ioe

    def getStdErr(self):
        print self._process.stderr.readlines()
    
    def recv_and_append(self, tokens):
        tagged_tokens = []
        for token in tokens:
            line = self._process.stdout.readline()
            if line.startswith('Accuracy ='):
                line = self._process.stdout.readline()
            #print list(line)
            if line == '\n' or line == '':
                continue
            decoded = self.decode(line)
            tagged = decoded.strip().split(self.osep)
            if len(tagged) == 0:
                continue
            #print tagged
            tag = tagged[self._tag_index]
            if self.tuple_mode:
                tagged_tokens.append(token + (tag,))
            else:
                tagged_tokens.append((token, tag))

        # is it last reading necessary?
        self._process.stdout.readline()

        return tagged_tokens

    def encode(self, token):
        """Encodes @p token before it is sent to the tagger."""
        return token.encode(self._encoding, 'xmlcharrefreplace')
    
    def decode(self, line):
        """Decodes @p line before it is returned."""
        return line.decode(self._encoding).strip()
    
    def tag_sentence(self, tokens):
        if self._closed:
            self.start()

        self.send(tokens)
        result = self.recv_and_append(tokens)
        return result

    def tag_sentences(self, sentences):
        for sentence in sentences:
            yield self.tag_sentence(sentence)

class Ocamorph(LineByLineTagger):
    def __init__(self, runnable, bin_model, encoding="LATIN2"):
        LineByLineTagger.__init__(self, runnable, encoding)
        self._bin_model = bin_model
        self.__set_default_options()

    def recv_line(self):
        data = LineByLineTagger.recv_line(self)
        return tuple(data.strip().split("\t"))

    def __set_default_options(self):
        o = []
        o += ["--bin", self._bin_model]
        o += ["--tag_preamble", ""]
        o += ["--tag_sep", "\t"]
        o += ["--guess", "Fallback"]
        o.append("--blocking")

        self.options = o
        
    def override_options(self):
        raise NotImplementedError()
    
    def set_blocking(self, bl=True):
        if bl:
            self.options[8] = "--blocking"
        else:
            del self.options[8]

    def tag(self, tokens):
        tokens = set(tokens)
        return LineByLineTagger.tag(self, tokens)

class Hundisambig(SentenceTagger):
    def __init__(self, runnable, model, morphtable=None, encoding="LATIN2", load=False):
        SentenceTagger.__init__(self, runnable, encoding, 1)
        self._model = model
        self._morph_set = None
        self._unknown = None
        self._noun = None
        self.set_morphtable(morphtable, load)
        self.__set_default_options()

    def __set_default_options(self):
        o = []
        o += ["--morphtable", self._morphtable]
        o += ["--tagger-model", self._model]
        o += ["--decompounding", "no"]  # Let's not bother with decompounding

        self.options = o
    
    def set_morphtable(self, mt, load=False):
        if self._closed:
            self._morphtable = mt
            if mt is None or not load:
                self._morph_set = None
            else:
                self._morph_set = set()
                with open(self._morphtable) as infile:
                    for line in infile:
                        try:
                            token, analysis = line.strip().split("\t", 1)
                        except ValueError:
                            continue
                        self._morph_set.add(token)
                        if self._unknown is None and 'UNKNOWN' in analysis:
                                self._unknown = token
                        if self._noun is None and 'NOUN' in analysis:
                                self._noun = token
        else:
            raise Exception("morphtable can be changed only while not running")
        self.__set_default_options()

    def encode(self, token):
        """Encodes @p token before it is sent to the tagger. Note: this encoding
        cannot be undone via decode(); if the original tokens are still needed,
        the caller must ensure that they are retained."""
        token_to_send = token.encode(self._encoding, 'xmlcharrefreplace')
        if self._morph_set is not None:
            if token_to_send not in self._morph_set:
                if self._unknown is not None:
                    token_to_send = self._unknown
                    print_logging(u"REPLACED " + token + u" WITH UNK " + token_to_send.decode(self._encoding))
                elif self._noun is not None:
                    token_to_send = self._noun
                    print_logging(u"REPLACED " + token + u" WITH NOUN " + token_to_send.decode(self._encoding))
                # else: no noun; the morphtable must be unusable anyway
        return token_to_send
    
class MorphAnalyzer:
    UNICODE_PATTERN = re.compile(ur"&#(\d+);")
    NUMBER_PATTERN = re.compile(ur"(\d+|[IVXLCDM]+)[.]", re.IGNORECASE)

    def __init__(self, ocamorph, hundisambig):
        self._ocamorph = ocamorph
        self._hundisambig = hundisambig

    def analyze(self, data):
        from tempfile import NamedTemporaryFile
        safe_data = [[self.replace_stuff(tok) for tok in sen] for sen in data]
        with NamedTemporaryFile() as morphtable_file:
            morphtable_filename = morphtable_file.name
            tokens = [tok for sen in safe_data for tok in sen]
            tagged = self._ocamorph.tag(tokens)
            for l in tagged:
                morphtable_file.write(u"\t".join(l).encode(self._hundisambig._encoding, 'xmlcharrefreplace') + "\n")
            morphtable_file.flush()
            if not self._hundisambig._closed:
                self._hundisambig.stop()
            self._hundisambig.set_morphtable(morphtable_filename)
            self._hundisambig.start()

            for sen_i, sen in enumerate(safe_data):
                ret = self._hundisambig.tag_sentence(sen)
                yield [self.correct(token, data[sen_i][i]) for i, token in enumerate(ret)]

            # BUGTEST
            import shutil
            shutil.copy(morphtable_file.name, 'aa')

    def replace_stuff(self, token):
        t = self.replace_punct(token)
        t = self.replace_num(t)
        t = self.remove_pipes(t)
        if len(t) == 0:
            t = u'/'
        return t

    def replace_punct(self, token):
        """Replaces unicode punctuation marks with ones understood by
        ocamorph."""
        try:
            if ispunct(token):
                token.encode(self._hundisambig._encoding)
            return token
        except UnicodeError:
            if isquot(token):
                return '"'
            else:
                return ','

    def replace_num(self, token):
        """Strips the '.' from the end of a number token, so that ocamorph
        correctly tags it as NUM."""
        m = MorphAnalyzer.NUMBER_PATTERN.match(token)
        return m.group(1) if m is not None else token

    def remove_pipes(self, token):
        return token.replace(u'|', u'')

    def correct(self, analysis, original):
        """Inverts the xmlcharreplacements in the lemma, as well as
        replace_punct for unicode punctuation marks."""
        word, crap = analysis
#        print "AAA", original.encode('utf-8'), word.encode('utf-8'), crap.encode('utf-8')
        if original == u'|':
            return (word, original + u'||PUNCT')
        try:
            lemma, stuff, derivation = crap.split('|')

            # If the original is a punctuation mark, tag it as such to avoid
            # problems with |, etc. Also, we include the original character,
            # not the one possibly replaced by replace_punct.
            if ispunct(original):
                return (word, original + u'||PUNCT')

            # Word not in the morphtable, or POS tag could not be determined.
            if crap == u'unknown||':
                lemma = word
                derivation = u'UNKNOWN'

            pieces = MorphAnalyzer.UNICODE_PATTERN.split(lemma)
            if len(pieces) > 1:
                for i in xrange(1, len(pieces), 2):
                    pieces[i] = unichr(int(pieces[i]))
                lemma = u''.join(pieces)

            if len(derivation) == 0:
                parts = lemma.rsplit('?', 1)
                if len(parts) >= 2:
                    lemma = parts[0]
                    derivation = parts[1].rsplit('/', 1)[-1].upper()
            return (word, lemma + u'|' + stuff + u'|' + derivation)
        except ValueError, ve:
            print_logging(ve)
            print_logging(word + u" // " + crap)
            raise ve

    def __exit__(self, exc_type, exc_value, traceback):
        self.__del__()

    def __del__(self):
        if self._hundisambig is not None:
            self._hundisambig.stop()
            self._hundisambig = None
        if self._ocamorph is not None:
            self._ocamorph.stop()
            self._ocamorph = None

class HundisambigAnalyzer(MorphAnalyzer):
    """"""
    def __init__(self, hundisambig):
        MorphAnalyzer.__init__(self, None, hundisambig)
        self._hundisambig.start()

    def analyze(self, data):
        safe_data = [[self.replace_stuff(tok) for tok in sen] for sen in data]
        for sen_i, sen in enumerate(safe_data):
            ret = self._hundisambig.tag_sentence(sen)
            yield [self.correct(token, data[sen_i][i]) for i, token in enumerate(ret)]

class Hunchunk(SentenceTagger):
    def __init__(self, huntag, modelName, bigramModel, configFile, encoding="LATIN2"):
        SentenceTagger.__init__(self, "python", encoding, 2)
        self.huntag = huntag
        self.modelName = modelName
        self.bigramModel = bigramModel
        self.configFile = configFile
        self.__set_default_options()
        self.start()

    def __set_default_options(self):
        o = [self.huntag]
        o += ["tag"]
        o += ["-m", self.modelName]
        o += ["-b", self.bigramModel]
        o += ["-l 1"]
        o += ["-c", self.configFile]
        self.options = o


if __name__ == "__main__":
    o = Ocamorph("/home/zseder/Proj/huntools/ocamorph-1.1-linux/ocamorph",
                 "/home/zseder/Proj/huntools/ocamorph-1.1-linux/morphdb.hu/morphdb_hu.bin")
    h = Hundisambig("/home/recski/sandbox/hundisambig_compact/hundisambig",
                   "/home/recski/sandbox/hundisambig_compact/hu_szeged.model")
    a = MorphAnalyzer(o, h)
    tagged = a.analyze([["tedd", "a", "piros", "kekszet", "a", "fekete", "fejre","."],
                       ["de", "ne", "most", "!"]])
    tagged = list(tagged)
    print tagged
    

