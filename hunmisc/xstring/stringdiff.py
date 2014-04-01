"""
Copyright 2011-13 Attila Zseder David Nemeskey
Email: zseder@gmail.com nemeskeyd@gmail.com

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


"""Levenshtein and Hamming edit distances for strings.

The distance between two strings is conceptually the number of places that one
or the other string needs to be changed to turn it into the other, much like
those word games where you have to turn "BROWN" into "ORANGE" one letter at a
time.

(BROWN -> BRAWN -> BRAN -> GRAN -> RANG -> RANGE -> ORANGE)

The Hamming distance is a very simple measure of string distance. It simply
counts how many characters are different between the two strings, which must be
of equal length.

The Levenshtein distance (otherwise known as simply "edit distance") is a more
sophisticated measure of string difference. It measures the similarity between
two strings. The distance is the number of deletions, insertions, or
substitutions required to transform one string into the other. The greater the
Levenshtein distance, the more different the strings are.

See:
http://en.wikipedia.org/wiki/Levenshtein_distance
http://www.merriampark.com/ld.htm
http://www.cut-the-knot.org/do_you_know/Strings.shtml

To be a measure of distance in a metric space, the measurement must be
symmetrical -- that is, distance(string1, string2) must equal distance(string2,
string1). This is true for both Hamming and Levenshtein.

(Not all spaces are metric spaces. For instance, in a city with one-way
streets, it is not always true that distance-as-the-car-drives between points A
and B is the same in both directions.)

Copyright (c) 2005 Steven D'Aprano.
Released under the same license as used by Python 2.3.2 itself.
See http://www.python.org/psf/license.html for details, and
http://www.python.org/2.3.2/license.html for the full text of the license.
"""

import sys


def hamming(s1, s2, case_sensitive=0):
    """Hamming distance between two strings.

    s1 and s2 should be two equal-length strings. Returns an integer count of
    the number of places the strings differ, that is, the number of
    substitutions needed to change one string into the other. A Hamming
    distance of zero implies the strings are the same; the higher the distance,
    the more different they are.

    If case_sensitive is false (the default), comparisons are case insensitive.
    Case sensitive comparisons only consider standard ASCII upper/lower case
    and are not internationalised.  """

    if len(s1) != len(s2):
        raise ValueError("Hamming edit distance is only defined for" +
                         " equal-length strings.")
    if not case_sensitive:
        s1 = s1.upper()
        s2 = s2.upper()
    return sum([c != k for c, k in zip(s1, s2)])


def levenshtein(s1, s2, case_sensitive=0, max_distance=sys.maxint,
                w_insert=1, w_delete=1, w_replace=1):
    """Levenshtein edit distance between two strings.

    s1 and s2 should be two arbitrary length strings. Returns an integer count
    of the edit distance between the strings, that is, the number of
    insertions, deletions and substitutions needed to change one string into
    the other. A Levenshtein distance of zero implies the strings are the same;
    the higher the distance, the more different the strings are.

    If case_sensitive is false (the default), comparisons are case insensitive.
    Case sensitive comparisons only consider standard ASCII upper/lower case
    and are not internationalised.

    The rest of the parameters are:
    - max_distance: caps the distance value.
    - w_insert: weight of the insertion operator. The default is 1.
    - w_delete: weight of the deletion operator. The default is 1.
    - w_replace: weight of the replacement operator. The default is 1 (!).
    """
    m = len(s1)
    n = len(s2)
    if m == 0:
        return n * w_insert
    if n == 0:
        return m * w_delete
    # There is a small, but significant difference in performance depending on
    # which string is longer, especially for very long strings. Swap the order
    # of the strings so that s1 is the shorter.
    if n < m:
        s1, s2 = s2, s1
        m, n = n, m
        w_insert, w_delete = w_delete, w_insert
    # Adjust for case sensitivity.
    if not case_sensitive:
        s1 = s1.upper()
        s2 = s2.upper()
    # Create an array with rows 0..m and columns 0..n.
    # We represent the array as a list of lists:
    #     array = [ row0, row1, row2, ... ]
    # where each row is also a list.
    # To access the item in row A column B, use array[A][B].
    array = [None]*(m+1)
    for i in range(m+1):
        array[i] = [None]*(n+1)
    # Initialise the first row to 0..n.
    for i in range(n+1):
        array[0][i] = w_insert * i
    # Initialize the first column to 0..m.
    for i in range(m+1):
        array[i][0] = w_delete * i

    # Measure the differences.
    # Loop over the rows and columns of the array, skipping the first of each.
    # Remember that rows = 0..m and columns = 0..n.
    for row in range(1, m+1):
        c1 = s1[row - 1]
        for col in range(1, n+1):
            c2 = s2[col - 1]
            # If the characters are the same, the cost is 0, otherwise it is 1.
            cost = 0 if c1 == c2 else w_replace

            # Cell immediately above plus one.
            x = array[row-1][col] + w_delete
            # Cell immediately to the left plus one.
            y = array[row][col-1] + w_insert
            # Cell diagonally above and to the left, plus the cost.
            z = array[row-1][col-1] + cost
            array[row][col] = min(x, y, z)

        # Check if we reached max_distance
        if min(array[row]) >= max_distance:
            return max_distance
    # When done, the bottom-right cell contains the Levenshtein distance.
    return min(max_distance, array[-1][-1])


class LevenshteinCustomWeights(object):
    """
    Levenshtein edit distance between two strings with custom weights.

    Note: the only reason why this is in a separate class instead of a function
    is to avoid the costly inversion of the replacement mapping. Alternatively,
    we could just not swap the two string -- it would be worth seeing if the
    performance really decreased; I doubt it (provided we use numpy arrays
    instead of nested lists).
    """

    def __init__(self,
                 w_insert=1, w_delete=1, w_replace=1,
                 insert_map={}, delete_map={}, replace_map={}):
        """
        This class differs from the function above in that the user can
        supply a dictionary for each operation with a {character: cost} mapping
        for insertion and deletion, and a {character x character: cost} mapping
        for replacement, thereby customizing the relations.

        The rest of the parameters are:
        - w_insert: weight of the insertion operator. The default is 1.
        - w_delete: weight of the deletion operator. The default is 1.
        - w_replace: weight of the replacement operator. The default is 1 (!).
        """
        self.w_insert = w_insert
        self.w_delete = w_delete
        self.w_replace = w_replace
        self.insert_map = insert_map
        self.delete_map = delete_map
        self.replace_map = replace_map
        self.inv_replace_map = dict(((k[1], k[0]), v)
                                    for k, v in replace_map.iteritems())

    def levenshtein(self, s1, s2, case_sensitive=0, max_distance=float('inf')):
        """
        s1 and s2 should be two arbitrary length strings. Returns an integer
        count of the edit distance between the strings, that is, the number of
        insertions, deletions and substitutions needed to change one string
        into the other. A Levenshtein distance of zero implies the strings are
        the same; the higher the distance, the more different the strings are.

        If case_sensitive is false (the default), comparisons are case
        insensitive. Case sensitive comparisons only consider standard ASCII
        upper/lower case and are not internationalised.

        If max_distance is specified, the function returns as soon as the
        distance reaches this value.
        """
        m = len(s1)
        n = len(s2)
        if m == 0:
            return sum(self.insert_map.get(s2[i], self.w_insert)
                       for i in xrange(n))
        if n == 0:
            return sum(self.delete_map.get(s1[i], self.w_delete)
                       for i in xrange(m))
        # There is a small, but significant difference in performance depending
        # on which string is longer, especially for very long strings. Swap the
        # order of the strings so that s1 is the shorter.
        if n < m:
            s1, s2 = s2, s1
            m, n = n, m
            w_insert, w_delete = self.w_delete, self.w_insert
            insert_map, delete_map = self.delete_map, self.insert_map
            replace_map = self.inv_replace_map
        else:
            w_insert, w_delete = self.w_insert, self.w_delete
            insert_map, delete_map = self.insert_map, self.delete_map
            replace_map = self.replace_map

        # Adjust for case sensitivity.
        if not case_sensitive:
            s1 = s1.upper()
            s2 = s2.upper()

        # We use two arrays + the two marginals instead of a 2D array
        # Only the first (vertical) marginal has been made implicit in the first
        # coordinate of prev and curr.
        #s1_marginal = [0] * (m + 1)
        #for i in xrange(1, m + 1):
        #    s1_marginal[i] = s1_marginal[i - 1] + delete_map.get(s1[i - 1], w_delete)
        s2_marginal = [0] * (n + 1)
        for i in xrange(1, n + 1):
            s2_marginal[i] = s2_marginal[i - 1] + insert_map.get(s2[i - 1], w_insert)

        curr = s2_marginal
        prev = [0] * (n + 1)

        # Measure the differences.
        # Loop over the rows and columns of the array, looking at two rows at a
        # time.
        for row in xrange(1, m + 1):
            c1 = s1[row - 1]
            # The old prev == curr will be completely overwritten
            prev, curr = curr, prev
            curr[0] = prev[0] + delete_map.get(c1, w_delete)
            for col in xrange(1, n + 1):
                c2 = s2[col - 1]
                # If the characters are the same, the cost is 0,
                # otherwise it is 1.
                cost = (0 if c1 == c2
                        else replace_map.get((c1, c2), self.w_replace))

                # Cell immediately above plus one.
                x = prev[col] + delete_map.get(c1, self.w_delete)
                # Cell immediately to the left plus one.
                y = curr[col-1] + insert_map.get(c2, self.w_insert)
                # Cell diagonally above and to the left, plus the cost.
                z = prev[col-1] + cost
                curr[col] = min(x, y, z)

            # Check if we reached max_distance
            if min(curr) >= max_distance:
                return max_distance
        # When done, the bottom-right cell contains the Levenshtein distance.
        return min(max_distance, curr[-1])


def verify():
    print "Verifying Hamming distance for equal-length strings:"
    assert hamming("SUPER", "DUPER") == 1
    assert hamming("STEM", "SPAM") == 2
    assert hamming("SPAM", "spam") == 0
    assert hamming("SPAM", "spam", 1) == 4
    print "No errors with Hamming distance."
    print "========================================================"
    print "Verifying Levenshtein edit distance:"
    assert levenshtein("ANT", "AUNT") == 1
    assert levenshtein("GUMBO", "GAMBOL") == 2
    assert levenshtein("GUMBO", "") == 5
    assert levenshtein("spam", "ham") == 2
    assert levenshtein("spam", "SPAM") == 0
    assert levenshtein("spam", "SPAM", 1) == 4
    assert levenshtein("spam", "SPAM", 1, max_distance=2) == 2
    assert levenshtein("GUMBO", "GAMBOL", w_insert=10) == 11
    assert levenshtein("GUMBO", "GAMBOL", w_insert=10, w_replace=2) == 12
    assert levenshtein("spam", "ham", w_replace=2) == 3
    assert levenshtein("spam", "ham", w_delete=10, w_replace=2) == 12
    assert (levenshtein("xyz", "abcde", w_insert=0, w_delete=0, w_replace=0)
            == 0)
    print "No errors with Levenshtein edit distance."
    print "========================================================"
    print "Verifying custom Levenshtein edit distance:"
    l = LevenshteinCustomWeights()
    assert l.levenshtein("ANT", "AUNT") == 1
    l = LevenshteinCustomWeights(delete_map={"A": 10})
    assert l.levenshtein("ANT", "AUNT") == 1
    l = LevenshteinCustomWeights(insert_map={"U": 10}, w_replace=20)
    assert l.levenshtein("ANT", "AUNT") == 10
    l = LevenshteinCustomWeights(replace_map={("A", "B"): 0.25})
    assert l.levenshtein("AAA", "BB") == 1.5
    l = LevenshteinCustomWeights(replace_map={("A", "B"): 0.25}, w_insert=0.5)
    assert l.levenshtein("AA", "BBB") == 1
    l = LevenshteinCustomWeights(replace_map={("A", "B"): 0.5})
    assert l.levenshtein("AAA", "BBB") == 1.5
    print "No errors with custom Levenshtein edit distance."


if __name__ == "__main__":
    verify()
