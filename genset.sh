#!/usr/bin/zsh
for file in `find $1 -name "*.txt"`
do
tts-deckconverter -mode mtg -option quality=png -option rulings=true -output $2 $file
done
