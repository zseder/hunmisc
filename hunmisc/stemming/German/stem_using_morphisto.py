from subprocess import Popen, PIPE
import re
import sys
import itertools
from string import capitalize as cap
from hunmisc.xstring.stringdiff import levenshtein
import cPickle
import dawg

class MorphistoStemmer():

    def __init__(self, freq_file_path, result_tag, printout_res=True,
                 morphisto_model_loc='/mnt/pajkossy/morphisto.ca',
                max_buffer_size=1000, result_path='/mnt/pajkossy/results',
                freq_struct_is_dawg=True, freq_ratio_limit=0.1, 
                 lenght_limit=20):

        self.chars_set = set([])
        self.buffer_ = list()
        self.line_count = 0
        self.result_tag = result_tag
        self.result_path = result_path
        self.max_size = max_buffer_size
        self.morphisto_analyses = {}
        self.analysis_pattern = re.compile(r'<.*?>')
        self.multiple_space_pattern = re.compile(r'\s[\s]+')
        self.morphisto_model_loc = morphisto_model_loc
        self.printout_res = printout_res
        if self.printout_res is False:
            self.open_filehandlers()
        self.freq_struct_is_dawg = freq_struct_is_dawg
        self.get_freqs(freq_file_path)
        self.freq_ratio_limit = freq_ratio_limit
        self.lenght_limit=lenght_limit

    def get_freqs(self, freq_file_path):

        if self.freq_struct_is_dawg:
            self.freqs = dawg.IntDAWG().load(freq_file_path)
        else:
            self.freqs = cPickle.load(open(freq_file_path))

    def open_filehandlers(self):

        self.not_stemmed_fh =\
        open('{0}/{1}.not_stemmed'.format(
            self.result_path, self.result_tag), 'w')
        self.simple_stemmed_fh =\
        open('{0}/{1}.simple_stemmed'.format(
            self.result_path, self.result_tag), 'w')
        self.compound_stemmed_fh =\
        open('{0}/{1}.compound_stemmed'.format(
            self.result_path, self.result_tag), 'w')
        self.compound_not_stemmed_fh =\
        open('{0}/{1}.compound_not_stemmed'.format(
            self.result_path, self.result_tag), 'w')
        self.freq_discarded_fh =\
        open('{0}/{1}.freq_discarded'.format(
            self.result_path, self.result_tag), 'w')
        self.s_stripping_fh =\
        open('{0}/{1}.s_stripping'.format(
            self.result_path, self.result_tag), 'w')

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

    def get_patterns(self):

        patterns = {}
        patterns['ue'] = u'\u00fc'
        patterns['oe'] = u'\u00f6'
        patterns['au'] = u'\u00e4'

        return patterns

    def stem_with_ue_replacement(self, data):

        mappings = self.get_patterns()
        list_to_stem = []
        dict_of_toks_to_stem = {}
        for line in data:
            l = line.strip().decode('utf-8')
            l_orig = l
            for m in mappings:
                l = re.sub(m, mappings[m], l)
            if l != l_orig:
                list_to_stem.append(l.encode('utf-8'))
                dict_of_toks_to_stem[l.encode('utf-8')] = \
                        l_orig.encode('utf-8')
        if len(list_to_stem) > 0:
            self.stem_input(list_to_stem)
            if self.printout_res is False:
                f = open('{0}/{1}.dict.pickle'.format(
                    self.result_path, self.result_tag), 'w')
                cPickle.dump(dict_of_toks_to_stem, f)

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
        if len(wds) == 2 and wds[0][-2:] in ['e', 'n'] and wds[1] == 'ig':
            return True, wds[0][:-1] + 'ig'
        if len(wds) == 2 and wds[0][-2:] in ['e', 'n'] and wds[1] == 'er':
            return True, wds[0][:-1] + 'er'
        if len(wds) == 2 and wds[0][-2:] in ['e', 'n'] and wds[1] == 'ung':
            return True, wds[0][:-1] + 'ung'
        if len(wds) == 2 and wds[1] == 'keit':
            return True, wds[0] + 'keit'
        if len(wds) == 2 and wds[1] == 'chen':
            return True, wds[0] + 'chen'
        return False, a

    def merge_prefixes(self, a):

        prefixes = set(['be', 'emp', 'ent', 'er', 'ge', 'miss', 'ver', 'voll',
                        'zer', 'ab', 'an', 'auf', 'aus', 'be', 'durch', 'ein',
                        'mit', 'nach', 'vor', 'zu', 'zusammen'])
        wds = a.split(' ')
        if wds[0] in prefixes:
            try:
                return u'{0}{1} {2}'.format(wds[0], wds[1], ' '.join(
                    wds[2:])).strip()
            except:
                print wds
                quit()
        else:
            return a

    def merge_prefixes_ig_er_ung_endings(self, a):
        if len(a.split(' ')) == 1:
            return True, a
        a = self.merge_prefixes(a)
        a2 = self.merge_ig_er_ung_endings(a)
        return a2

    def is_good_split(self, split, list_of_analysis_to_match):

        list_of_analysis = []
        word_in_orig = ''.join([p[0] for p in split[:-1]])
        for c, versions in split:
            list_of_analysis.append([])
            for v in versions:
                if v in self.morphisto_analyses:
                    for a in self.morphisto_analyses[v]:
                        a = a.strip()
                        if len(a) > 0:
                            list_of_analysis[-1].append(a)
        list_of_analysis[-1] = filter(lambda x: len(x.split(' ')) == 1 or
                                    self.merge_prefixes_ig_er_ung_endings(x)[0]
                                      is True, list_of_analysis[-1])
        # last part of split should be analysed as one token
        for tuple_ in itertools.product(*list_of_analysis):
            if ' '.join(tuple_) in list_of_analysis_to_match:
                merged_ending = self.merge_prefixes_ig_er_ung_endings(
                    tuple_[-1].lower())[1]
                return True, word_in_orig + merged_ending
        return False, ''

    def lookfor_matching_stemmed_split(self, compound_list):
        not_succeeded_list = []
        stemmed_list = []
        freq_discarded = []

        for pair in compound_list:
            word, analysis_list = pair
            solutions = []
            try:
                max_split_count = max([len(a.split(' '))
                                       for a in analysis_list])
            except:
                print word, analysis_list
                continue
            is_true = False
            for split in self.generate_all_split_with_casing_s\
                         (word, max_split_count):
                is_true, stemmed = self.is_good_split(split, analysis_list)
                if is_true is True:
                    solutions.append(stemmed)
            if len(solutions) > 0:
                    chosen_stem = self.choose_most_frequent_stemming(
                    solutions)
                    if self.freqs.get(chosen_stem.lower(), 0) >\
                       self.freq_ratio_limit * self.freqs.get(word.lower(), 0):
                        stemmed_list.append(
                            '\t'.join((word, chosen_stem)))
                    else:
                        freq_discarded.append(
                            '\t'.join((word, chosen_stem)))
            else:
                not_succeeded_list.append('\t'.join(
                        (word, ';'.join(analysis_list))))
        return not_succeeded_list, stemmed_list, freq_discarded

    def analyse_update_cache_in_parts(self, all_list):

        buffer_ = []
        i = 0
        for item in all_list:
            i += 1
            buffer_.append(item)
            if i > 100000:
                self.analyse_update_cache(buffer_)
                buffer_ = []
                i = 0
        self.analyse_update_cache(buffer_)

    def compound_word_stemming(self, compound_words):

        chars_to_analyse = []
        for pair in compound_words:
            word, analysis_list = pair
            if len(word) > self.lenght_limit:
                sys.stderr.write(u'{0}\n'.format(word).encode('utf-8'))
                continue
            try:
                max_split_count = max([len(a.split(' '))
                                        for a in analysis_list])
            except:
                print word, analysis_list
                continue
            for split in self.generate_all_split_with_casing_s\
                         (word, max_split_count):
                for chars, chars_versions in split:
                    for chars in chars_versions:
                        if chars not in self.morphisto_analyses:
                            chars_to_analyse.append(chars)
        self.analyse_update_cache_in_parts(chars_to_analyse)
        not_succeeded, stemmed, freq_discarded = \
                self.lookfor_matching_stemmed_split(compound_words)
        return not_succeeded, stemmed, freq_discarded

    def sort_analysed_buffer(self):

        not_stemmed = []
        simple_word_stemmings = []
        compound_words = []
        freq_discarded = []
        s_stripping = []
        for b in self.buffer_:
            simple_found = False
            if b not in self.morphisto_analyses:
                if b[-1] == 's' and self.freqs.get(b[:-1].lower(), 0) >\
                1/self.freq_ratio_limit * self.freqs.get(b.lower(), 0):
                    s_stripping.append('\t'.join((b, b[:-1])))
                else:
                    not_stemmed.append(b)
            else:
                stemmed_versions = []
                for a in self.morphisto_analyses[b]:
                    if len(a.split(' ')) == 1:
                        stemmed_versions.append(a)
                        simple_found = True
                if not simple_found:
                    compound_words.append((b, self.morphisto_analyses[b]))
                else:
                    chosen_stem = self.choose_most_frequent_stemming(
                    stemmed_versions)
                    if self.freqs.get(chosen_stem.lower(), 0) >\
                       self.freq_ratio_limit * self.freqs.get(b.lower(), 0):
                        simple_word_stemmings.append(
                            '\t'.join((b, chosen_stem)))
                    else:
                        freq_discarded.append(
                            '\t'.join((b, chosen_stem)))
        return not_stemmed, simple_word_stemmings, compound_words,\
                freq_discarded, s_stripping

    def choose_most_similar_stemming(self, stemmed_versions, b):
        return sorted(stemmed_versions, key=lambda x: levenshtein(x, b))[0]

    def choose_most_frequent_stemming(self, stemmed_versions):
        return sorted(stemmed_versions, key=lambda x: self.freqs.get(
            x.lower(), 0), reverse=True)[0]

    def stem_lines_with_morphisto(self):

        self.analyse_update_cache(self.buffer_)
        not_stemmed, simple_word_stemmings, compound_words,\
                freq_discarded_simple, s_stripping = \
                self.sort_analysed_buffer()
        not_stemmed_compound, compound_word_stemmings,\
                freq_discarded_compound =\
                self.compound_word_stemming(compound_words)
        freq_discarded = freq_discarded_simple + freq_discarded_compound
        self.write_out_result(not_stemmed, simple_word_stemmings,
                              not_stemmed_compound, compound_word_stemmings,
                              freq_discarded, s_stripping)

    def write_out_result(self, not_stemmed, simple_word_stemmings,
                         not_stemmed_compound, compound_word_stemmings,
                         freq_discarded, s_stripping):
        not_stemmed = '\n'.join(not_stemmed).encode('utf-8') + '\n'
        simple_word_stemmings = '\n'.join(simple_word_stemmings)\
                .encode('utf-8') + '\n'
        compound_word_stemmings = '\n'.join(compound_word_stemmings)\
                .encode('utf-8') + '\n'
        not_stemmed_compound = '\n'.join(not_stemmed_compound)\
                .encode('utf-8') + '\n'
        freq_discarded = '\n'.join(freq_discarded)\
                .encode('utf-8') + '\n'
        s_stripping = '\n'.join(s_stripping).encode('utf-8') + '\n'
        if self.printout_res is False:
            self.not_stemmed_fh.write(not_stemmed)
            self.simple_stemmed_fh.write(simple_word_stemmings)
            self.compound_stemmed_fh.write(compound_word_stemmings)
            self.compound_not_stemmed_fh.write(not_stemmed_compound)
            self.freq_discarded_fh.write(freq_discarded)
            self.s_stripping_fh.write(s_stripping)
        else:
            sys.stderr.write(not_stemmed + simple_word_stemmings +
                            compound_word_stemmings + not_stemmed_compound
                            + freq_discarded + s_stripping)

    def stem_input(self, data):
        global_line_count = 0
        for line in data:
            global_line_count += 1
            self.line_count += 1
            if global_line_count % 1000 == 0:
                print global_line_count
            l = line.strip().decode('utf-8')
            self.buffer_.append(cap(l))
            if self.line_count > self.max_size or line is None:
                self.stem_lines_with_morphisto()
                self.clear_caches()
        self.stem_lines_with_morphisto()
        if self.printout_res is False:
            self.close_filehandlers()


def main():

    a = MorphistoStemmer(sys.argv[1], sys.argv[2], printout_res=False)

    a.stem_input(sys.stdin)

if __name__ == '__main__':
    main()
