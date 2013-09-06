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
#/bin/bash
language=$1
input_file=$2
output_file=$3
hunspell_path_infos=$4

hunspell=/home/zseder/.local/bin/hunspell
if [ ! -e $hunspell ];
then
    echo "needs latest hunspell, currently at nessi6:$hunspell"
    exit
fi

hunspell_path=`egrep $language $hunspell_path_infos | cut -f2` 

if [[ ${language} == "Bulgarian" ]];
then
	input_encoding=UTF-8
	output_encoding=CP1251

    hunspell_output=`mktemp`
    first_column=`mktemp`
    second_column=`mktemp`

    cat ${input_file} | iconv -f ${input_encoding} -t ${output_encoding} -c | iconv -f ${output_encoding} -t ${input_encoding} | $hunspell -d ${hunspell_path} -s -i ${input_encoding} | egrep ' ' > ${hunspell_output}
    cut -f1 -d' ' ${hunspell_output} > ${first_column}
    cut -f2 -d' ' ${hunspell_output} |  iconv -f ${output_encoding} -t ${input_encoding} > ${second_column}
    paste ${first_column} ${second_column} | sed 's/ /\t/g' > ${output_file}
    rm $hunspell_output $first_column $second_column

elif [[ ${language} == "Vietnamese" || ${language} == "Korean" ]];
then
	celkod=`grep "^SET" ${hunspell_path}.aff | head -1 | cut -f2 -d" " | sed 's/\r$//'`
	cat ${input_file} | iconv -t ${celkod} -f utf-8 -c | $hunspell -d ${hunspell_path}  -s  | egrep ' ' > ${output_file}

else	
	celkod=`grep "^SET" ${hunspell_path}.aff | head -1 | cut -f2 -d" " | sed 's/\r$//'`
	cat ${input_file} | iconv -t ${celkod} -f utf-8 -c | $hunspell -d ${hunspell_path} -s -i ${celkod} 2>${language}.hunspell.err | egrep ' ' | iconv -f ${celkod} -t utf-8 > ${output_file}
fi

