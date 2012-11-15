# coding: utf-8

# KR kódok beolvasása, a megfelelõ memóriareprezentációk megépítése.

import sys

def cerr(txt) :
    sys.stderr.write(txt+"\n")
    sys.stderr.flush()

# ÖSSZETETTKR = TELJESKR ( "+" TELJESKR )*
# TELJESKR = TÕ ( "/" DEKORÁLTKR )+
# DEKORÁCIÓ = "[" KR "]" (Regen nem igy volt, hanem egyszeruen igy: DEKORÁCIÓ = "[" VÁLTOZÓNÉV "]" )
# DEKORÁLTKR = KR ( DEKORÁCIÓ )*
# FEJ = VÁLTOZÓNÉV
# KR = FEJ ( "<" KR ">" )*
#
# TÕ = TÕBETÛ+
# VÁLTOZÓNÉV = VÁLTOZÓNÉVBETÛ+
#
# TÕBETÛ = [a-zA-Z0-9`;.@&-] vagy ami még ezen kívül eszembe jut, és nem +/[]<>
#
# VÁLTOZÓNÉVBETÛ = [A-Z0-9_-] TÕBETÛ-vel ellentétben ASCII karakterkészlet.


class Node :
    def __init__(self) :
        # self.parent = null
        self.children = []
        self.value = ""
    def __str__(self) :
        return self.value + "".join( map( lambda p : "<" + str(p) + ">" , self.children ) )


class KRCode :
    def __init__(self) :
        # krNodes[0] kepzos[1] krNodes[1] kepzos[1] rendszerben alternalnak. Pontosabban:
        # stem + "/" + str(krNodes[0]) + "[" + "][".join(kepzos[0]) + "]/" + krNodes[1] + "/" + ...
        self.stem = ""
        self.krNodes = []
        self.kepzos = [] # TODO Mi a neve?
    def __str__(self) :
        out = self.stem + "/"
        n = len(self.krNodes)
        assert n-len(self.kepzos) in (0,1)
        for i in range(n) :
            krNode = self.krNodes[i]
            out += str(krNode)
            if i<len(self.kepzos) :
                kepzoGroup = self.kepzos[i]
                out += "".join( map( lambda k : "[" + str(k) + "]", kepzoGroup ) )
            if i<n-1 :
                out += "/"
        return out

# Ha ez most C++ lenne, akkor ezt irnam:
# typedef vector<KRCode> Compound

# Kornai szerint az utolso szoosszetetel kivetelevel a tobbi nem ragozodik igazibol.
# Itt csak a vege van dekoralva:
class SimplifiedCompound :
    def __init__(self) :
        self.krCode = KRCode()
        self.modifiers = [] # (list<string>)
    def __init__(self,compound) :
        n = len(compound)
        constituentStems = []
        for i,constituent in enumerate(compound) :
            if i<n-1 :
                if len(constituent.kepzos)!=0 :
                    cerr("DATA THROWN AWAY: kepzo "+str(constituent.kepzos))
                if len(constituent.krNodes)!=1 :
                    cerr("DATA THROWN AWAY: multiple inflection "+" ".join(map(str,constituent.krNodes)) )
                if len(constituent.krNodes[0].children)!=0 :
                    cerr("DATA THROWN AWAY: complex KR-code "+str(constituent.krNodes[0]))
                    
                constituentStems.append(constituent.stem)

        self.krCode = compound[n-1]
        self.modifiers = constituentStems

def descent( code, pos, leaf ) :
    if pos==len(code) :
        return pos

    if code[pos]=="<" :
        assert leaf.value!=""
        newLeaf = Node()
        newLeaf.parent = leaf
        leaf.children.append(newLeaf)
        pos = descent( code, pos+1, newLeaf )
    elif code[pos]==">" :
        return pos+1
    else :
        # TODO A tokenizalas korabban elvegzendo, itt mar tokenvektorral kellene dolgozni.
        l = code[pos:].find("<")
        r = code[pos:].find(">")
        mx = len(code)-pos
        if l==-1 :
            l = mx
        if r==-1 :
            r = mx
        nextPos = pos+min(l,r)
        assert leaf.value==""
        leaf.value = code[pos:nextPos]
        pos = nextPos
    return descent( code, pos, leaf )

def dumpTab( node, indent ) :
    print " "*indent+node.value
    for c in node.children :
        dumpTab( c, indent+1 )

def dump( root ) :
    dumpTab( root, 0 )

def analyzeKR( code ) :
    try :
        root = Node()
        pos = descent( code, 0, root )
        assert pos==len(code)
        log = False
        if log :
            print code
            dump(root)
            print ""
    except :
        sys.stderr.write( "Invalid KR: " + code + "\n" )
        raise
    return root

def analyzeConstituent( w ) :
    #print w
    krCode = KRCode()
    tkr = w.split("/") # hundisambig: "|"
    # assert len(tkr)>1
    stem = tkr[0]
    assert( stem.find("<")==-1 )
    assert( stem.find(">")==-1 )
    assert( stem.find("[")==-1 )
    assert( stem.find("]")==-1 )
    p = stem.find("{")
    if stem[-1:]=="}" :
        assert p!=-1
        realStem = stem[:p]
        assert realStem.find("}")==-1
        decorator = stem[p+1:-1]
    else :
        assert p==-1
        realStem = stem
    
    krCode.stem = realStem
    
    for i,part in enumerate(tkr[1:]) :
        p = part.find("[")
        
        # Az uccsoban ritkan, de elofordulhat kepzo.
        # A tobbiben abszolute kotelezoen elofordul.
        if i!=len(tkr[1:])-1 :
            if p==-1 :
                cerr( "MISSING KEPZO: "+part )
            assert p!=-1
        
        if p==-1 :
            p = len(part)
	if p==0 :
	    # Megengedjuk, hogy ne legyen fokategoria, de csak az elso
	    # kepzoben. Ez igazibol nem kepzo, hanem a kepzes segitsegevel
	    # megoldott alkategoria.
	    if i!=0 :
		cerr("SUBCATEGORIZATION (empty main category) IS ONLY ALLOWED AT THE FIRST POSITION: "+part)
		assert p>0 or i==0
        krNode = analyzeKR( part[:p] )
        krCode.krNodes.append( krNode )
        # Csakis a vegen, opcionalisan lehet egy
        # ( "[" "[A-Z_]"+ "]" ) pattern.
        # TODO Valojaban egy
        # ( "[" "[A-Z_]"+ "]" )* pattern.
        kepzoGroup = []
        (START,OUT,IN) = (0,1,2)
        state = START
        pos = 0
        # Na gyakoroljuk kicsit a kezzel irt veges automatakat :)
        while pos<len(part) :
            c = part[pos]
            if state==START :
                assert c!="]"
                if c=="[" :
                    state = IN
                    kepzo = ""
            elif state==IN :
                assert c!="["
                if c=="]" :
                    state = OUT
		    # Ez 2012.07.31 elott nem igy volt,
		    # eddig a kepzonek nem volt kacsacsor-strukturaja.
		    # Most mar van:
		    parsedKepzo = analyzeKR(kepzo)
                    kepzoGroup.append(parsedKepzo)
                    kepzo = ""
                else :
                    ok = False
                    if ord(c)>=ord('A') and ord(c)<=ord('Z') :
                        ok=True
                    if ord(c)>=ord('0') and ord(c)<=ord('9') :
                        ok=True
                    if c=="_" or c=="-" :
                        ok=True
		    if c=="<" or c==">" :
			ok = True
                    if not ok :
                        raise "data error"
                    kepzo += c
            elif state==OUT :
                assert c=="["
                state = IN
            pos += 1

        assert state!=IN
        if len(kepzoGroup)>0 :
            krCode.kepzos.append(kepzoGroup)

    if w!=str(krCode) :
        cerr( w+" != "+str(krCode) )
        raise "internal error"

    return krCode

def analyze( t ) :
    compounds = t.split("+") # hundisambig: "@"
    krCodes = []

    for compoundIndex,w in enumerate(compounds) :
        krCodes.append( analyzeConstituent(w) )
    return krCodes


def main() :
    manyWordsPerLine = True
    
    if manyWordsPerLine :
        for l in sys.stdin :
            tokens = l.strip("\n").split(" ")
            if len(tokens)==1 and tokens[0]=="" :
                continue
            for token in tokens :
                analyze(token)
    else :
        # Az ocamorph standard, kacsacsõrös kimenetét vizsgálja helyesség szempontjából.
        for l in sys.stdin :
            t = l.strip("\n")
            if t[:2]=="> " :
                inputWord = t[2:]
                continue

            try :
                analyze(t)
            except :
                cerr( "BUG: "+t+" IN WORD: "+inputWord )

if __name__ == "__main__" :
    main()
