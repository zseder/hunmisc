from subprocess_wrapper import AbstractSubprocessClass

"""
TODO
- maybe a sentence, token, etc class hierarchy?
"""

class LineByLineTagger(AbstractSubprocessClass):
    def __init__(self, runnable, encoding):
        AbstractSubprocessClass.__init__(self, runnable, encoding)

    def send_line(self, line):
        self._process.stdin.write(line.encode(self._encoding) + "\n")

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
    ie. one token per line, attributes separated by tab,
    empty line on sentence end
    """
    def __init__(self, runnable, encoding, tag_index=-1):
        AbstractSubprocessClass.__init__(self, runnable, encoding)
        self._tag_index = tag_index

    def send(self, tokens):
        """
        send tokens to _process.stdin after encoding
        excepts only one sentence
        """
        self.tuple_mode = isinstance(tokens[0], tuple)
        for token in tokens:
            # differentiate between already tagged and raw tokens
            if self.tuple_mode:
                token_str = "\t".join(token)
            else:
                token_str = token
            token_to_send = token_str.encode(self._encoding)
            self._process.stdin.write(token_to_send)
            self._process.stdin.write("\n")
        self._process.stdin.write("\n")
        self._process.stdin.flush()

    def recv_and_append(self, tokens):
        tagged_tokens = []
        for token in tokens:
            line = self._process.stdout.readline()
            decoded = line.decode(self._encoding)
            tagged = decoded.strip().split("\t")
            if len(tagged) == 0:
                continue
            tag = tagged[self._tag_index]
            if self.tuple_mode:
                tagged_tokens.append(token + (tag,))
            else:
                tagged_tokens.append((token, tag))

        # is it last reading necessary?
        self._process.stdout.readline()

        return tagged_tokens
    
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
    def __init__(self, runnable, bin_model):
        LineByLineTagger.__init__(self, runnable, "latin-1")
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
        #tokens = set(tokens)
        return LineByLineTagger.tag(self, tokens)

class Hundisambig(SentenceTagger):
    def __init__(self, runnable, model, morphtable=None):
        SentenceTagger.__init__(self, runnable, "latin-1", 1)
        self._model = model
        self._morphtable = morphtable
        self.__set_default_options()

    def __set_default_options(self):
        o = []
        o += ["--morphtable", self._morphtable]
        o += ["--tagger-model", self._model]

        self.options = o
    
    def set_morphtable(self, mt):
        if self._closed:
            self._morphtable = mt
        else:
            raise Exception("morphtable can be changed only while not running")
        self.__set_default_options()

class MorphAnalyzer:
    def __init__(self, ocamorph, hundisambig):
        self._ocamorph = ocamorph
        self._hundisambig = hundisambig

    def analyze(self, data):
        from tempfile import NamedTemporaryFile
        morphtable_file = NamedTemporaryFile()
        morphtable_filename = morphtable_file.name
        tokens = [tok for sen in data for tok in sen]
        tagged = self._ocamorph.tag(tokens)
        for l in tagged:
            morphtable_file.write("\t".join(l).encode(self._hundisambig._encoding) + "\n")
        morphtable_file.flush()
        if not self._hundisambig._closed:
            self._hundisambig.stop()
        self._hundisambig.set_morphtable(morphtable_filename)
        self._hundisambig.start()
        for sen in data:
            yield self._hundisambig.tag_sentence(sen)
        morphtable_file.close()
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.__del__()

    def __del__(self):
        self._hundisambig.stop()
        self._ocamorph.stop()

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
    

