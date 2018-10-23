# Decker

Generates image sheets for [Magic the Gathering](http://magic.wizards.com/), handles decks and drafts.

## Usage

`python fetchdeck.py -d <deck.csv> -o <output.png> [-t] [-f <sheet format>]`

Constructs a deck using the scryfall api

`python fetchset.py -e edition`

Pulls an entire set from scryfall and creates an index for cards to images

`python gendeck.py -d <deck.csv> -o <output.png> [-t] [-s <sets>] [-f <sheet format>]`

Constructs a deck using the downloaded set index

`python gendraft.py -d <deck.csv> -o <output.png> [-t] [-s <sets>] [-d <draft.json>] [-f <sheet format>]`

Simulates a draft using the downloaded set index, the draft structure is taken from a json file,
"winchestor.json" is an example

### Decks

Decks should be csv files with rows `(edition, name, count)`

#### MtG Card Back
* [option 1](https://www.slightlymagic.net/forum/download/file.php?id=11045&mode=view)
* [option 2](https://i.imgur.com/P7qYTcI.png)

## License

Copyright © 2018 Sidhant Godiwala (grinnbearit)

Distributed under the Eclipse Public License, the same as Clojure.
