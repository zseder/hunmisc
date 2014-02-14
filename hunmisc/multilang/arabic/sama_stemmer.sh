# Copyright 2011-13 Attila Zseder
# Email: zseder@gmail.com
# 
# This file is part of hunmisc project
# url: https://github.com/zseder/hunmisc
# 
# hunmisc is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
# 
# 
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

