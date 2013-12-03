import logging
from hunmisc.liblinear.liblinearutil import problem, predict, load_model, \
        train, parameter
from collections import defaultdict

class LiblinearWrapper(object):
    def __init__(self):
        self.class_cache = {}
        self.feat_cache = {}
        self.liblin_params = "-s 0 -c 1"
        self.problem = problem()

    def create_from_file(self, f):
        for l in f:
            le = l.strip().split("\t")
            if len(le) != 2: continue
            y = le[0]
            x = le[1].split()
            self.add_event((y,x))

    def int_feats(self, features):
        feats = dict([
            (self.feat_cache.setdefault(feat, len(self.feat_cache) + 1), 1)
            for feat in features])
        return feats

    def add_event(self, event):
        y, x = event
        if len(x) == 0:
            return

        x_int = self.int_feats(x)
        y_int = self.class_cache.setdefault(y, len(self.class_cache))
        self.problem.add_event(y_int, x_int)

    def choose(self, n):
        counts = {}
        for x in self.problem.x_space:
            for f, _ in x:
                counts[f] = 1 + counts.get(f, 0)
        to_remove = set([f for f, c in counts.iteritems() if c < n])
        return to_remove

    def cutoff(self, n=10):
        logging.info("Running global cutoff with n={0}".format(n))
        to_remove = self.choose(n)
        new_feat_cache = {}
        renumbering = {}
        for feat in self.feat_cache:
            if feat not in to_remove:
                new_feat_cache[feat] = len(new_feat_cache) + 1
            renumbering[feat] = new_feat_cache[feat]
        self.problem.remove(to_remove, renumbering)
        logging.info("cutoff done")

    def save_problem(self, ofn):
        f = open('{0}.problem'.format(ofn), 'w')
        for i in xrange(len(self.problem.y_)):
            f.write("{0} {1}\n".format(
                self.problem.y_[i],
                " ".join("{0}:{1}".format(f.index, f.value) for f in 
                sorted(self.problem.x_space[i], key=lambda x: x.index)[2:])))
        f.close()


    def train(self):
         logging.info("Training...")
         self.problem.finish()
         self.model = train(self.problem, parameter(self.liblin_params))
    
    def predict(self, features, gold = None):
        int_features = [self.int_feats(fvec) for fvec in features]
        if gold:
            gold_int_labels = [self.class_cache[g] for g in gold]
        else:
            gold_int_labels = [0 for i in xrange(len(features))]
        p_labels, _, _ = predict(gold_int_labels, int_features, self.model, '-b 1')
        
        d = dict([(v, k) for k, v in self.class_cache.iteritems()])
        return [d[int(label)] for label in p_labels]
    
    def save_labels(self, ofn):
        l_fn = open('{0}.labelNumbers'.format(ofn), 'w')
        for i in self.class_cache:
            l_fn.write('{0}\t{1}\n'.format(i, self.class_cache[i]))  
        l_fn.close()   
        f_fn = open('{0}.featureNumbers'.format(ofn), 'w')
        for i in self.feat_cache:
            f_fn.write('{0}\t{1}\n'.format(i.encode('utf-8'), \
                 self.feat_cache[i])) 
        f_fn.close()
        
     
    @staticmethod 
    def load(ifn):
        ed = LiblinearWrapper()
        ed.class_cache = dict([(l.strip().split('\t')[0], 
            int(l.strip().split('\t')[1])) 
            for l in open('{0}.labelNumbers'.format(ifn))])

        ed.feat_cache = dict([(l.strip().split('\t')[0], 
            int(l.strip().split('\t')[1])) 
            for l in open('{0}.featureNumbers'.format(ifn))])

        ed.model = load_model('{0}.model'.format(ifn))
        return ed

def get_freq_feat_indeces(problem, count):
    index_freqs = defaultdict(int)
    for l in problem:
        for item in l.strip('\n').split(' ')[1:]:
            index_freqs[int(item.split(':')[0])] += 1
    freq_list = sorted(index_freqs.keys(), \
                       key=lambda x:index_freqs[x], reverse = True)
    return freq_list[:count] 

def generate_freq_feats(ed, fn, count):
    
    model_lines = open('{0}.model'.format(fn)).readlines()[7:]
    problem = open('{0}.problem'.format(fn))
    indeces = get_freq_feat_indeces(problem, count)

    reversed_feat_cache = dict([(v, k) for k, v in \
                                ed.feat_cache.iteritems()])
    reversed_class_cache = dict([(v, k) for k, v in \
                                 ed.class_cache.iteritems()])
    for i in indeces:
        l = model_lines[i- 1]
        values = l.split()
        for j, v in enumerate(values):
            yield reversed_feat_cache[i], reversed_class_cache[j], float(v)

def get_feat_weights(fn):        
    
    fw = defaultdict(lambda: defaultdict(dict))
    model_fh = open('{0}.model'.format(fn))

    for i in range(7):
        l = model_fh.readline()
    i = 1
    while l:
        l = model_fh.readline()
        data = l.strip().split(' ')
        for j, d in enumerate(data):
            fw[i][j] = d   
        i += 1
    return fw
