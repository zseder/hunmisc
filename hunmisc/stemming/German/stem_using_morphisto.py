from subprocess import Popen, PIPE
import re
import sys
import itertools
from string import capitalize as cap

class MorphistoStemmer():

    def __init__(self, printout_res=True, morphisto_model_loc=
                 '/home/judit/morphisto/morphisto.ca',
                max_buffer_size=200,
                result_path='/home/pajkossy/stem_with_morphisto'):

        self.chars_set = set([])
        self.buffer_ = list()
        self.line_count = 0
        self.max_size = max_buffer_size
        self.morphisto_analyses = {}
        self.analysis_pattern = re.compile(r'<.*?>')
        self.multiple_space_pattern = re.compile(r'\s[\s]+')
        self.morphisto_model_loc = morphisto_model_loc
        self.printout_res = printout_res
        if self.printout_res is False:
            self.open_filehandlers(result_path)

    def open_filehandlers(self, result_path):

        self.not_stemmed_fh =\
        open('{0}/not_stemmed'.format(result_path), 'w')
        self.simple_stemmed_fh =\
        open('{0}/simple_stemmed'.format(result_path), 'w')
        self.compound_stemmed_fh =\
        open('{0}/compound_stemmed'.format(result_path), 'w')
        self.compound_not_stemmed_fh =\
        open('{0}/compound_not_stemmed'.format(result_path), 'w')

    def close_filehandlers(self):

        self.not_stemmed_fh.close()
        self.simple_stemmed_fh.close()
        self.compound_stemmed_fh.close()
        self.compound_not_stemmed_fh.close()

    def generate_all_split(self, word, max_count):
        if max_count < 2 or len(word) < 3:
            yield [word]
        else:
            for i in range(1, len(word)):   # lengh of first part
                for j in range(1, max_count):    # number of remaining splits
                    for split in self.generate_all_split(word[i:], j):
                        yield [word[:i]] + split

    def versions(self, w):

        versions = set([])
        versions.add(w)
        versions.add(w[0].upper() + w[1:])
        if w[-1] == 's':
            versions.add(w[:-1])
            versions.add(w[0].upper() + w[1:-1])
        return list(versions)

    def generate_all_split_with_casing_s(self, word, max_count):

        for split in self.generate_all_split(word, max_count):
            all_list = [(p, self.versions(p)) for p in split]
            yield all_list

    def clear_caches(self):

        #self.word_split = {}
        self.chars_set = set([])
        self.buffer_ = list()
        self.morphisto_analyses = {}
        self.line_count = 0

    def analyse_update_cache(self, list_to_analyse):
        if len(list_to_analyse) > 0:
            morphisto_input = '\n'.join(list_to_analyse).encode('utf-8')
            p = Popen('fst-infl2 ' + self.morphisto_model_loc,
                  shell=True, stdin=PIPE, stdout=PIPE)
            morph_out = p.communicate(morphisto_input)[0].decode('utf-8')
            self.update_morphisto_cache(morph_out)

    def update_morphisto_cache(self, morph_out):

        for chars, analysis in self.process_morphisto_output(morph_out):
            self.morphisto_analyses[chars] = analysis

    def process_morphisto_output(self, morph_out):

        for title, block in self.generate_output_blocks(morph_out):
            if block[0][:9] != 'no result':
                results = []
                for l in block:
                    r = re.sub(self.analysis_pattern, ' ', l)
                    r = re.sub(self.multiple_space_pattern, ' ', r).strip()
                    if r not in results and r != '':
                        results.append(r)
                yield title, results

    def generate_output_blocks(self, morph_out):

        block = []
        title = morph_out.split('\n')[0].strip()[2:]
        for line in morph_out.split('\n')[1:]:
            l = line.strip()
            if l[:2] == '> ':
                if block != []:
                    yield title, block
                    title = l[2:]
                    block = []
            else:
                block.append(l)
        yield title, block

    def merge_ig_er_ung_endings(self, a):

        wds = a.split(' ')
        if len(wds) == 2 and wds[0][-2:] == 'en' and wds[1] == 'ig':
            return True, wds[0][:-2] + 'ig'
        if len(wds) == 2 and wds[0][-2:] == 'en' and wds[1] == 'er':
            return True, wds[0][:-2] + 'er'
        if len(wds) == 2 and wds[0][-2:] == 'en' and wds[1] == 'ung':
            return True, wds[0][:-2] + 'ung'
        if len(wds) == 2 and wds[1] == 'keit':
            return True, wds[0] + 'keit'
        if len(wds) == 2 and wds[1] == 'chen':
            return True, wds[0] + 'chen'
        return False, a

    def is_good_split(self, split, list_of_analysis_to_match):
        
        list_of_analysis = []
        word_in_orig = ''.join([p[0] for p in split[:-1]])
        for c, versions in split:
            list_of_analysis.append([])
            for v in versions:
                if v in self.morphisto_analyses:
                    for a in self.morphisto_analyses[v]:
                        list_of_analysis[-1].append(a)

        list_of_analysis[-1] = filter(lambda x: len(x.split(' ')) == 1 or
                                    self.merge_ig_er_ung_endings(x)[0] is True,
                                     list_of_analysis[-1])
        # last part of split should be analysed as one token
        for tuple_ in itertools.product(*list_of_analysis):
            if ' '.join(tuple_) in list_of_analysis_to_match:
                merged_ending = self.merge_ig_er_ung_endings(
                    tuple_[-1].lower())[1]
                return True, word_in_orig + merged_ending
        return False, ''

    def lookfor_matching_stemmed_split(self, compound_list):
        not_succeeded_list = []
        stemmed_list = []

        for pair in compound_list:
            word, analysis_list = pair
            max_split_count = max([len(a.split(' ')) for a in analysis_list])
            is_true = False
            for split in self.generate_all_split_with_casing_s\
                         (word, max_split_count):
                is_true, stemmed = self.is_good_split(split, analysis_list)
                if is_true is True:
                    stemmed_list.append('\t'.join((word, stemmed)))
                    break
            if is_true is False:
                    not_succeeded_list.append('\t'.join(
                        (word, ';'.join(analysis_list))))
        return not_succeeded_list, stemmed_list

    def analyse_update_cache_in_parts(self, all_list):

        buffer_ = []
        i = 0
        for item in all_list:
            i += 1
            buffer_.append(item)
            if i > 500000:
                self.analyse_update_cache(buffer_)
                buffer_ = []
                i = 0
        self.analyse_update_cache(buffer_)        

    def compound_word_stemming(self, compound_words):

        chars_to_analyse = []
        for pair in compound_words:
            word, analysis_list = pair
            #self.word_split[word] = []
            max_split_count = max([len(a.split(' ')) for a in analysis_list])
            
            for split in self.generate_all_split_with_casing_s\
                         (word, max_split_count):
                #self.word_split[word].append(split)
                for chars, chars_versions in split:
                    for chars in chars_versions:
                        if chars not in self.morphisto_analyses:
                            chars_to_analyse.append(chars)
        self.analyse_update_cache_in_parts(chars_to_analyse)
        not_succeeded, stemmed = self.lookfor_matching_stemmed_split\
                (compound_words)
        return not_succeeded, stemmed

    def sort_analysed_buffer(self):

        not_stemmed = []
        simple_word_stemmings = []
        compound_words = []
        for b in self.buffer_:
            simple_found = False
            if b not in self.morphisto_analyses:
                not_stemmed.append(b)
            else:
                for a in self.morphisto_analyses[b]:
                    if len(a.split(' ')) == 1:
                        simple_word_stemmings.append('\t'.join((b, a)))
                        simple_found = True
                        break
                if not simple_found:
                    compound_words.append((b, self.morphisto_analyses[b]))
        return not_stemmed, simple_word_stemmings, compound_words

    def stem_lines_with_morphisto(self):

        self.analyse_update_cache(self.buffer_)
        not_stemmed, simple_word_stemmings, compound_words =\
                self.sort_analysed_buffer()
        not_stemmed_compound, compound_word_stemmings =\
                self.compound_word_stemming(compound_words)

        self.write_out_result(not_stemmed, simple_word_stemmings,
                              not_stemmed_compound, compound_word_stemmings)

    def write_out_result(self, not_stemmed, simple_word_stemmings,
                         not_stemmed_compound, compound_word_stemmings):
        not_stemmed = '\n'.join(not_stemmed).encode('utf-8') + '\n'
        simple_word_stemmings = '\n'.join(simple_word_stemmings)\
                .encode('utf-8') + '\n'
        compound_word_stemmings = '\n'.join(compound_word_stemmings)\
                .encode('utf-8') + '\n'
        not_stemmed_compound = '\n'.join(not_stemmed_compound)\
                .encode('utf-8') + '\n'
        if self.printout_res is False:
            self.not_stemmed_fh.write(not_stemmed)
            self.simple_stemmed_fh.write(simple_word_stemmings)
            self.compound_stemmed_fh.write(compound_word_stemmings)
            self.compound_not_stemmed_fh.write(not_stemmed_compound)
        else:
            sys.stderr.write(not_stemmed + simple_word_stemmings + 
                            compound_word_stemmings + not_stemmed_compound)

    def stem_input(self, data):

        for line in data:
            self.line_count += 1
            if self.line_count % 100 == 0:
                print self.line_count
            l = line.strip().decode('utf-8')
            self.buffer_.append(cap(l))
            if self.line_count > self.max_size or line is None:
                self.stem_lines_with_morphisto()
                self.clear_caches()
        self.stem_lines_with_morphisto()
        if self.printout_res is False:
            self.close_filehandlers()


def main():

    a = MorphistoStemmer(printout_res=False)
    a.stem_input(sys.stdin)

if __name__ == '__main__':
    main()
