#!/usr/bin/zsh
for file in `ls $1`
do
    output+=($(python codeck.py -d ${1}/$file -e ${@:2}))
done
printf '%s\n' "${(u)output[@]}"
