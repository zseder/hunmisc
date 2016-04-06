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


from itertools import izip_longest
import logging
import re
import signal
import sys

from subprocess_wrapper import AbstractSubprocessClass
from hunmisc.xstring.xstring import ispunct, isquot
from hunmisc.corpustools.bie1_tools import parse_bie1_sentence

"""
TODO
- maybe a sentence, token, etc class hierarchy?
"""

class Alarm(Exception):
    """To implement timeout in hunspell"""

def alarm_handler(signum, frame):
    raise Alarm

class LineByLineTagger(AbstractSubprocessClass):
    def __init__(self, runnable, encoding, options=None):
        AbstractSubprocessClass.__init__(self, runnable, encoding, options)

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
    def __init__(self, runnable, encoding, tag_index=-1, sep="\t", isep="\t", osep="\t", chunk_field=None):
        AbstractSubprocessClass.__init__(self, runnable, encoding)
        self._tag_index = tag_index
        self.sep = sep
        self.isep = sep
        self.osep = sep
        self.isep = isep
        self.osep = osep
        if chunk_field is None:
            self.chunk_mode = False
        else:
            self.chunk_mode = True
            self.chunk_field = chunk_field

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
                self._process.stdin.write(token_to_send)
                self._process.stdin.write("\n")
            self._process.stdin.write("\n")
            self._process.stdin.flush()
        except IOError, ioe:
            logging.error(str(ioe))
            logging.error(self._process.stderr.readline())
            raise ioe

    def get_std_err(self):
        return self._process.stderr.readlines()

    def recv_and_append(self, tokens):
        tagged_tokens = []
        for token in tokens:
            line = self._process.stdout.readline()
            if line.startswith("Accuracy"):
                line = self._process.stdout.readline()

            decoded = self.decode(line)
            tagged = decoded.strip().split(self.osep)

            if len(tagged) == 0 or len(decoded.strip()) == 0:
                continue

            tag = tagged[self._tag_index]
            if self.tuple_mode:
                tagged_tokens.append(token + (tag,))
            else:
                tagged_tokens.append((token, tag))

        # is it last reading necessary?
        self._process.stdout.readline()

        if self.chunk_mode:
            return parse_bie1_sentence(tagged_tokens, self.chunk_field)
        else:
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
                    logging.debug(u"REPLACED " + token + u" WITH UNK " + token_to_send.decode(self._encoding))
                elif self._noun is not None:
                    token_to_send = self._noun
                    logging.debug(u"REPLACED " + token + u" WITH NOUN " + token_to_send.decode(self._encoding))
                # else: no noun; the morphtable must be unusable anyway
        return token_to_send

class MorphAnalyzer(object):
    UNICODE_PATTERN = re.compile(ur"&#(\d+);")
    NUMBER_PATTERN = re.compile(ur"(\d+|[IVXLCDM]+)[.]", re.IGNORECASE)

    def __init__(self, ocamorph, hundisambig):
        self._ocamorph = ocamorph
        self._hundisambig = hundisambig
        self._encoding = ocamorph._encoding if ocamorph is not None else hundisambig._encoding

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

#            # BUGTEST
#            import shutil
#            shutil.copy(morphtable_file.name, 'aa')

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
                token.encode(self._encoding)
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
            logging.debug(ve)
            logging.debug(word + u" // " + crap)
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

class OcamorphAnalyzer(MorphAnalyzer):
    """"""
    def __init__(self, ocamorph):
        MorphAnalyzer.__init__(self, ocamorph, None)

    def analyze(self, data):
        safe_data = [[self.replace_stuff(tok) for tok in sen] for sen in data]
        for sen_i, sen in enumerate(safe_data):
            ret = self._ocamorph.tag(sen)
            yield ret

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
    def __init__(self, huntag, modelName, bigramModel, configFile, encoding="LATIN2", chunk_field=-1):
        SentenceTagger.__init__(self, "python", encoding, chunk_field, chunk_field=chunk_field)
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

class Hunspell(AbstractSubprocessClass):
    """wrapper for hunspell run by -a option
    result is a list of codes, see the codes below this description
    Example usage:
        Analyzing:
        >>> from hunmisc.utils.huntool_wrapper import Hunspell
        >>> h = Hunspell(path_to_hunspell, path_to_dict_without_extension,
                        mode="analyze")
        >>> h.start()
        >>> h.analyze("Ich habe keine hausaufgabe")
        [0, 0, 0, 3]

        Stemming:
        >>> from hunmisc.utils.huntool_wrapper import Hunspell
        >>> h = Hunspell(path_to_hunspell, path_to_dict_without_extension)
        >>> h.start()
        >>> h.stem("asztalokkal")
        u'asztal'

    """

    stem_err_msg = "hunspell is blocking while using -s function because of" \
                   " buffering. Modify pipe_interface() method in " \
                   "hunspell.cxx with fflush() stdout while stemming to make " \
                   "this work.\n"

    MATCH = 0
    AFFIX = 1
    COMPOUND = 2
    SUGGEST = 3
    INCORRECT = 4
    EMPTY = 5
    TIMEOUT = 6

    def __init__(self, runnable, dictpath, mode="stem"):
        encoding = self.__get_encoding(dictpath)
        AbstractSubprocessClass.__init__(self, runnable, encoding)
        o = []
        self.mode = mode
        if mode == "stem":
            o += ["-s"]
        elif mode == "analyze":
            o += ["-a"]
        o += ["-d",  dictpath]
        o += ["-i",  encoding]
        self.options = o

    def __get_encoding(self, dictpath):
        affpath = dictpath + ".aff"
        with open(affpath) as aff_f:
            for line in aff_f:
                l = line.strip()
                if l.startswith("SET "):
                    encoding = l.split(" ", 1)[1]
                    return encoding
        # no encoding, assuming UTF-8?
        return "UTF-8"

    def start(self):
        AbstractSubprocessClass.start(self)
        signal.signal(signal.SIGALRM, alarm_handler)
        if self.mode == "analyze":
            # useless status line printed to stdout...
            self._process.stdout.readline()
        if self.mode == "stem":
            try:
                self._process.stdin.write("a\n")
                self._process.stdin.flush()

                signal.alarm(5)
                self.a_line = self._process.stdout.readline()
                self._process.stdout.readline()
                signal.alarm(0)
            except Alarm:
                raise Exception(Hunspell.stem_err_msg)
        self.stuck = False

    def check(self, text):
        words = text.split(" ")
        return reduce(lambda x, y: x + y,
                      [self.check_word(word) for word in words])

    def check_word(self, word):
        new_res = []
        for res in self.process_word(word):
            print res
            r = res.strip()
            if len(r) == 0:
                continue
            if r.split() > 1:
                new_res.append(Hunspell.MATCH)
            else:
                new_res.append(Hunspell.INCORRECT)
        return new_res

    def choose_stem(self, stems):
        return sorted([s for s in stems], key=lambda x: len(x))[0]

    def clear_process_output(self):
        while True:
            self._process.stdin.write("a\n")
            self._process.stdin.flush()
            signal.setitimer(signal.ITIMER_REAL, 0.05, 0)
            try:
                res_line = self._process.stdout.readline()
                sys.stderr.write(repr(res_line))
                if res_line == self.a_line:
                    self.stuck = False
                    # final empty after a
                    self._process.stdout.readline()
                    sys.stderr.write("Stuck cleared.\n")
                    signal.setitimer(signal.ITIMER_REAL, 0, 0)
                    break
            except Alarm:
                pass

    def stem_word(self, word):
        try:
            to_send = word.encode(self._encoding)
        except UnicodeEncodeError:
            return word

        if self.stuck:
            self.clear_process_output()

        signal.setitimer(signal.ITIMER_REAL, 0.25, 0)
        try:
            stems = []
            self._process.stdin.write(to_send + "\n")
            self._process.stdin.flush()
            have_final_results = False

            while True:
                res_line = self._process.stdout.readline().strip().decode(
                    self._encoding)
                if len(res_line) == 0:
                    if have_final_results:
                        signal.setitimer(signal.ITIMER_REAL, 0, 0)
                        if len(stems) == 0:
                            return word
                        else:
                            return self.choose_stem(stems)

                if len(res_line.split()) == 2:
                    root, stem = tuple(res_line.split())
                    if root == word[-len(root):]:
                        have_final_results = True
                else:
                    stem = res_line
                    if stem == word[-len(stem):]:
                        have_final_results = True
                stems.append(stem)
        except Alarm:
            msgu = u"hunspell timeout at word {0}\n".format(word)
            sys.stderr.write(msgu.encode("utf-8"))
            self.stuck = True
            return word

    def analyze(self, text):
        words = text.split(" ")
        res = reduce(lambda x, y: x + y,
                     [list(self.process_word(word)) for word in words])
        new_res = []
        for r in res:
            if len(r.strip()) == 0:
                new_res.append(Hunspell.EMPTY)

            if r == "*":
                new_res.append(Hunspell.MATCH)
            elif r[0] == "+":
                new_res.append(Hunspell.AFFIX)
            elif r[0] == "-":
                new_res.append(Hunspell.COMPOUND)
            elif r[0] == "&":
                new_res.append(Hunspell.SUGGEST)
            elif r[0] == "#":
                new_res.append(Hunspell.INCORRECT)
        return new_res

    def process_word(self, word):
        self._process.stdin.write("\n" + word.encode(self._encoding) + "\n")
        self._process.stdin.flush()

        # timeout with one second
        signal.alarm(1)
        try:
            res_line = self._process.stdout.readline().strip().decode(
                self._encoding)
            signal.alarm(0)
        except Alarm:
            yield Hunspell.TIMEOUT
            return
        while res_line:
            yield res_line
            try:
                signal.alarm(1)
                res_line = self._process.stdout.readline().strip().decode(
                    self._encoding)
                signal.alarm(0)
            except Alarm:
                yield Hunspell.TIMEOUT
                return

class SFSTAnalyzer(LineByLineTagger):
    """
    Wraps the SFST executable fst-infl2 (there is pysfst, but
      1. this is an alternative,
      2. it didn't install for me).

    Returns the possible analyses of a word as a list. Returns [] if none is
    found.
    """
    def __init__(self, model, runnable='fst-infl2', encoding='utf-8'):
        """Note: model should be a compressed FST (.ca)."""
        LineByLineTagger.__init__(self, runnable, encoding,
                                  ['-s', '-delim', "\t", model])

    def recv_line(self):
        return super(SFSTAnalyzer, self).recv_line().strip().split("\t")[1:]

class HFSTAnalyzer(LineByLineTagger):
    """
    Wraps the HFST executable -- in case one doesn't want to install the Python
    packages (not available in Pypi), only as Debian packages...

    This code uses the Apertium output format, weights included, as that is the
    one that fits on a line. An empty list is returned for words without
    any analysis.
    """
    def __init__(self, model, runnable='hfst-proc', encoding='utf-8',
                 weights=True):
        """
        @param weights if @c True (the default), recv_line (and therefore tag)
                       returns a list of (analysis, weight) tuples, not just
                       the analyses.
        """
        LineByLineTagger.__init__(self, runnable, encoding, ['-pW', model])
        self.weights = weights
        self.linep = re.compile(r'[\^][^/]+/([^$]+)[$]')
        self.delimp = re.compile(r'~([^~]+)~(?:/|$)')

    def send_line(self, line):
        super(HFSTAnalyzer, self).send_line(line)
        super(HFSTAnalyzer, self).send_line('')

    def recv_line(self):
        line = super(HFSTAnalyzer, self).recv_line()
        while not line:
            # Throw away empty line before 2nd & up requests
            line = super(HFSTAnalyzer, self).recv_line()
        lst = self.delimp.split(self.linep.search(line).group(1))[:-1]
        if self.weights:
            return [(a, float(w)) for a, w in izip_longest(*[iter(lst)] * 2)]
        else:
            return lst[::2]

if __name__ == "__main__":
    o = Ocamorph("/home/zseder/Proj/huntools/ocamorph-1.1-linux/ocamorph",
                 "/home/zseder/Proj/huntools/ocamorph-1.1-linux/morphdb.hu/morphdb_hu.bin")
    h = Hundisambig("/home/recski/sandbox/hundisambig_compact/hundisambig",
                    "/home/recski/sandbox/hundisambig_compact/hu_szeged.model")
    a = MorphAnalyzer(o, h)
    tagged = a.analyze([["tedd", "a", "piros", "kekszet", "a", "fekete",
                         "fejre", "."],
                        ["de", "ne", "most", "!"]])
    tagged = list(tagged)
    print tagged
