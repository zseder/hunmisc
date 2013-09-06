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


import sys
import codecs

pagesep = "%%#PAGE"

actual_page = None

for line in sys.stdin:
    l = line.strip().decode("utf-8")
#    l = line.strip()
    
    if l.startswith(pagesep):
        actual_page = l.split(" ", 1)[1]
        continue
    
    le = l.split("\t")
    if len(le) != 5:
        continue
    if le[1].endswith("link"):
        sys.stdout.write(u"{0}\t{1}\t{2}\n".format(le[2], actual_page, "\t".join(le[:2]+le[3:])).encode("utf-8"))
#        sys.stdout.write("{0}\t{1}\t{2}\n".format(le[2], actual_page, "\t".join(le[:2]+le[3:])))

