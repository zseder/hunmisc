#/bin/bash
language=$1
input_file=$2
output_file=$3
hunspell=/home/zseder/.local/bin/hunspell
if [ ! -e $hunspell];
then
    echo "needs latest hunspell, currently at nessi6:$hunspell"
    exit
fi

if [[ ${language} == "Bulgarian" ]];
then
	input_encoding=UTF-8
	output_encoding=CP1251

    hunspell_output=`mktemp`
    first_column=`mktemp`
    second_column=`mktemp`

    cat ${input_file} | iconv -f ${input_encoding} -t ${output_encoding} -c | iconv -f ${output_encoding} -t ${input_encoding} | $hunspell -d /mnt/store/home/hlt/Language/Multi/hunspell_dicts/${language}/${language} -s -i ${input_encoding} | egrep ' ' > ${hunspell_output}
    cut -f1 -d' ' ${hunspell_output} > ${first_column}
    cut -f2 -d' ' ${hunspell_output} |  iconv -f ${output_encoding} -t ${input_encoding} > ${second_column}
    paste ${first_column} ${second_column} | sed 's/ /\t/g' > ${output_file}
    rm $hunspell_output $first_column $second_column

elif [[ ${language} == "Vietnamese" || ${language} == "Korean" ]];
then
	celkod=`grep "^SET" /mnt/store/home/hlt/Language/Multi/${language}/${language}.aff | head -1 | cut -f2 -d" " | sed 's/\r$//'`
	cat ${input_file} | iconv -t ${celkod} -f utf-8 -c | $hunspell -d /mnt/store/home/hlt/Language/Multi/hunspell_dicts/${language}/${language} -s  | egrep ' ' > ${output_file}

else	
	celkod=`grep "^SET" /mnt/store/home/hlt/Language/Multi/${language}/${language}.aff | head -1 | cut -f2 -d" " | sed 's/\r$//'`
	cat ${input_file} | iconv -t ${celkod} -f utf-8 -c | $hunspell -d /mnt/store/home/hlt/Language/Multi/hunspell_dicts/${language}/${language} -s -i ${celkod} 2>${language}.hunspell.err | egrep ' ' | iconv -f ${celkod} -t utf-8 > ${output_file}
fi

