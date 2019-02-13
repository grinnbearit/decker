import json
import argparse
import texttable as tt
import decker.core as dc
import decker.layout as dl


def calculate_rarecount(fixed=[], variable=[]):
    """
    Using the passed distribution, returns the
    expected number for each rarity

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

    return expected


def adjust_rarecount(rarity_count, expected_rarecount):
    """
    Using the expected rarecount and the actual number of cards
    of each rarity, returns the closest whole number for each card of
    a rarity such that

    1. Each card shows up at least once
    2. No card within a rarity is preferred
    3. The adjusted rarecount ratio is close to expected
    4. The total number of cards is at least the sum of expected
    """
    rarity_ratio = {rarity: exp_count/rarity_count[rarity] for (rarity, exp_count)
                    in expected_rarecount.items()}
    multiplier = min(rarity_ratio.values())
    multiplier = 1.0 if multiplier >= 1.0 else 1.0/multiplier
    scaled_rarecount = {rarity: round(ratio*multiplier) for (rarity, ratio)
                        in rarity_ratio.items()}
    return scaled_rarecount


def calculate_error(rarity_count, expected_rarecount, adjusted_rarecount):
    """
    Returns (raritity, set, draft, cube, multiplier, p_draft, p_cube) for all rarities where
    `set` is the number of cards of that rarity in the set(s), `draft` is the number of cards of
    that rarity according to the spec and `cube` is the number of cards of that rarity in the cube.

    `multiplier` is the number of instances of each card of the rarity

    `p_draft` and `p_cube` are the probabilities of drawing this rarity from the draft
    and the cube respectively.
    """
    adjusted_count = {}
    for rarity, rarecount in adjusted_rarecount.items():
        adjusted_count[rarity] = rarity_count[rarity] * rarecount

    expected_sum = sum(expected_rarecount.values())
    adjusted_sum = sum(adjusted_count.values())

    error = []
    for rarity, count in adjusted_count.items():
        num_draft = expected_rarecount[rarity]
        num_set = rarity_count[rarity]
        num_cube = count
        multiplier = num_cube/num_set
        p_draft = num_draft/expected_sum
        p_cube = num_cube/adjusted_sum
        error.append((rarity, num_draft, num_set, multiplier, num_cube, p_draft, p_cube))

    return error


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

    expected_rarecount = calculate_rarecount(draft.get("fixed", []), draft.get("variable", []))
    rarities = dc.read_rarities(args.sets, args.editions)
    rarity_count = {rarity: len(cards) for (rarity, cards) in rarities.items()}
    adjusted_rarecount = adjust_rarecount(rarity_count, expected_rarecount)

    if args.test:
        table = tt.Texttable()
        table.add_rows(calculate_error(rarity_count, expected_rarecount, adjusted_rarecount),
                       header=False)
        table.header(["Rarity", "Draft", "Set", "Multiplier", "Cube", "P(Draft)", "P(Cube)"])
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
    print(adjusted_rarecount)
