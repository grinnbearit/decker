import json
import argparse
import decker.core as dc
import decker.tts as dt


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", '--deck',
                        help="deck filename",
                        required=True)
    parser.add_argument("-o", "--output",
                        help="tts output",
                        required=True)
    parser.add_argument("-p", "--path",
                        help="editions directory",
                        default="editions")

    args = parser.parse_args()

    deck = dc.read_deck(args.deck)
    editions = dc.deck_editions(deck)
    index = dc.read_index(args.path, editions)
    ttsdeck = dt.deck_to_ttsdeck(index, deck)

    with open(args.output, "w") as fp:
        json.dump(ttsdeck, fp, indent=True)
