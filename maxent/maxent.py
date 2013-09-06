"""
Copyright 2011-13 Attila Zseder
Email: zseder@gmail.com

This file is part of hunmisc project
url: https://github.com/zseder/hunmisc

hunmisc is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
"""


from numpy import *

## A simple, ineffective reference implementation of the Iterative Scaling
## algorithm for MaxEnt with binary features.

## Features are functions that take an x vector and return a number (0 or 1 in
## this version).

class MaxEnt(object):
    def __init__(self, train_set, features):
        """@param train_set: the train set;
        @param f: the features."""
        self.axes        = MaxEnt.computeAxes(train_set)
        self.state_space = ones([len(s) for s in self.axes], dtype=float)
        self.state_space /= size(self.state_space)
        self.features    = features
        self.mu          = [1.0] * (len(features) + 1)
        self.mu[0]       = 1.0 / size(self.state_space)
        self.Es          = MaxEnt.computeEs(train_set, features)
    
    def iterate(self, num_iters):
        """Does n full (all mus) iterations."""
        for n in xrange(num_iters):
            for i in xrange(len(self.features)):
                self.do_iteration(i)
    
    def do_iteration(self, i):
        """Does an iteration: computes mu_i and mu_0."""
        sumPi  = self.computePs(i)
        nSumPi = 1 - sumPi
        Efi  = self.Es[i]
        nEfi = 1 - Efi
        print sumPi, nSumPi, Efi, nEfi
        self.mu[i + 1] = self.mu[i + 1] * nSumPi / nEfi * Efi / sumPi
        self.mu[0]     = self.mu[0]     * nEfi / nSumPi
        self.refresh_states()
    
    def get_class(self, x):
        """Returns the class for the vector x. x differs from elements in the
        training set in that it must be one item shorter -- the class must be
        cut off."""
        classes = self.state_space[
                tuple(self.axes[i].index(val) for i, val in enumerate(x))]
        ret = (None, 0)
        for i, p in enumerate(classes):
            if (p > ret[1]):
                ret = (self.axes[-1][i], p)
        return ret
    
    def refresh_states(self):
        """Recomputes the probabilities in the state space."""
        self._refresh_states(self.axes, [], [])
        
    def _refresh_states(self, axes, ids, values):
        """Recursive helper method for refresh_states."""
        if len(axes) == 0:
            new_val = self.mu[0]
            for i, mu in enumerate(self.mu[1:]):
                if self.features[i](values):
                    new_val *= mu
            self.state_space[tuple(ids)] = new_val
        else:
            for axis_id, axis_value in enumerate(axes[0]):
                self._refresh_states(axes[1:], ids + [axis_id],
                                               values + [axis_value])
    
    def computePs(self, i):
        """Computes the summarized probability weight where f_i is 1."""
        return self._computePs(self.features[i], self.axes, [], [])
        
    
    def _computePs(self, feature, axes, ids, values):
        """Recursive helper method for computePs."""
        sum = 0.0
        if len(axes) == 0:
            if feature(values):
                sum += self.state_space[tuple(ids)]
        else:
            for axis_id, axis_value in enumerate(axes[0]):
                sum += self._computePs(feature, axes[1:], ids + [axis_id],
                                       values + [axis_value])
        return sum
    
    @staticmethod
    def computeEs(train_set, features):
        """Computes the sampled expected values for all features."""
        es = zeros(len(features), float)
        for train_data in train_set:
            for i, feature in enumerate(features):
                es[i] += feature(train_data)
        es /= len(train_set)
        return es
    
    @staticmethod
    def computeAxes(train_set):
        """Returns the axes - lists of elements each attribute can take."""
        sets = [set()] * len(train_set[0])
        for train_data in train_set:
            for i, value in enumerate(train_data):
                sets[i].add(value)
        return [list(s) for s in sets]

if __name__ == '__main__':
    def f1(x):
        return x[0] == 1 and x[1] == 1 and x[2] == 0
    def f2(x):
        return x[0] == 0 and x[1] == 0 and x[2] == 0
    def f3(x):
        return x[0] == 1 and x[1] == 0 and x[2] == 1
    def f4(x):
        return x[0] == 0 and x[1] == 1 and x[2] == 1
    
    train_set = [[1, 1, 0]] * 30 + [[0, 0, 0]] * 20 + [[1, 0, 1]] * 24 + [[0, 1, 1]] * 26
    features = [f1, f2, f3, f4]
    m = MaxEnt(train_set, features)
    print m.axes
    print m.Es
    print m.mu
    print m.state_space
#    m.do_iteration(0)
#    print m.axes
#    print m.Es
#    print m.mu
#    print m.state_space
#    m.do_iteration(1)
    m.iterate(2)
    print m.state_space
    print m.get_class([1, 1])
    print m.get_class([1, 0])
    print m.get_class([0, 1])
    print m.get_class([0, 0])
