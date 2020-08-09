import json
import argparse
import decker.tts as dt
import decker.core as dc
import decker.edition as de


def is_deck_highres(index, deck):
    for deckline in deck:
        card = index[deckline["edition"]][deckline["collector_number"]]
        if not card["highres_image"]:
            return False
    return True


def edition_to_deck(path, edition):
    """
    returns an entire edition as a deck
    of singletons
    """
    deck = []
    for card in de.read_edition(path, edition):
        deckline = {"count": 1,
                    "name": card["name"],
                    "edition": edition,
                    "collector_number": card["collector_number"]}
        deck.append(deckline)
    return deck


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-d", "--deck",
                       help="deck filename")
    group.add_argument("-t", "--tokens",
                       help="token edition")
    parser.add_argument("-o", "--output",
                        help="tts output",
                        required=True)
    parser.add_argument("-p", "--path",
                        help="editions directory",
                        default="editions")
    parser.add_argument("-l", "--lowres",
                        help="generates a deck with low res images," +\
                        " if no high res available",
                        action="store_true")

    args = parser.parse_args()

    if args.deck:
        deck = dc.read_deck(args.deck)
        editions = dc.deck_editions(deck)
    else:
        edition = args.tokens
        deck = edition_to_deck(args.path, edition)
        editions = [edition]

    index = dc.read_index(args.path, editions)

    if not args.lowres:
        if not is_deck_highres(index, deck):
            print(f"not all cards in {args.deck} have highres prints")
            exit(-1)

    ttsdeck = dt.deck_to_ttsdeck(index, deck)

    with open(args.output, "w") as fp:
        json.dump(ttsdeck, fp, indent=True)
