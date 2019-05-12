import argparse
import decker.core as dc
import decker.layout as dl


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", '--deck',
                        help="deck filename",
                        required=True)
    parser.add_argument("-o", "--output",
                        help="image output",
                        required=True)
    parser.add_argument("-s", "--sets",
                        help="sets directory",
                        default="sets")
    parser.add_argument('-t', '--test',
                        help="test deck",
                        action="store_true")
    parser.add_argument('-f', "--format",
                        help="A3/A4/TTS/gdrive",
                        default="gdrive")
    parser.add_argument('-b', '--back',
                        help="add sheet of backs",
                        action="store_true")

    args = parser.parse_args()

    deck = dc.read_deck(args.deck)
    editions = dc.deck_editions(deck)
    index = dc.read_index(args.sets, editions)

    missing_cards = dc.check_deck(index, deck)

    if missing_cards:
        print("{0} missing".format(len(missing_cards)))
        for card in missing_cards:
            print("{0}, {1}".format(card["edition"], card["name"]))
        exit(1)
    elif args.test:
        exit(0)

    pages = dc.deck_pages(index, deck)
    pngdex = dc.read_pngdex(args.sets, pages)

    dims = dl.dimensions(args.format)
    images = dc.slice_deck(index, pngdex, deck)
    sheets = dl.layout(images, dims)

    dl.write_sheets(args.output, sheets)

    if args.back:
        back = dl.read_back("back.png")
        sheet = dl.layout_backs(back, dims)
        dl.write_sheets("back_%s" % args.output, [sheet])
