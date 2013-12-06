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


import re

# for detecting encoding/charset in htmls
charset_pattern = re.compile(r"charset=([a-zA-Z0-9\-]+)")

# for detecting, where is the problem in one encoding, based on
# Unicode{Encode,Decode}Error.msg
position_interval_pattern = re.compile(r"position ([0-9]*)-([0-9]*)")
position_pattern = re.compile(r"position ([0-9]*):")


# common hungarian encodings enumerated
_common_hungarian_encodings = ["utf-8", "LATIN1", "LATIN2", "windows-1250",
                                 "windows-1252"]

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

def detect_encoding_in_html(html):
    """regex matching for html charset"""
    s = charset_pattern.search(html)
    if s is not None:
        return s.group(1)
    return None

def guess_encoding_in_html(t, possible_encodings=_common_hungarian_encodings):
    """Guess html encoding (usually if not detected) based on encoding
    error counts and a list of @possible_encodings"""
    d = {}
    for pe in possible_encodings:
        value = count_encoding_errors(t, pe)
        if len(d) > 0:
            m = min(d.values())
            if value < m:
                d.clear()
                d[pe] = value
            elif value == m:
                d[pe] = value
        else:
            d[pe] = value
    if len(d) == 1:
        return d.keys()[0]
    else:
        pos = [(k,possible_encodings.index(k)) for k in d.keys()]
        pos.sort(key=lambda x: x[1])
        return pos[0][0]

def count_encoding_errors(t, enc):
    """Counts encoding errors in t text for enc encoding"""
    c = 0
    while True:
        try:
            t = t.decode(enc)
            break
        except LookupError:
            return len(t)
        except UnicodeError, e:
            msg = str(e)
            s = position_interval_pattern.search(msg)
            if s is not None:
                start, stop = int(s.group(1)), int(s.group(2))
                t = t[stop+1:]
                c += 1
            else:
                s = position_pattern.search(msg)
                if s is not None:
                    pos = int(s.group(1))
                    t = t[pos+1:]
                    c += 1
                else:
                    raise e
    return c

def decode_html_text(text):
    """decodes html text based on possible encodings and encoding errors"""
    enc = detect_encoding_in_html(text)
    if enc is not None:
        res = count_encoding_errors(text, enc)
        if res > 10:
            guessed = guess_encoding_in_html(text)
            enc = guessed
    else:
        enc = guess_encoding_in_html(text)
    decoded_text = text.decode(enc, "ignore")
    return decoded_text

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

