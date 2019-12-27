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

`python codeck.py -d <deck.csv> [-s <sets>] [-a <all possible sets>] [-i <ignore sets>] [-n <newest set>] [-o <oldest set>] [-c <print in csv format>] [-e <print editions needed>]`

Checks a deck, using codex.csv, for missing cards as well as the sets required.

### Making it Easier

`./checkset.sh <directory> [-n <newest set>] [-o <oldest set>] [-i <ignore sets>]`

Checks for missing cards and required sets for all decks in a directory

`./updateset.sh <directory> [-n <newest set>] [-o <oldest set>] [-i <ignore sets>]`

Updates the deck files in a directory with the latest required set

`./genset.sh`

Generates all decks in a directory

### Decks

Decks should be csv files with rows `(edition, name, count)`

#### MtG Card Back
* [option 1](https://www.slightlymagic.net/forum/download/file.php?id=11045&mode=view)
* [option 2](https://i.imgur.com/P7qYTcI.png)

## License

Copyright © 2018 Sidhant Godiwala (grinnbearit)

Distributed under the Eclipse Public License, the same as Clojure.
