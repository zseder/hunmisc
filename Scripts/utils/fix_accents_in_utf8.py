
def fix_utf8_accents(s):
    #o3
    s = s.replace(u"\u00F4" , u"\u0151")
    s = s.replace(u"\u00F5" , u"\u0151")
    
    #O3
    s = s.replace(u"\u00D4" , u"\u0150")
    s = s.replace(u"\u00D5" , u"\u0150")
    
    #u3
    s = s.replace(u"\u00FB" , u"\u0171")
    s = s.replace(u"\u0169" , u"\u0171")
    
    #U3
    s = s.replace(u"\u00DB" , u"\u0170")
    s = s.replace(u"\u0168" , u"\u0170")
    
    return s

if __name__ == "__main__":
    import sys
    for l in sys.stdin:
        l = l.decode("utf-8")
        l = fix_utf8_accents(l)
        print l.encode("utf-8"),
