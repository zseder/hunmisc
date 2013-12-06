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


## TODO: merge with anchorize.py!
import sys
from langtools.utils import cmd_utils
from langtools.utils import file_utils

pagesep = "%%#PAGE"
anchor  = "%%#Field\tAnchor\n"

def filter(filter_files):
    bad_pages = set()
    for filter_file in filter_files:
        fin = file_utils.FileReader(filter_file).open()
        for line in fin:
            bad_pages.add(line.strip())
        fin.close()
    return bad_pages

if __name__ == '__main__':
    try:
        params, args = cmd_utils.get_params(sys.argv[1:], 'i:f:', 'if', 0)
    except ValueError as err:
        sys.stderr.write("Error: {0}\n".format(err))
        sys.stderr.write("Splits the anchor file(s) to two: one that lists the "
            + "redirect and disambiguation links, and one that lists the anchors"
            + " in the \"real\" pages. The files should be in utf-8.\n")
        sys.stderr.write("Usage: {0} -i input_file+ -f filter_file+\n")
        sys.stderr.write("       input_file: the input file to split\n")
        sys.stderr.write("       filter_file: a file that lists redirect or "
                         + "disambiguation pages, one page a line\n")
        sys.exit()
    
    bad_pages = filter(params['f'])
    for infile in params['i']:
        fin = file_utils.FileReader(infile).open()
        good_out = file_utils.FileWriter(infile + 'good', 'w').open()
        bad_out = file_utils.FileWriter(infile + 'bad', 'w').open()
        curr_out = good_out
        for line in fin:
            l = line.strip()
            if l.startswith(pagesep):
                page = l[8:]
                curr_out = bad_out if page in bad_pages or 'disambig' in page else good_out
                curr_out.write(u"{0}\n".format(l))
                curr_out.write(anchor)
            else:
                curr_out.write(u"{0}\n".format(l))
        good_out.close()
        bad_out.close()
        fin.close()

