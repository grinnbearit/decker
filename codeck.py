import sys
import argparse
import decker.core as dc
import decker.codex as dx


def find_missing(cardex, deck):
    """
    returns a list of card names that aren't found in the passed cardex
    """
    return [deckline["name"] for deckline in deck if deckline["name"] not in cardex]


def print_editions(codex, cardex, deck):
    """
    prints the set of needed editions
    """
    acc = set()
    for deckline in deck:
        acc.add(list(cardex[deckline["name"]])[0])

    for row in codex:
        if row["edition"] in acc:
            edition = row["edition"]
            name = row["name"]
            date = row["date"]
            print(f"{date}, {edition}, {name}")


def print_csv(cardex, deck):
    """
    prints a deck in csv format to stdout
    """
    print("edition,name,count")

    rows = []
    for deckline in deck:
        name = deckline["name"]
        edition = list(cardex[name])[0]
        count = deckline["count"]
        print(f'"{edition}","{name}",{count}')


def print_deck(cardex, deck, all=False):
    """
    prints edition, card name pairs to stdout
    """
    for deckline in deck:
        name = deckline["name"]
        if all:
            edition_str = "[{}]".format(','.join(str(e) for e in cardex[name]))
        else:
            edition_str = cardex[name][0]
        print(f"{edition_str}, {name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", '--deck',
                        help="deck filename",
                        required=True)
    parser.add_argument("-p", "--path",
                        help="editions directory",
                        default="editions")
    parser.add_argument("-a", "--all",
                        help="list all editions",
                        action="store_true")
    parser.add_argument("-i", "--ignore",
                        help="ignored editions",
                        nargs='+')
    parser.add_argument("-n", "--newest",
                        help="newest edition to consider")
    parser.add_argument("-o", "--oldest",
                        help="oldest edition to consider")
    parser.add_argument("-c", "--csv",
                        help="print out in csv deck format (overrides --all)",
                        action="store_true")
    parser.add_argument("-e", "--editions",
                        help="prints a set of all editions used (overrides --all, --csv)",
                        action="store_true")

    args = parser.parse_args()

    deck = dc.read_deck(args.deck)
    igset = set(args.ignore) if args.ignore else set()
    codex = dx.read_codex("codex.csv")
    cardex = dx.read_cardex(args.path, codex, args.newest, args.oldest, igset)

    missing_names = find_missing(cardex, deck)
    if missing_names:
        print("{0} missing".format(len(missing_names)))
        for name in missing_names:
            print(f"{name}")
        exit(1)

    if args.editions:
        print_editions(codex, cardex, deck)
    elif args.csv:
        print_csv(cardex, deck)
    else:
        print_deck(cardex, deck, args.all)
