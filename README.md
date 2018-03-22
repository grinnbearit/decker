# Decker

Generates image sheets for printing card games like [Magic the Gathering](http://magic.wizards.com/) and [Netrunner](https://www.fantasyflightgames.com/en/products/android-netrunner-the-card-game/).

## Usage

`python gendeck.py [-s <sheet type>] -d <deck.csv> -o <output.png> [-t]`


If there are multiple sheets generated, they'll be saved as `0_output.png`, `1_output.png` etc

-t indicates `test mode` which checks which cards can be fetched or not returning "ok" if all
can be fetched or a list of missing cards if they can't

### Decks

Decks should be csv files with rows `(number_of_copies, card_name [, edition])`

#### MtG Card Back
* [option 1](https://www.slightlymagic.net/forum/download/file.php?id=11045&mode=view)
* [option 2](https://i.imgur.com/P7qYTcI.png)

## License

Copyright © 2017 Sidhant Godiwala (grinnbearit)

Distributed under the Eclipse Public License, the same as Clojure.
