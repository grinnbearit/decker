import argparse
import decker.core as dc
import decker.paper as dp
import decker.layout as dl
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
    group.add_argument("-b", "--back",
                       help="planar/scheme/standard," +\
                       " prints a single sheet of backs of the kind specified")
    parser.add_argument("-o", "--output",
                        help=" output",
                        required=True)
    parser.add_argument("-p", "--path",
                        help="editions directory",
                        default="editions")
    parser.add_argument("-l", "--lowres",
                        help="generates a deck with low res images," +\
                        " if no high res available",
                        action="store_true")
    parser.add_argument('-f', "--format",
                        help="A3/A4",
                        default="A3")

    args = parser.parse_args()

    dims = dl.dimensions(args.format)

    if args.back:
        images = dp.back_to_images(args.back, dims[0]*dims[1])
        sheets = dl.layout(images, dims)
        dl.write_sheets(args.output, sheets)
        exit(0)

    deck = dc.read_deck(args.deck)
    editions = dc.deck_editions(deck)
    index = dc.read_index(args.path, editions)

    if not args.lowres:
        if not is_deck_highres(index, deck):
            print(f"not all cards in {args.deck} have highres prints")
            exit(-1)

    images = dp.deck_to_images(index, deck)
    sheets = dl.layout(images, dims)
    dl.write_sheets(args.output, sheets)
