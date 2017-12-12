# Decker

Generates image sheets for printing card games like [Magic the Gathering](http://magic.wizards.com/) and [Netrunner](https://www.fantasyflightgames.com/en/products/android-netrunner-the-card-game/).

## Usage

`python gendeck.py -d <deck.csv> -o <output.png>`


If there are multiple sheets generated, they'll be saved as `0_output.png`, `1_output.png` etc

### Decks

Decks should be csv files with rows `(number_of_copies, card_name)`

## License

Copyright © 2017 Sidhant Godiwala (grinnbearit)

Distributed under the Eclipse Public License, the same as Clojure.
