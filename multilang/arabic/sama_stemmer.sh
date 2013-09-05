#!/usr/bin/env bash
vocab=$1

vocab_ana=`mktemp`
sama-analyze $vocab > $vocab_ana

vocab_ana_cut=`mktemp`
cat $vocab_ana | cut -f1,3 | grep "_[0-9]$" | sed "s/_[0-9]$//" | sort -u -S4G > $vocab_ana_cut
rm $vocab_ana

vocab_ana_cut_orig=`mktemp`
vocab_ana_cut_stem=`mktemp`
cut -f1 $vocab_ana_cut > $vocab_ana_cut_orig
cut -f2 $vocab_ana_cut | perl buckwalter_to_utf8.pl > $vocab_ana_cut_stem
rm $vocab_ana_cut
paste $vocab_ana_cut_orig $vocab_ana_cut_stem
rm $vocab_ana_cut_orig $vocab_ana_cut_stem

