"""
General text processing tool, using nltk.PunctTokenizertokenizer
(word and sentence) and -s mode of Hunspell, these can be varied.
Currently functions for processing wikipedia (lines starting with "%%#PAGE
are not processed") and bible (+_TAG_ + '\t' + _LINE_TO_PROCESS_) are written, 
easily extandable for other text inputs.
"""

from hunmisc.utils.huntool_wrapper import Hunspell
from hunmisc.nltk.nltktools import NltkTools 

import sys
import re
import cPickle

class Hunspell_chache_aimed(object):
        
    def __init__(self, runnable, path, cache_file, only_alpha=False):
        
        self.hunspell = Hunspell(runnable, path)
        self._cache = open(cache_file, 'a+')
        self.cached_words = {}
        if cache_file != None:
            self.read_cache()
        self.new_cached_words = {}    
        self.only_alpha = only_alpha
        if self.only_alpha is True:
            self.alpha_matcher = re.compile("[^\W\d_]+", re.UNICODE)
        print "{0} {1} {2} {3}".format(runnable, path, cache_file, only_alpha)
        self.hunspell.start()
        
    def read_cache(self):
        
        for l_utf in self._cache:
            l = l_utf.strip().decode('utf-8')
            if len(l.split(' ')) == 1:
                self.cached_words[l] = l
            if len(l.split(' ')) == 2:
                orig, stemmed = l.split(' ')
                self.cached_words[orig] = stemmed

    def write_cache(self):

        for tok in self.new_cached_words:
            self._cache.write(u'{0} {1}\n'.format(tok,
                              self.new_cached_words[tok]).encode('utf-8'))

    def cached_stem(self, word):

        if self.only_alpha is True:
            if self.alpha_matcher.match(word) == None or\
            self.alpha_matcher.match(word).group() != word:
                return word
        if word in self.cached_words:
            return self.cached_words[word]
        sys.stderr.write(word.encode('utf-8') + '\n')
        stem = self.hunspell.stem_word(word)
        self.hunspell._process.stdout.flush()
        self.cached_words[word] = stem
        self.new_cached_words[word] = stem
        return stem
   
def get_lang_spec_path(language, info_file):
    info_file = open(info_file)
    for l in info_file:
        lang = l.split('\t')[0]
        if lang == language:
            return l.strip().split('\t')[1]

def stem_line(line, hs):
    return ' '.join([ hs.cached_stem(tok) for tok in line.strip().split(' ') ])


def process_text(text, tokenizer, hs):
    for tokenized_sen in tokenizer.tokenize(text.decode('utf-8')):
        stemmed_sen = stem_line(' '.join(tokenized_sen), hs)
        yield stemmed_sen.encode('utf-8')

def process_wp(stream, hs, tokenizer):

    wp_page = ''
    for line in stream:
        if line.startswith('%%#PAGE'):
            for processed_sen in process_text(wp_page, tokenizer, hs):
                print processed_sen
            wp_page = ''
            print line.strip()
        else:
            wp_page += line

    for processed_sen in process_text(wp_page, tokenizer, hs):
        print processed_sen 


def get_tools(language, hunspell_path, hunspell_path_infos, cache):

    aff_dict_path = get_lang_spec_path(language, hunspell_path_infos)
    hs = Hunspell_chache_aimed(hunspell_path, aff_dict_path, cache, only_alpha=True)
    tokenizer = NltkTools(tok=True,\
       stok_model=cPickle.load(open('/mnt/ihlt/Proj/dictbuild/nltk_tokenizers/' + language)))

    return hs, tokenizer


def process_bible(stream, hs, tokenizer):

    for line in stream:
        parts = line.strip().split('\t')
        if len(parts) == 2:
            tag = parts[0]
            stemmed_sens = []
            for sen in process_text(parts[1], tokenizer, hs):
                stemmed_sens.append(sen)
            print "{0}\t{1}".format(tag, ' '.join(stemmed_sens))    

def process_wp_given_lang(stream, language, hunspell_path, hunspell_path_infos, cache):
    
    hs, tokenizer = get_tools(language, hunspell_path, hunspell_path_infos, cache)
    process_wp(stream, hs, tokenizer)
    hs.write_cache()

def process_bible_given_lang(stream, language, hunspell_path, hunspell_path_infos, cache):
    hs, tokenizer = get_tools(language, hunspell_path, hunspell_path_infos, cache)
    process_bible(stream, hs, tokenizer)
    hs.write_cache()

def main():

    language = sys.argv[1]
    hunspell_path = sys.argv[2]
    hunspell_path_infos = sys.argv[3]
    cache_file = sys.argv[4]
    process_wp_given_lang(sys.stdin, language, hunspell_path, hunspell_path_infos, cache_file)
   

if __name__ == "__main__":
    main()
