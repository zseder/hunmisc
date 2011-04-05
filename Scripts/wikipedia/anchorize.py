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

