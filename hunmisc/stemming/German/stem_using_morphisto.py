from subprocess import Popen, PIPE
import re
import sys
import itertools

def generate_first_lines(output):
    
    data = []
    for line in output:
        l = line.strip('\n').decode('utf-8')
        if l[:2] == '> ':
            data.append(l[2:])
        elif len(data) == 1:
            if l[:9] != 'no result':
                data.append(l)
                yield data
            data = []
            
def get_compound_words(output):
    
    analysis_pattern = re.compile(r'<.*?>')
    for pair in generate_first_lines(output):
        word, analysis = pair
        words = re.sub(analysis_pattern, ' ', analysis)
        words = ' '.join(filter(lambda x:x!= '', words.split(' ')))
        if len(words.split(' ')) > 1:
            print u'{0}\t{1}'.format(word, words).encode('utf-8')

class MorphistoStemmer():

    def __init__(self, morphisto_model_loc='/home/judit/morphisto/morphisto.ca', 
                max_buffer_size=100):
        self.max_size = max_buffer_size
        self.chars_set = set([])
        self.data_lines = list()
        self.line_count = 0
        self.word_split = {}
        self.chars_analyses = {}
        self.analysis_pattern = re.compile(r'<.*?>')
        self.multiple_space_pattern = re.compile(r'\s[\s]+')
        self.morphisto_model_loc = morphisto_model_loc

    def generate_all_split(self, word, max_count):
        if max_count < 2 or len(word) < 3:
            yield [word]
        else:
            for i in range(2, len(word) - 1):   # lengh of first part
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


    def process_input_line(self, l):

         word = l.split('\t')[0]
         analysis = l.split('\t')[1]
         max_count = len(analysis.split(' '))
         self.word_split[word] = []
         for split in self.generate_all_split_with_casing_s\
                      (word, max_count):
             self.word_split[word].append(split)
             for chars, chars_versions in split:
                 for chars in chars_versions:
                     if chars not in self.chars_analyses:
                         self.chars_set.add(chars)
    
    def clear_caches(self):

        self.word_split = {}
        self.data_lines = list()
        self.chars_set = set([])

    def update_chars_analyses_with_morphisto(self, list_to_analyse):
        
        morphisto_input = '\n'.join(list_to_analyse).encode('utf-8')
        p = Popen('fst-infl2 ' + self.morphisto_model_loc,
                  shell=True, stdin=PIPE, stdout=PIPE)
        morph_out = p.communicate(morphisto_input)[0].decode('utf-8')
        self.update_chars_analyses(morph_out) 

    def update_chars_analyses(self, morph_out):    

        for chars, analysis in self.process_morphisto_output(morph_out):
            self.chars_analyses[chars] = analysis

    def process_morphisto_output(self, morph_out):

        for title, block in self.generate_output_blocks(morph_out):
            if block[0][:9] == 'no result':
                yield title, None
            else:
                results = set([])
                for l in block:
                    r = re.sub(self.analysis_pattern, ' ', l)
                    r = re.sub(self.multiple_space_pattern, ' ', r)
                    results.add(r.strip())
                    results = results.difference(set(['']))
                yield title, list(results)        
    
    def generate_output_blocks(self, morph_out): 
    
        block = []
        title = ''
        for line in morph_out.split('\n'):
            l = line.strip()
            if l[:2] == '> ':
                if block != []:
                    yield title, block
                    title = l[2:]
                    block = []
            else:
                block.append(l)
        yield title, block           
    
    def merge_ig_endings(self, a):
        
        wds = a.split(' ')
        if len(wds) == 2 and wds[0][-2:] == 'en' and wds[1] == 'ig':
            return True, wds[0][:-2] + 'ig'
        else:
            return False, a

    def is_good_split(self, split, analysis):
        n = False
        list_of_analysis = []
        word_in_orig = ''.join([p[0] for p in split[:-1]])
        for c, versions in split:
            list_of_analysis.append([])
            for v in versions:
                if self.chars_analyses[v] != None:
                    for a in self.chars_analyses[v]:
                        list_of_analysis[-1].append(a)

        list_of_analysis[-1] = filter(lambda x: len(x.split(' ')) == 1 or
                                    self.merge_ig_endings(x)[0] == True, #landen ig
                                     list_of_analysis[-1])
        if n == True:
            print list_of_analysis
        # last part of split should be analysed as one token        

        for tuple_ in itertools.product(*list_of_analysis):
            if ' '.join(tuple_) == analysis:
                merged_ending = self.merge_ig_endings(tuple_[-1].lower())[1]
                return True, word_in_orig + merged_ending
        return False, ''    
        

    def print_results(self):

        for l in self.data_lines:
            word = l.split('\t')[0]
            analysis = l.split('\t')[1]
            is_true = False
            for split in self.word_split[word]:
                is_true, stemmed = self.is_good_split(split, analysis)
                if is_true is True:
                    print u'{0}\t{1}'.format(word, stemmed).encode('utf-8')
                    break
            if is_true is False: 
                print 'NORES', word.encode('utf-8'), analysis.encode('utf-8')     

    def stem_based_on_analysis(self, data): 

        for line in data:
            if self.line_count % 100 == 0:
                print self.line_count
            self.line_count += 1    

            l = line.strip().decode('utf-8')
            self.data_lines.append(l)
            self.process_input_line(l)

            if self.line_count > self.max_size or line == None:
                self.update_chars_analyses_with_morphisto(
                    list(self.chars_set))
                self.print_results()    
                self.clear_caches()
                quit()
                        


#pattern = re.compile(ur'> ([\w]+)', re.UNICODE)
def main():

    a = MorphistoStemmer()
    a.stem_based_on_analysis(sys.stdin)
    #get_compound_words(sys.stdin)

if __name__ == '__main__':
    main()
