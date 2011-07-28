"""Levenshtein and Hamming edit distances for strings.

The distance between two strings is conceptually the number of places that one or
the other string needs to be changed to turn it into the other, much like those
word games where you have to turn "BROWN" into "ORANGE" one letter at a time.

(BROWN -> BRAWN -> BRAN -> GRAN -> RANG -> RANGE -> ORANGE)

The Hamming distance is a very simple measure of string distance. It simply counts 
how many characters are different between the two strings, which must be of equal 
length.

The Levenshtein distance (otherwise known as simply "edit distance") is a more
sophisticated measure of string difference. It measures the similarity between two 
strings. The distance is the number of deletions, insertions, or substitutions 
required to transform one string into the other. The greater the Levenshtein 
distance, the more different the strings are.

See:
http://en.wikipedia.org/wiki/Levenshtein_distance
http://www.merriampark.com/ld.htm
http://www.cut-the-knot.org/do_you_know/Strings.shtml

To be a measure of distance in a metric space, the measurement must be symmetrical
-- that is, distance(string1, string2) must equal distance(string2, string1). This 
is true for both Hamming and Levenshtein.

(Not all spaces are metric spaces. For instance, in a city with one-way streets, it
is not always true that distance-as-the-car-drives between points A and B is the 
same in both directions.)

Copyright (c) 2005 Steven D'Aprano.
Released under the same license as used by Python 2.3.2 itself. 
See http://www.python.org/psf/license.html for details, and 
http://www.python.org/2.3.2/license.html for the full text of the license.
"""



def hamming(s1, s2, case_sensitive=0):
	"""Hamming distance between two strings.

	s1 and s2 should be two equal-length strings. Returns an integer count of the
	number of places the strings differ, that is, the number of substitutions needed
	to change one string into the other. A Hamming distance of zero implies the 
	strings are the same; the higher the distance, the more different they are.

	If case_sensitive is false (the default), comparisons are case insensitive. 
	Case sensitive comparisons only consider standard ASCII upper/lower case and 
	are not internationalised.
	"""
	if len(s1) != len(s2):
		raise ValueError("Hamming edit distance is only defined for equal-length strings.")
	if not case_sensitive:
		s1 = s1.upper()
		s2 = s2.upper()
	return sum([c != k for c,k in zip(s1,s2)])



def levenshtein(s1, s2, case_sensitive=0):
	"""Levenshtein edit distance between two strings.

	s1 and s2 should be two arbitrary length strings. Returns an integer count of the
	edit distance between the strings, that is, the number of insertions, deletions and
	substitutions needed to change one string into the other. A Levenshtein distance of
	zero implies the strings are the same; the higher the distance, the more different 
	the strings are.

	If case_sensitive is false (the default), comparisons are case insensitive. Case sensitive 
	comparisons only consider standard ASCII upper/lower case and are not internationalised.
	"""
	m = len(s1)
	n = len(s2)
	if m == 0:
		return n
	if n == 0:
		return m
	# There is a small, but significant difference in performance depending on which 
	# string is longer, especially for very long strings. Swap the order of the strings 
	# so that s1 is the shorter.
	if n < m:
		s1, s2 = s2, s1
		m, n = n, m
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
		array[0][i] = i
	# Initialize the first column to 0..m.
	for i in range(m+1):
		array[i][0] = i

	# Measure the differences.
	# Loop over the rows and columns of the array, skipping the first of each.
	# Remember that rows = 0..m and columns = 0..n.
	for row in range(1, m+1):
		c1 = s1[row - 1]
		for col in range(1, n+1):
			c2 = s2[col - 1]
			# If the characters are the same, the cost is 0, otherwise it is 1.
			cost = 1 - int(c1==c2)
			x = array[row-1][col] + 1  # Cell immediately above plus one.
			y = array[row][col-1] + 1  # Cell immediately to the left plus one.
			z = array[row-1][col-1] + cost  # Cell diagonally above and to the left, plus the cost.
			array[row][col] = min(x, y, z)
	# When done, the bottom-right cell contains the Levenshtein distance.
	return array[-1][-1]



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
	print "No errors with Levenshtein edit distance."



if __name__ == "__main__":
	verify()


