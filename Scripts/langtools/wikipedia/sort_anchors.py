"""
input: tab separated lines, 6 fields, sorted by first field
(output of achorize.py)
1. Target page
2. Src page
3. Anchor text
4. link tag
5. POS tag
8. stemmed anchor
"""
import sys

actual_page = None
if __name__ == "__main__":
    for line in sys.stdin:
        le = line.strip().split("\t")
        if actual_page is None:
            actual_page = le[0], [le[1:]]
        elif actual_page[0] != le[0]:
            print "%%#PAGE {0}".format(actual_page[0])
            for l in actual_page[1]:
                print "\t".join(l)
            print
            actual_page = le[0], [le[1:]]
        else:
            actual_page[1].append(le[1:])

    print "%%#PAGE {0}".format(actual_page[0])
    for l in actual_page[1]:
        print "\t".join(l)
    print


