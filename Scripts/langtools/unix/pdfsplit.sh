#!/bin/sh
input=$1
outname=`basename .pdf $2`
if [ $# -eq 4 ]; then
    start=$3
    end=$4
    for i in `seq $start $end`; do
        ii=`printf %03d $i`
        gs -sDEVICE=pdfwrite -dSAFER -dFirstPage=$i -dLastPage=$i -o $outname.$ii.pdf $input
    done
else
    gs -sDEVICE=pdfwrite -dSAFER -o $outname.%03d.pdf $input
fi
