import sys

for l in sys.stdin:
    s = l.strip()
    print unichr(int(float.fromhex(s))).encode("utf-8")
