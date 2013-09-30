from collections import defaultdict

def score_path(path):
    covered = 0
    for i in path:
        covered += i[1] - i[0]
    return float(covered) ** 2 / len(path)

class IntervalTree(object):
    """Class that implements a data structure that stores intervals
    It builds up a continuations (interval to interval) map, and a 
    roots set.
    It implements best_path, which will find the best path based on
    a passed @scorer function pointer wth using depth-first traversal.
    """
    def __init__(self, intervals):
        self._add(intervals)

    def _add(self, intervals):
        """builds up data structure. roots & continuations"""
        last = 0
        intervals_starting = defaultdict(list)
        for i in intervals:
            intervals_starting[i[0]].append(i)
            last = max(last, i[1])

        self.continuations = defaultdict(set)
        self.roots = set()
        leaves = set()
        for i in xrange(last + 1):
            # when starting, new intervals are all leaves
            if len(leaves) == 0:
                for interval in intervals_starting[i]:
                    leaves.add(interval)
                self.roots = set(leaves)
                continue

            # append new intervals to end of non-overlapping leaves
            new_leaves = set()
            leaves_to_rm = set()
            for interval in intervals_starting[i]:
                for leaf in leaves:
                    end_of_leaf = leaf[1]
                    start_of_interval = interval[0]
                    if start_of_interval >= end_of_leaf:
                        self.continuations[leaf].add(interval)
                        new_leaves.add(interval)
                        leaves_to_rm.add(leaf)

            leaves -= leaves_to_rm
            leaves |= new_leaves

    def best_path(self, nodes=None, scorer=score_path):
        """dft based best path searching with caching"""
        if not hasattr(self, "best_path_cache"):
            self.best_path_cache = {}

        if nodes is None:
            nodes = self.roots

        if len(nodes) == 0:
            return []

        if len(nodes) > 0:
            new_paths = []
            for node in nodes:
                if node in self.best_path_cache:
                    new_paths.append(self.best_path_cache[node])
                else:
                    local_best_path = [node] + self.best_path(
                        self.continuations[node], scorer)
                    self.best_path_cache[node] = local_best_path
                    new_paths.append(self.best_path_cache[node])

            return self.choose_path(new_paths, scorer)

    def choose_path(self, paths, scorer):
        """scores n paths and chooses best"""
        best_path = [[], None]
        for path in paths:
            s = scorer(path)
            if best_path[1] is None or s > best_path[1]:
                best_path = [path, s]
        return best_path[0]

def test():
    test_intervals = [[(0,1), (0,2), (1,2), (1,3), (2,3)],
                      [(2,3)],
                      [(8, 9), (3, 6), (7, 8), (3, 4), (5, 6), (1, 2),
                       (4, 5), (0, 1)],
                      [(29, 31), (54, 55), (40, 41), (65, 67), (18, 19),
                       (52, 53), (43, 44), (24, 27), (25, 26), (61, 62),
                       (27, 28), (18, 20), (17, 18), (29, 30), (56, 58),
                       (57, 59), (14, 15), (55, 56), (33, 34), (61, 63),
                       (45, 46), (30, 31), (43, 45), (15, 16), (64, 66),
                       (22, 23), (13, 15), (28, 29), (8, 9), (65, 66),
                       (62, 65), (58, 59), (12, 13), (41, 43), (3, 6),
                       (51, 53), (49, 50), (37, 38), (53, 55), (50, 51),
                       (38, 39), (7, 8), (24, 25), (44, 45), (66, 67),
                       (59, 60), (50, 52), (34, 35), (63, 65), (42, 43),
                       (36, 37), (46, 47), (16, 17),(11, 12), (8, 10),
                       (39, 40), (11, 13), (48, 49), (21, 23), (41, 42),
                       (51, 52), (52, 55), (53, 54), (13, 14), (67, 68),
                       (3, 4), (5, 6), (25, 27), (31, 32), (1, 2), (57, 58),
                       (63,64), (37, 39), (56, 57), (4, 5), (0, 1), (55, 57),
                       (33, 35), (60, 61), (42, 45), (9, 10), (62, 63),
                       (19, 20), (64, 65), (20, 23), (26, 27), (21, 22),
                       (0, 2), (20, 21)]]
    for test in test_intervals:
        it = IntervalTree(test)
        bp = it.best_path()
        print bp


if __name__ == "__main__":
    test()

