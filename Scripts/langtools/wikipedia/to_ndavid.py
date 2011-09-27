import sys
"""
This script reads normal parsed Wikipedia pages in Conll-like format
and transforms it to format needed by ndavid
"""

from nltk_tools import NltkTools
nt = NltkTools(tok=True, pos=True, stem=True)

pageSep = "%%#PAGE"
actPage = None
starter = False
for line in sys.stdin:
    l = line.strip().decode("utf-8")
    if l.startswith(pageSep):
        if actPage is not None:
            print
        
        actPage = l.split(" ", 1)[1]
        starter = True
        print l.encode("utf-8").replace(" ", "\t", 1)
        print "%%#Field\tTitle"
        titleTokens = nt.word_tokenize(actPage)
        titleTokensWithPos = list(nt.pos_tag(titleTokens))
        stemmedTitleTokens = nt.stem(titleTokensWithPos)
        hardStemmedTitleTokens = list(nt.stem(((x[0][0].tolower() + x[0][1:] if x[0][0].isupper() and x[0][1:].islower() else x[0]), x[1]) for x in titleTokensWithPos))
        for i, (tok, pos, stem) in enumerate(stemmedTitleTokens):
            print u"{0}\t{1}\t{2}\t{3}\t{4}\t{5}".format(tok, "word", "0", pos, stem, hardStemmedTitleTokens[i][2]).encode("utf-8")
        print
    elif starter and l.startswith("Templates:"):
        try:
            templates = l.split("\t", 1)[1]
            print u"%%#Templates\t{0}".format(templates).encode("utf-8")
        except IndexError:
            pass
    elif starter and l.startswith("REDIRECT"):
        print "%%#Redirect"
    else:
        if starter:
            print "%%#Field\tBody"
            starter = False
        print l.encode("utf-8")

