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


#!/usr/bin/env python
"""Scatter plot with different colors and sizes and limits
"""

import math
import sys

from pylab import scatter, legend, grid, show, xlim, ylim

def plot_data(data):
    props = dict( alpha=0.5, edgecolors='none' )

    handles = []
    classes = list(set([x[2] for x in data]))
    colours = ["green", "red", "blue", "black", "orange"]
    for class_, colour in zip(classes, colours):
        class_data = [a for a in data if a[2] == class_]
        if len(class_data) == 0:
            continue
        x = [math.log(1.0 + float(a[3]), 10) for a in class_data]
        y = [math.log(1.0 + float(a[1]), 10) for a in class_data]
        s = [max(400*float(a[4]), 20.0) for a in class_data]
        handles.append(scatter(x, y, c=colour, s=s, **props))

    legend(handles, [c.upper() for c in classes], loc=4)
    xlim(-0.3, 9.5)
    ylim(-0.3, 11.0)
    grid(True)

    show()

def read_data(istream):
    d = []
    for l in istream:
        d.append(l.strip().split("\t"))
    return d

def main():
    data = read_data(open(sys.argv[1]))
    plot_data(data)

if __name__ == "__main__":
    main()
