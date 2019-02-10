import json
import argparse
import texttable as tt
import decker.core as dc
import decker.layout as dl


def calculate_rarecount(fixed=[], variable=[]):
    """
    Using the passed distribution, returns the
    expected number for each rarity normalised
    by the least likely rarity.

    fixed expects (rarity, count) tuples
    variable expects ({rarity : probability}, count) tuples
    where the probabilities in a map must sum to 1.0
    """
    expected = {}
    for (rarity, count) in fixed:
        expected[rarity] = count

    for (choices, count) in variable:
        for (rarity, prob) in choices.items():
            expected[rarity] = prob*count

    norm = min(expected.values())
    norm_expected = {rarity:count/norm for (rarity, count) in expected.items()}
    return norm_expected


def adjust_rarecount(rarity_count, expected_rarecount):
    """
    Using the expected rarecount and the actual number of cards
    of each rarity, returns the closest whole number for each card of
    a rarity such that

    1. Each card shows up at least once
    2. No card within a rarity is preferred
    3. The adjusted rarecount ratio is close to expected
    """
    card_count = {rarity: len(cards) for (rarity, cards) in rarities.items()}
    multiplier = max([card_count[rarity] for (rarity, exp_count) in expected_rarecount.items()
                      if exp_count == 1])
    scaled_count = {}
    for rarity, exp_count in expected_rarecount.items():
        new_count = round(exp_count*multiplier/card_count[rarity])
        scaled_count[rarity] = new_count if new_count > 0 else 1
    return scaled_count


def calculate_error(rarity_count, expected_rarecount, adjusted_rarecount):
    """
    Returns (raritity, ideal, actual) for all rarities where ideal
    is the probability of drawing that rarity according to the specification
    and actual is the probability according to the adjusted rarecount
    """
    adjusted_count = {}
    for rarity, rarecount in adjusted_rarecount.items():
        adjusted_count[rarity] = rarity_count[rarity] * rarecount

    expected_sum = sum(expected_rarecount.values())
    adjusted_sum = sum(adjusted_count.values())

    probabilities = []
    for rarity, count in adjusted_count.items():
        ideal = expected_rarecount[rarity]/expected_sum
        actual = count/adjusted_sum
        probabilities.append((rarity, ideal, actual))

    return probabilities


def build_cube(rarities, adjusted_rarecount):
    """
    Returns a cube (deck format) based on the adjusted rarecount
    """
    cube = []
    for rarity, rarecount in adjusted_rarecount.items():
        for edition, name in rarities[rarity]:
            cube.append({"edition": edition,
                         "name": name,
                         "count": rarecount})
    return cube


def split_cube(cube, deck_size):
    """
    split the cube into decks of size `deck_size`
    """
    decks = []

    deck = []
    num_cards = 0
    for card in cube:
        if num_cards + card["count"] <= deck_size:
            num_cards += card["count"]
            deck.append(card)
        else:
            num_diff = deck_size - num_cards
            deck.append({"edition": card["edition"],
                         "name": card["name"],
                         "count": num_diff})
            decks.append(deck)

            num_cards = card["count"] - num_diff
            deck = [{"edition": card["edition"],
                     "name": card["name"],
                     "count": num_cards}]
    decks.append(deck)
    return decks

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
    parser.add_argument('-t', '--test',
                        help="test cube",
                        action="store_true")
    parser.add_argument('-f', "--format",
                        help="A3/A4/TTS",
                        default="TTS")
    parser.add_argument('-b', '--back',
                        help="add sheet of backs",
                        action="store_true")

    args = parser.parse_args()

    with open(args.draft) as f:
        draft = json.load(f)

    expected_rarecount = calculate_rarecount(draft["fixed"], draft["variable"])
    rarities = dc.read_rarities(args.sets, args.editions)
    rarity_count = {rarity: len(cards) for (rarity, cards) in rarities.items()}
    adjusted_rarecount = adjust_rarecount(rarity_count, expected_rarecount)

    if args.test:
        table = tt.Texttable()
        table.add_rows(calculate_error(rarity_count, expected_rarecount, adjusted_rarecount),
                       header=False)
        table.header(["Rarity", "Prob Ideal", "Prob Actual"])
        print(table.draw())
        exit(0)

    cube = build_cube(rarities, adjusted_rarecount)

    index = dc.read_index(args.sets, args.editions)
    pages = dc.deck_pages(index, cube)
    pngdex = dc.read_pngdex(args.sets, pages)

    dims = dl.dimensions(args.format)
    decks = split_cube(cube, dims[0]*dims[1])

    # Since a Cube could be too large to fit in memory
    for (idx, deck) in enumerate(decks[:3]):
        images = dc.slice_deck(index, pngdex, deck)
        sheet = dl.layout(images, dims)[0]
        dl.write_sheet(args.output, sheet, idx)

    if args.back:
        back = dl.read_back("back.png")
        sheet = dl.layout_backs(back, dims)
        dl.write_sheets("back_%s" % args.output, [sheet])
