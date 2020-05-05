import argparse
import decker.core as dc
import decker.layout as dl
import decker.edition as de


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", '--deck',
                        help="deck filename",
                        required=True)
    parser.add_argument("-o", "--output",
                        help="image output",
                        required=True)
    parser.add_argument("-p", "--path",
                        help="editions directory",
                        default="editions")
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
    pngdex = dc.read_pngdex(args.path, editions)

    missing_decklines = dc.check_deck(pngdex, deck)

    if missing_decklines:
        print("{0} missing".format(len(missing_decklines)))
        for deckline in missing_decklines:
            print("{0}, {1}".format(deckline["edition"], deckline["name"]))
        exit(1)
    elif args.test:
        exit(0)

    pngids = dc.deck_to_pngids(pngdex, deck)
    images = de.render_pngids(args.path, pngids)

    dims = dl.dimensions(args.format)
    sheets = dl.layout(images, dims)

    dl.write_sheets(args.output, sheets)

    if args.back:
        back = dl.read_back("back.png")
        sheet = dl.layout_backs(back, dims)
        dl.write_sheets("back_%s" % args.output, [sheet])
