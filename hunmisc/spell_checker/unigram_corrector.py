import dawg
import cPickle


class UnigramCorrector():

    def __init__(self, correct_cache={}, corrections_cache={},
                 corrections_list=[]):

        self.correct_cache = correct_cache
        self.correction_indeces_cache = corrections_cache
        self.corrections_list = corrections_list

    def load_dawg_caches(self, correct_cache_fn, correction_indeces_fn,
                        corrections_list_fn):

        self.correct_cache = dawg.DAWG().load(correct_cache_fn)
        self.correction_indeces_cache = \
                dawg.IntDAWG().load(correction_indeces_fn)
        self.corrections_list = cPickle.load(open(corrections_list_fn))

    def check_word(self, word):

        return word in self.correct_cache

    def correct_word(self, word):

        if word in self.correct_cache:
            return word
        if word in self.correction_indeces_cache:
            index = self.correction_indeces_cache[word]
            return self.corrections_list[index]
        return word
