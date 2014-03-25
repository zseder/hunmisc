import sys
from collections import defaultdict

from sortedcollection import SortedCollection


def insert_char(word, char):
    for i in xrange(len(word) + 1):
        yield word[:i] + (char,) + word[i:]


def gen_changed(word, src_char, tgt_char):
    res = set()
    if src_char == "":
        res |= set(insert_char(word, tgt_char))
    else:
        prev = -1
        while True:
            try:
                i = word.index(src_char, prev + 1)
                new_w = word[:i] + (tgt_char,) + word[i + 1:]
                res.add(new_w)
                prev = i
            except ValueError:
                break

    return res


def read_matrix(istream):
    d = defaultdict(dict)
    for l in istream:
        le = l.split("\t")
        src, tgt, w = le
        #if len(src) > 1 or len(tgt) > 1:
        #    continue
        w = abs(float(w))
        d[src][tgt] = w

    return dict(d)


class CloseWordsGenerator(object):
    def __init__(self, correct_words, transmatrix=None, max_distance=3):
        self.__store_matrix(transmatrix)
        self.corrects = set(tuple(c for c in w) for w in correct_words)
        self.max_dist = max_distance

    def __store_matrix(self, m):
        """stores every row of the matrix in weighted order
        """
        chars = set(m.iterkeys())
        for inner_d in m.itervalues():
            chars |= set(inner_d.itervalues())
        d = {}
        for c1, row in m.iteritems():
            values = [(c2, w) for c2, w in row.iteritems() if w > 1e-10]
            d[c1] = sorted(values, key=lambda x: x[1])
        self.transitions = d

    def get_char_changes(self, word, src_char):
        row = self.transitions[src_char]
        values = []
        for tgt, weight in row:
            new_words = set(gen_changed(word, src_char, tgt))
            values.append((weight, new_words))
        return sorted(values, key=lambda x: x[0])

    def get_closest(self, word):
        """Computes closest word(s) based on stored transition matrix
        """
        t = self.transitions
        chars = set(word) | set([''])

        if word not in self.change_cache:
            self.change_cache[word] = []
            for c in chars:
                if c not in t or len(t[c]) == 0:
                    continue

                self.change_cache[word] += self.get_char_changes(word, c)

        if len(self.change_cache[word]) == 0:
            del self.change_cache[word]
            return None

        return self.change_cache[word].pop(0)

    def choose_next(self):
        if len(self.not_done) == 0:
            return

        return self.not_done[0]

    def __get_closest_for_seen(self):
        best = [None, set()]
        while len(best[1]) == 0:
            n = self.choose_next()
            if n is None:
                break

            word, (old_weight, old_dist) = n
            # skip if old_word is already as far as it can be
            if old_dist == self.max_dist:
                self.done.add(word)
                self.not_done.remove(self.not_done[0])
                continue

            cl = self.get_closest(word)
            if cl is None:
                self.done.add(word)
                self.not_done.remove(self.not_done[0])
                continue

            change_weight, new_words = cl

            new_weight = old_weight + change_weight
            if best[0] is None:
                best[0] = (new_weight, old_dist + 1)
                best[1] = new_words
            elif new_weight < best[0][0]:
                best[0] = (new_weight, old_dist + 1)
                best[1] = new_words
            elif new_weight == best[0][0]:
                best[1] |= new_words
        return best

    def get_closest_correct(self, word):
        word = tuple(c for c in word)

        # caching variables for speedup
        self.seen = {word: (0., 0)}
        self.change_cache = {}
        self.done = set()
        self.not_done = SortedCollection(key=lambda x: x[1][0])
        self.not_done.insert(self.seen.items()[0])

        while True:
            new_value, new_words = self.__get_closest_for_seen()
            if len(new_words) == 0:
                return None

            correct_words = new_words & self.corrects
            if len(correct_words) > 0:
                return correct_words

            for w in new_words:
                if w not in self.seen:
                    self.seen[w] = new_value
                    self.not_done.insert((w, new_value))


def main():
    matrix_f = open(sys.argv[1])
    m = read_matrix(matrix_f)
    good_words = ["facebook", "britney"]
    cwg = CloseWordsGenerator(good_words, m)
    tests = ["faremook"]
    for w in tests:
        print w, cwg.get_closest_correct(w)

if __name__ == "__main__":
    main()
