#!/usr/bin/zsh
for file in `find $1 -name "*.txt"`
do
    output+=$(python codeck.py -c $file -e ${@:2})
    output+="\n"
done

# remove trailing '\n'
unset 'output[${#output[@]}]'
unset 'output[${#output[@]}]'

echo "${output[@]}" | sort -r | uniq
