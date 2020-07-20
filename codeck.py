import sys
import argparse
import decker.core as dc
import decker.codex as dx


def find_missing(cardex, cardlist):
    """
    returns a list of card names that aren't found in the passed cardex
    """
    return [cardline["name"] for cardline in cardlist if cardline["name"] not in cardex]


def print_editions(codex, editions):
    """
    prints the set of needed editions from newest to oldest
    """
    for row in codex:
        if row["edition"] in editions:
            edition = row["edition"]
            name = row["name"]
            date = row["date"]
            print(f"{date}, {edition}, {name}")


def print_deck(deck):
    """
    prints the deck in mtgo format
    """
    for deckline in deck:
        count = deckline["count"]
        name = deckline["name"]
        edition = deckline["edition"].upper()
        collector_number = deckline["collector_number"]
        print(f"{count} {name} ({edition}) {collector_number}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", '--cards',
                        help="file containing list of cards with counts",
                        required=True)
    parser.add_argument("-p", "--path",
                        help="editions directory",
                        default="editions")
    parser.add_argument("-i", "--ignore",
                        help="ignored editions",
                        nargs='+')
    parser.add_argument("-n", "--newest",
                        help="newest edition to consider")
    parser.add_argument("-o", "--oldest",
                        help="oldest edition to consider")
    parser.add_argument("-e", "--editions",
                        help="prints a set of all editions used",
                        action="store_true")


    args = parser.parse_args()

    cardlist = dx.read_cardlist(args.cards)
    igset = set(args.ignore) if args.ignore else set()
    codex = dx.read_codex("codex.csv")
    cardex = dx.read_cardex(args.path, codex, args.newest, args.oldest, igset)

    missing_names = find_missing(cardex, cardlist)
    if missing_names:
        print("{0} missing".format(len(missing_names)))
        for name in missing_names:
            print(f"{name}")
        exit(1)

    editions = dx.list_editions(cardex, cardlist)
    if args.editions:
        print_editions(codex, editions)
    else:
        index = dc.read_index(args.path, editions)
        deck = dx.cardlist_to_deck(cardex, index, cardlist)
        print_deck(deck)
