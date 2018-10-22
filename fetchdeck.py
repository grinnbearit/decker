import argparse
import decker.core as dc
import decker.layout as dl
import decker.scryfall as ds


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--deck',
                        help="deck filename",
                        required=True)
    parser.add_argument('-o', "--output",
                        help="image output",
                        required=True)
    parser.add_argument('-t', '--test',
                        help="test deck",
                        action="store_true")
    parser.add_argument('-f', "--format",
                        help="A3/A4/TTS",
                        default="TTS")
    parser.add_argument('-b', '--back',
                        help="add sheet of backs",
                        action="store_true")

    args = parser.parse_args()

    deck = dc.read_deck(args.deck)

    missing_cards = ds.check_deck(deck)

    if missing_cards:
        print("{0} missing".format(len(missing_cards)))
        for card in missing_cards:
            print("{0}, {1}".format(card["edition"], card["name"]))
        exit(1)
    elif args.test:
        exit(0)

    dims = dl.dimensions(args.format)
    images = ds.fetch_deck(deck)
    sheets = dl.layout(images, dims)
    dl.write_sheets(args.output, sheets)

    if args.back:
        back = dl.read_back("back.png")
        sheet = dl.layout_backs(back, dims)
        dl.write_sheets("back_%s" % args.output, [sheet])
