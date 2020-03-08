#!/usr/bin/zsh
for file in `ls $1`
do
    output+=$(python codeck.py -d ${1}/$file -e ${@:2})
    output+="\n"
done

# remove trailing '\n'
unset 'output[${#output[@]}]'
unset 'output[${#output[@]}]'

echo "${output[@]}" | sort -r | uniq
