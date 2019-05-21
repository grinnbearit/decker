#!/usr/bin/zsh
for file in `ls $1`
do
python codeck.py -d ${1}/$file -c ${@:2} > /dev/shm/updateset.dat
cat /dev/shm/updateset.dat > ${1}/$file
done
