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
        d[le[0]] = [_ for _ in le[1:]]
    return d

def classes_pct(s):
    if float(s) > 1.0:
        return str(int(round(float(s)))) + "%"
    else:
        return ''

def c_pct(s):
    if float(s) > 10.0:
        return str(int(round(float(s)))) + "%"
    elif float(s) > 2.0:
        return '%1.1f%%' % s
    else:
        return ''

def main():
    data = read_data(open(sys.argv[1]))
    data = [(k, v[0], int(v[1])) for k, v in data.iteritems()]

    #data = sorted([v for v in data if v[1] == "c"], key=lambda x: x[2])
    #labels = [k for k, _, _ in data]
    #sizes = [v for _, _, v in data]

    sum_per_classes = {}
    for k, cl, l1 in data:
        if cl == "m": cl = "s"
        if cl == "c": cl = "t"
        sum_per_classes[cl] = sum_per_classes.get(cl, 0) + int(l1)
    labels, sizes = zip(*sorted(sum_per_classes.items(), key=lambda x: x[1]))

    sumsizes = float(sum(sizes))
    relsizes = [v / sumsizes for v in sizes]

    explode = [0.0 for _ in sizes]
    colors = ['yellowgreen', 'gold', 'lightskyblue', 'lightcoral']
    plt.pie(relsizes, explode=explode, labels=labels, autopct=classes_pct, startangle=90, colors=colors)
    labels = [(labels[li] if relsizes[li] > 0.02 else "") for li in xrange(len(labels))]
    #plt.pie(relsizes, explode=explode, labels=labels, autopct=c_pct, startangle=90, colors=colors, pctdistance=0.8, labeldistance=1.05)
    # Set aspect ratio to be equal so that pie is drawn as a circle.
    plt.axis('equal')
    
    plt.show()
    #plt.savefig("fig.png", dpi=150, bbox_inches="tight")

if __name__ == "__main__":
    main()
