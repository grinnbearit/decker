#!/usr/bin/zsh
for file in `find $1 -name "*.txt"`
do
python gendeck.py -d $file -o $(basename ${file%.txt}).json ${@:2}
done
