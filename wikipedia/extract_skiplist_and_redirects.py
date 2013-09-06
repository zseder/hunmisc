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
Extracts the skiplist and the redirect pages from the pages file.

To create the pages file from the sql, run parse_insert_into_rows.py.
"""
import sys

def extract_skiplist_and_redirects(pages_name, skiplist_name, redirect_name):
    with open(pages_name, 'r') as pages_file, open(skiplist_name, 'w') as skiplist_file, open(redirect_name, 'w') as redirect_file:
        for line in pages_file:
            fields = line.strip().split("\t")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "Usage: {0} pages_file skiplist redirect_file\n".format(__file__)
        print "Where: pages_file: the input file;"
        print "       skiplist: pages not in the main namespace are written here;"
        print "       redirect_file: redirect pages are written here.\n"
        sys.exit(1)

    do_it(*sys.argv[1:])

