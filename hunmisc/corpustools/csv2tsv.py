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


"""This script converts csv to tsv, and that is not that simple as it seems,
because csv can have commas in double quotes

"""
import sys

def parse_csv(s):
    s = s.strip()
    start_dquote_index = s.find("\"")
    # look for double quote intervals
    while start_dquote_index >= 0:
        end_dquote_index = s.find("\"", start_dquote_index + 1)

        # replace commas inside double quotes
        s = (s[:start_dquote_index] +
             s[start_dquote_index:end_dquote_index+1].replace(",", "<comma>") +
             s[end_dquote_index+1:])
        new_end_dquote_index = s.find("\"", start_dquote_index + 1)
        start_dquote_index = s.find("\"", new_end_dquote_index + 1)

    # replace <comma> with real comma
    return [v.replace("<comma>", ",") for v in s.split(",")]

def to_tsv(l):
    return "\t".join(l)

def main():
    for l in sys.stdin:
        print to_tsv(parse_csv(l))

if __name__ == "__main__":
    main()
