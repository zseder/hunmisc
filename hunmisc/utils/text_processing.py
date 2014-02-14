"""
General text processing tool, using nltk.PunctTokenizertokenizer
(word and sentence) and -s mode of Hunspell, these can be varied.
Currently functions for processing wikipedia (lines starting with "%%#PAGE
are not processed") and bible (+_TAG_ + '\t' + _LINE_TO_PROCESS_) are written, 
easily extandable for other text inputs.
"""

from hunmisc.utils.huntool_wrapper import Hunspell
from hunmisc.nltk.nltktools import NltkTools 

import os
import sys
import re
import cPickle

class Hunspell_chache_aimed(object):
        
    def __init__(self, runnable, path, cache_file, only_alpha=False):
        
        self.hunspell = Hunspell(runnable, path)
        self._cache_file = cache_file
        self.cached_words = {}
        if cache_file != None:
            self.read_cache()
        self.only_alpha = only_alpha
        if self.only_alpha is True:
            self.alpha_matcher = re.compile("[^\W\d_]+", re.UNICODE)
        self.hunspell.start()
        
    def read_cache(self):
        
        if not os.path.exists(self._cache_file):
            return 
        for l_utf in open(self._cache_file):
            l = l_utf.strip().decode('utf-8')
            if len(l.split(' ')) == 1:
                self.cached_words[l] = l
            if len(l.split(' ')) == 2:
                orig, stemmed = l.split(' ')
                self.cached_words[orig] = stemmed

    def write_cache(self):
        
        with open(self._cache_file, "w") as f:
            for tok in self.cached_words:
                print 4655555555555555555555
                f.write(u'{0} {1}\n'.format(tok,
                              self.cached_words[tok]).encode('utf-8'))

    def cached_stem(self, word):

        if self.only_alpha is True:
            if self.alpha_matcher.match(word) == None or\
            self.alpha_matcher.match(word).group() != word:
                return word
        if word in self.cached_words:
            return self.cached_words[word]
        stem = self.hunspell.stem_word(word)
        self.cached_words[word] = stem
        return stem
   
def get_lang_spec_path(language, info_file):
    info_file = open(info_file)
    for l in info_file:
        lang = l.split('\t')[0]
        if lang == language:
            return l.strip().split('\t')[1]

def stem(text, hs):
    return [ hs.cached_stem(tok) for line in text for tok in line.strip().split(' ')]

def process_text(text, todo):

    for function in todo:
        text = function(text)

    return text  

def process_wp(stream, todo):

    wp_page = ''
    for line in stream:
        if line.startswith('%%#PAGE'):
            print process_text(wp_page, todo).encode('utf-8')
            wp_page = ''
            print line.strip()
        else:
            wp_page += line.decode('utf-8')

    print process_text(wp_page, todo).encode('utf-8')

def get_tools(language, hunspell_path, hunspell_path_infos, cache):

    aff_dict_path = get_lang_spec_path(language, hunspell_path_infos)
    hs = Hunspell_chache_aimed(hunspell_path, aff_dict_path, cache, only_alpha=True)
    tokenizer = NltkTools(tok=True,\
       stok_model=cPickle.load(open('/mnt/ihlt/Proj/dictbuild/nltk_tokenizers/' + language)))

    return hs, tokenizer

def process_bible(stream, hs, tokenizer):

    for line in stream:
        parts = line.decode('utf-8').strip().split('\t')
        if len(parts) == 2:
            tag = parts[0]
            stemmed_sens = []
            for sen in process_text(parts[1], tokenizer, hs):
                stemmed_sens.append(sen)
            print "{0}\t{1}".format(tag, ' '.join(stemmed_sens)).encode('utf-8')    


def main():


    language = sys.argv[1]
    hunspell_path = sys.argv[2]
    hunspell_path_infos = sys.argv[3]
    cache_file = sys.argv[4]
    hs, tokenizer = get_tools(language, hunspell_path, hunspell_path_infos, cache_file)
    hs.read_cache()
    todo =         [lambda x: "\n".join(tokenizer.sen_tokenize(x)), 
                    lambda x: "\n".join([' '.join(tokenizer.word_tokenize(line)) for line in x.split('\n')]), 
                    lambda x: "\n".join([' '.join([hs.cached_stem(w) for w in l.strip().split(' ')]) for l in x.split('\n')]) ] 

    process_wp(sys.stdin, todo)
    print repr(hs.cached_words)
    hs.write_cache()

if __name__ == "__main__":
    main()
