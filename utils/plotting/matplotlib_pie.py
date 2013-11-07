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


"""Simple bar fig with matplotlib"""

import sys

import matplotlib.pyplot as plt

def read_data(istream):
    d = {}
    for l in istream:
        le = l.strip().split()
        d[le[0]] = [float(_) for _ in le[1:]]
    return d

def main():
    data = read_data(open(sys.argv[1]))
    #ax.scatter([_[0] for _ in data.itervalues()],
            #[_[1] for _ in data.itervalues()],
            #c='r')
    data = sorted([(k, v[0]) for k, v in data.iteritems()], key=lambda x: x[1], reverse=True)[:20]
    labels = [k for k, v in data]
    sizes = [v for k, v in data]
    sumsizes = sum(sizes)
    relsizes = [v / sumsizes for v in sizes]
    explode = [0.0 for _ in sizes]
    plt.pie(relsizes, explode=explode, labels=labels, autopct='%1.1f%%', startangle=90)
    # Set aspect ratio to be equal so that pie is drawn as a circle.
    plt.axis('equal')
    
    plt.savefig("fig.png", dpi=150, bbox_inches="tight")

if __name__ == "__main__":
    main()
