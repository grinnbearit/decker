#!/usr/bin/zsh
for file in `find $1 -name "*.txt"`
do
python codeck.py -c $file ${@:2} > /dev/shm/updateset.dat
cat /dev/shm/updateset.dat > $file
done
