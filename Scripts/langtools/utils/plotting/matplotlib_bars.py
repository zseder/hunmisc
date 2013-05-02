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
    data = sorted([(k, v[0], v[1], v[2]) for k, v in data.iteritems()], key=lambda x: x[2])
    #width = [float(x[2])/data[-1][2] for x in data]
    width = [0.6] * len(data)
    plt.bar(range(len(data)), [_[3] for _ in data], width=width)
    plt.xticks([n+0.3 for n in range(len(data))], [_[0] for _ in data], rotation=90)
    
    plt.savefig("fig.png", dpi=150, bbox_inches="tight")

if __name__ == "__main__":
    main()
