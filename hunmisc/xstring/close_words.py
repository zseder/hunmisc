import sys
from collections import defaultdict


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
        if len(src) > 1 or len(tgt) > 1:
            continue
        w = abs(float(w))
        d[src][tgt] = w

    return dict(d)


class CloseWordsGenerator(object):
    def __init__(self, correct_words, transmatrix=None, max_distance=2):
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

    def best_char_change(self, word, src_char, row):
        """returns best word(s) with changing @src_char and skips words
        already seen"""
        result = [-1, set()]
        for tgt, weight in row:
            # to deal with more changes having the same penalty, we have to
            # collect more results until there is an increase in weight
            if weight != result[0] and len(result[1]) > 0:
                break

            words = set(gen_changed(word, src_char, tgt))
            words -= set(self.seen.iterkeys())
            if len(words) > 0:
                result[0] = weight
                result[1] |= words
                for w in words:
                    self.seen[w] = (weight, self.seen[word][1] + 1)

        return result

    def get_closest(self, word):
        """Computes closesd word(s) based on stored transition matrix
        """
        t = self.transitions
        chars = set(word) | set([''])

        # call best_char_change (to skip already seen changes) on every char
        best = min((self.best_char_change(word, c, t[c])
                   for c in chars if (c in t and len(t[c]) > 0)),
                   key=lambda x: x[0])

        return best

    def __get_closest_for_seen(self):
        best = [None, set()]
        while len(best[1]) == 0:
            # stop if there is no possible changes
            if self.skip_first_n == len(self.seen):
                break

            word, (old_weight, old_dist) = sorted(self.seen.iteritems(),
                                      key=lambda x: x[1][1])[self.skip_first_n]

            # skip if old_word is already as far as it can be
            if old_dist == self.max_dist:
                self.skip_first_n += 1
                continue

            change_weight, new_words = self.get_closest(word)

            # @skip_first_n th word is done
            if len(new_words) == 0:
                self.skip_first_n += 1
                continue

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
        self.seen = {word: (0., 0)}
        self.skip_first_n = 0
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


def main():
    matrix_f = open(sys.argv[1])
    m = read_matrix(matrix_f)
    good_words = ["facebook", "britney"]
    cwg = CloseWordsGenerator(good_words, m)
    tests = ["facebok", "facbok"]
    for w in tests:
        print w, cwg.get_closest_correct(w)

if __name__ == "__main__":
    main()
