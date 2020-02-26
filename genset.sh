#!/usr/bin/zsh
for file in `ls $1`
do
python gendeck.py -d ${1}/$file -o ${file%.csv}.png ${@:2}
done
