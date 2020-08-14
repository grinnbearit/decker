import re
import json
import argparse
import decker.tts as dt
import decker.core as dc
import decker.codex as dx
import decker.edition as de


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


def is_edition_highres(path, edition):
    """
    returns True if all token cards have highres prints
    """
    for card in de.read_edition(path, edition):
        if card["layout"] in ["token", "emblem", "double_faced_token"]:
            if not card["highres_image"]:
                return False
    return True


def escape_name(name):
    filled = re.sub("\s", "_", name)
    return re.sub("[^\w\d_]", "", filled.lower())


def gen_token_deck(path, edition):
    """
    returns all token cards in an edition as a deck
    """
    deck = []
    for card in de.read_edition(path, edition):
        if card["layout"] in ["token", "emblem", "double_faced_token"]:
            deckline = {"count": 1,
                        "name": card["name"],
                        "edition": edition,
                        "collector_number": card["collector_number"]}
            deck.append(deckline)
    return deck


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path",
                        help="editions directory",
                        default="editions")
    parser.add_argument("-l", "--lowres",
                        help="generates a deck with low res images," +\
                        " if no high res available",
                        action="store_true")
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
    igset = set(args.ignore) if args.ignore else set()
    codex = dx.read_codex("codex.csv")
    editions = dx.filter_editions(codex, args.newest, args.oldest, igset)

    if args.editions:
        print_editions(codex, editions)
        exit(0)

    if not args.lowres:
        for edition in editions:
            if not is_edition_highres(args.path, edition):
                print(f"not all tokens in {edition} have highres prints")
                exit(1)

    index = dc.read_index(args.path, editions)
    tokex = dc.read_tokex(args.path, editions)
    for (name, indices) in tokex.items():
        deck = []
        for (edition, collector_number) in indices:
            deckline = {"count": 1,
                        "name": name,
                        "edition": edition,
                        "collector_number": collector_number}
            deck.append(deckline)

        ttsdeck = dt.deck_to_ttsdeck(index, deck)
        escaped = escape_name(name)
        with open(f"{escaped}.json", "w") as fp:
            json.dump(ttsdeck, fp, indent=True)
