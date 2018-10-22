import csv
import time
import argparse
import requests as r
from PIL import Image


def read_deck(deck_file):
    """
    reads a csv deck file and returns a list of (edition, name, count) tuples
    """
    acc = []
    with open(deck_file, "r") as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            acc.append({"edition": row["edition"],
                        "name": row["name"],
                        "count": int(row["count"])})
    return acc


def check_card(card):
    """
    returns True if the card is found on scryfall, else False
    """
    response = r.head("https://api.scryfall.com/cards/named",
                      params={"set": card["edition"],
                              "exact": card["name"]})
    return response.ok


def check_deck(deck):
    """
    returns a list of missing cards, if none are missing
    returns an empty list
    """
    acc = []
    for card in deck:
        if not check_card(card):
            acc.append(card)
        time.sleep(0.050)       # Time between requests
    return acc


def fetch_card(card):
    """
    returns the Image object for the card
    """
    response = r.get("https://api.scryfall.com/cards/named",
                     params={"set": card["edition"], "exact": card["name"],
                             "format": "image", "version": "png"},
                     stream=True)
    return Image.open(response.raw)


def fetch_deck(deck, size=None):
    """
    returns a list of Image objects for the passed deck
    """
    acc = []
    for card in deck:
        image = fetch_card(card)
        acc.append(image)
        for _ in range(1, card["count"]):
            acc.append(image.copy())
        time.sleep(0.050)       # Time between requests
    return acc


def dimensions(frmt):
    """
    translates a format type into (columns, rows)
    """
    formats = {"A3": (6, 3),
               "A4": (3, 3),
               "TTS": (10, 7)}
    if frmt in formats:
        return formats[frmt]
    raise Exception("Unsupported format")


def layout(images, dimensions=(6, 3)):
    """
    lays out sheets of images, side by side, according to the passed dimensions (cols, rows)
    returns an array of new image sheets, assumes all passed cards are the same size
    """

    im = images[0]
    (width, height) = im.size

    (cols, rows) = dimensions

    cards_per_sheet = cols * rows
    chunks = [images[x:x+cards_per_sheet] for x in range(0, len(images), cards_per_sheet)]

    sheets = []
    for chunk in chunks:
        sheet = Image.new("RGB", (width * cols, height * rows), "white")

        for (idx, image) in zip(range(cards_per_sheet), chunk):
            col = idx % cols
            row = idx // cols
            sheet.paste(image, (width * col, height * row))

        sheets.append(sheet)

    return sheets


def read_back(filename):
    back = Image.open(filename)
    return back


def layout_backs(back, dimensions=(3, 6)):
    (width, height) = back.size
    (rows, cols) = dimensions
    sheet = Image.new("RGB", (width * cols, height * rows), "white")
    for row in range(rows):
        for col in range(cols):
            sheet.paste(back, (width * col, height * row))
    return sheet


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

    deck = read_deck(args.deck)

    missing_cards = check_deck(deck)

    if missing_cards:
        missing_cards = check_deck(cards)
        print("{0} missing".format(len(missing_cards)))
        for card in missing_cards:
            print("{0}, {1}".format(card["edition"], card["name"]))
        exit(1)
    elif args.test:
        exit(0)

    dims = dimensions(args.format)
    images = fetch_deck(deck)
    sheets = layout(images, dims)

    if len(sheets) == 1:
        sheets[0].save(args.output)
    else:
        for idx in range(len(sheets)):
            sheets[idx].save("%03d_%s" % (idx, args.output))

    if args.back:
        back = read_back("back.png")
        sheet = layout_backs(back, dims)
        sheet.save("back_%s" % args.output)
