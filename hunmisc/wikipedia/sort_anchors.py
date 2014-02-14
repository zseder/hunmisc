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
            print "%%#PAGE\t{0}".format(actual_page[0])
            print "%%#Field\tAnchors"
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


