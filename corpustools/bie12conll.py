#!/usr/bin/python -u

import sys
import optfunc

def transform(s_const, c, dontDoBIE1ToBI=False, dontDoNbarToNP=False,
              dontDoNplusToNbar=False) :
    s = s_const
    if s!="O" :
        if s[1]!="-" :
            raise ValueError( "Malformed tag: "+s+'\nLine: '+str(c))
        
        if not dontDoNplusToNbar:
          s=s.strip('+')
        
        if not dontDoNbarToNP :
            a = s.split("_")
            if len(a)!=2 :
                raise ValueError( "Malformed tag: "+s+'\nLine: '+str(c))
            s = a[0]+"P"
        if not dontDoBIE1ToBI :
            if s[0]=="1" :
                s = "B" + s[1:]
            if s[0]=="E" :
                s = "I" + s[1:]
    return s

def main( dontDoBIE1ToBI=False, dontDoNbarToNP=False, dontDoNplusToNbar=False, fields="-2,-1" ) :
    fieldList = map( int, fields.split(",") )
    lengthSet = set()
    line = sys.stdin.readline()
    c=0
    while line :
        c+=1
        a = line.strip().split()
        if len(a)==0 :
            print
        else :
            assert len(a)>=2
            lengthSet.add(len(a))
            if len(lengthSet)>1 :
                raise ValueError("Column number differs from those of" +
                                 "previous lines: {0}".format(line))
            for ind in fieldList :
                a[ind] = transform(a[ind], c, dontDoBIE1ToBI, dontDoNbarToNP, dontDoNplusToNbar)
            print "\t".join(a)
        line = sys.stdin.readline()

if __name__ == '__main__':
    optfunc.run(main)

