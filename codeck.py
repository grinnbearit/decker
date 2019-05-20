import sys
import csv
import argparse
import decker.core as dc


def find_missing(codex, deck):
    """
    returns a list of card names that aren't found in the passed codex
    """
    return [card["name"] for card in deck if card["name"] not in codex]


def print_csv(codex, deck):
    """
    prints a deck in csv format to stdout
    """
    rows = []
    for card in deck:
        card["edition"] = codex[card["name"]][0]
        rows.append(card)

    print("edition,name,count")
    writer = csv.DictWriter(sys.stdout, fieldnames=["edition", "name", "count"], quoting=csv.QUOTE_NONNUMERIC)
    writer.writerows(rows)


def print_edition(codex, deck, all=False):
    """
    prints a edition, card pairs to stdout
    """
    for card in deck:
        name = card["name"]
        if all:
            edition_str = "[{}]".format(','.join(str(e) for e in codex[name]))
        else:
            edition_str = codex[name][0]
        print(f"{edition_str}, {name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", '--deck',
                        help="deck filename",
                        required=True)
    parser.add_argument("-s", "--sets",
                        help="sets directory",
                        default="sets")
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

    args = parser.parse_args()

    deck = dc.read_deck(args.deck)
    edset = set(args.ignore) if args.ignore else set()
    codex = dc.read_codex(args.sets, args.newest, args.oldest, edset)

    missing_cards = find_missing(codex, deck)
    if missing_cards:
        print("{0} missing".format(len(missing_cards)))
        for card in missing_cards:
            print(f"{card}")
        exit(1)

    if args.csv:
        print_csv(codex, deck)
    else:
        print_edition(codex, deck, args.all)
