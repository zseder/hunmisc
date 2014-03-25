class UnigramCorrector():

    def __init__(self, correct_cache={}, corrections_cache={}):

        self.correct_cache = correct_cache
        self.corrections_cache = corrections_cache

    def check_word(self, word):

        return word in self.correct_cache
    
    def correct_word(self, word):

        if word in self.correct_cache:
            return word
        return self.corrections_cache.get(word, word)
