import json
import random
import argparse
import decker.core as dc
import decker.layout as dl
from collections import Counter


def pick_cards(rarities, fixed=[], variable=[]):
    """
    selects cards using the passed distribution,
    fixed expects (rarity, count) tuples
    variable expects ({rarity : probability}, count) tuples
    where the probabilities in a map must sum to 1.0
    """
    acc = []
    for (rarity, count) in fixed:
        for _ in range(count):
            # replace with random.choices in python 3.6
            cardtup = random.choice(rarities[rarity])
            acc.append(cardtup)

    for (choices, count) in variable:
        for _ in range(count):
            flip = random.random()
            cumprob = 0
            for (rarity, prob) in choices.items():
                cumprob += prob
                if flip < cumprob:
                    cardtup = random.choice(rarities[rarity])
                    break
            acc.append(cardtup)

    deck = []
    for ((edition, name), count) in Counter(acc).items():
        deck.append({"edition": edition,
                     "name": name,
                     "count": count})

    return deck


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--editions",
                        help="list of editions",
                        nargs='+',
                        required=True)
    parser.add_argument("-o", "--output",
                        help="image output",
                        required=True)
    parser.add_argument("-d", "--draft",
                        help="draft json config",
                        default="winchester.json")
    parser.add_argument("-s", "--sets",
                        help="sets directory",
                        default="sets")
    parser.add_argument('-f', "--format",
                        help="A3/A4/TTS",
                        default="TTS")
    parser.add_argument('-b', '--back',
                        help="add sheet of backs",
                        action="store_true")

    args = parser.parse_args()

    with open(args.draft) as f:
        draft = json.load(f)

    rarities = dc.read_rarities(args.sets, args.editions)
    deck = pick_cards(rarities, draft["fixed"], draft["variable"])

    index = dc.read_index(args.sets, args.editions)
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