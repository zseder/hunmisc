#unicode-proszeky map
upm = unicode_proszeky_map = {
    u"\u00C1": u"A1",
    u"\u00C9": u"E1",
    u"\u00CD": u"I1",
    u"\u00D3": u"O1",
    u"\u00D6": u"O2",
    u"\u0150": u"O3",
    u"\u00DA": u"U1",
    u"\u00DC": u"U2",
    u"\u0170": u"U3",
    u"\u00E1": u"a1",
    u"\u00E9": u"e1",
    u"\u00ED": u"i1",
    u"\u00F3": u"o1",
    u"\u00F6": u"o2",
    u"\u0151": u"o3",
    u"\u00FA": u"u1",
    u"\u00FC": u"u2",
    u"\u0171": u"u3"
}

#proszeky-unicode map
pum = proszeky_unicode_map = dict([(i[1], i[0]) for i in upm.items()])

def clean_unicode_accents(s):
    """Changing not proper accents (tildes and umlauts) to the proper
    hungarian accents in unicode strings"""
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

def encode_to_proszeky(s, cleaning=False):
    """unicode 2 proszeky"""
    # accent cleaning (umlauts, tildes and more)
    if cleaning:
        s = clean_unicode_accents(s)

    # escaping bigrams already in proszeky
    for k in pum.keys():
        s = s.replace(k, k[0] + "%uniq_proszeky_string%" + k[1])

    # proszeky replacing
    for k in upm.keys():
        s = s.replace(k, upm[k])

    # remove escapes
    s = s.replace("%uniq_proszeky_string%", "")
    return s

def decode_from_proszeky(s):
    """proszeky 2 unicode"""
    for k in pum.keys():
        s = s.replace(k, pum[k])
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
            l = clean_unicode_accents(l)
        if options.proszeky:
            l = encode_to_proszeky(l)
        print l.encode("utf-8"),

