# Decker (simplified)

Converts cardlists (name, count) tuples to mtga decks, integrates with [tts-deckconverter](https://github.com/jeandeaual/tts-deckconverter/releases)

## Usage

`python fetchset.py -e <edition> [-p <metadata directory>]`

downloads edition metadata

`python codeck.py -c <cardlist.csv> [-p <metadata directory] [-n <newest set>] [-o <oldest set>] [-e <print editions needed>]`

converts a card list to mtga deck format, uses the most recent card given edition filters

### Making it Easier

`./checkset.sh <directory> [-n <newest set>] [-o <oldest set>] [-i <ignore sets>]`

Checks for missing cards and required sets for all cardlists in a directory

`./updateset.sh <directory> [-n <newest set>] [-o <oldest set>] [-i <ignore sets>]`

Updates the cardlist files in a directory as mtga deck files

`./genset.sh <directory> <output directory>`

Generates all decks in a directory using tts-deckconverter

## License

Copyright © 2020 Sidhant Godiwala (grinnbearit)

Distributed under the Eclipse Public License, the same as Clojure.
