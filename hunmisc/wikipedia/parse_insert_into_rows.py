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

for line in sys.stdin:
    if not line.startswith("INSERT INTO"):
        continue
    
    line = line.decode("utf-8", "ignore").split("VALUES", 1)[1].strip().rstrip(";")
    entries = eval("( %s )" % line)
    for entry in entries:
        entry_elements = list(entry)
        entry_elements = [str(ee) if type(ee) != str else ee.decode("utf-8") for ee in entry_elements]
        try:
            print "\t".join([ee for ee in entry_elements]).encode("utf-8")
        except UnicodeDecodeError, ude:
            sys.stderr.write("There is an encoding problem with a link:\n")
            sys.stderr.write(str(entry).decode("utf-8", "ignore") + "\n")
