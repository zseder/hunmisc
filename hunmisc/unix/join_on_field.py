import sys

file1 = sys.argv[1]
file2 = sys.argv[2]
field1 = int(sys.argv[3])
field2 = int(sys.argv[4])

d = {}
for line in file(file1):
    le = line.strip().split("\t")
    d[le[field1]] = le[:field1] + le[field1 + 1:]

for line in file(file2):
    try:
        le = line.strip().split("\t")
        if len(le) < 2: continue
        other = d[le[field2]]
        to_print = other + le[:field2] + le[field2 + 1:]
        print "%s\t%s" % (le[field2], "\t".join(to_print))
    except KeyError:
        continue
