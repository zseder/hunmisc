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

import matplotlib.pyplot as plt
from matplotlib import rc

def read_data(istream):
    r = [[],[],[],[],[]]
    for l in istream:
        le = l.strip().split()
        [r[i].append(le[i]) for i in xrange(len(le))]
    return r

def main():
    d = read_data(open(sys.argv[1]))
    rc('font', size=14)
    ax = plt.subplot(111)
    ax.plot(d[0], d[1], label="$M$", linewidth=2)
    ax.plot(d[0], d[2], label="$l KL$", linewidth=2)
    ax.plot(d[0], d[3], label="$l (H_q+KL)$", linewidth=2)
    ax.plot(d[0], d[4], label="$M + l (H_q+KL)$", linewidth=2)
    plt.xlabel("Bits")
    ax.legend(loc=7)
    plt.show()
    #plt.savefig("fig.png")

if __name__ == "__main__":
    main()

