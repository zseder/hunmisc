def clean_utf8_accents(s):
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

def change_utf_to_proszeky(s):
    s = s.replace(u"\u00C1", u"A1")
    s = s.replace(u"\u00C9", u"E1")
    s = s.replace(u"\u00CD", u"I1")
    s = s.replace(u"\u00D3", u"O1")
    s = s.replace(u"\u00D6", u"O2")
    s = s.replace(u"\u0150", u"O3")
    s = s.replace(u"\u00DA", u"U1")
    s = s.replace(u"\u00DC", u"U2")
    s = s.replace(u"\u0170", u"U3")
    
    s = s.replace(u"\u00E1", u"a1")
    s = s.replace(u"\u00E9", u"e1")
    s = s.replace(u"\u00ED", u"i1")
    s = s.replace(u"\u00F3", u"o1")
    s = s.replace(u"\u00F6", u"o2")
    s = s.replace(u"\u0151", u"o3")
    s = s.replace(u"\u00FA", u"u1")
    s = s.replace(u"\u00FC", u"u2")
    s = s.replace(u"\u0171", u"u3")
    return s

if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-c", "--clean", action="store_true", default=False, dest="clean",
                  help="fix hungarian characters coded with umlaut and tilde")
    parser.add_option("-p", "--pro1sze1ky", action="store_true", default=False, dest="proszeky",
                  help="change hungarian characters to proszeky coding")
    (options, args) = parser.parse_args()
    
    import sys
    for l in sys.stdin:
        l = l.decode("utf-8")
        if options.clean:
            l = clean_utf8_accents(l)
        if options.proszeky:
            l = change_utf_to_proszeky(l)
        print l.encode("utf-8"),

