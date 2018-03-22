import re
import sys
import csv
import time
import argparse
import requests as r
from PIL import Image
import itertools as it


def read_deck(deck_file):
    """
    reads a csv deck file and returns a list of (count, card, edition) tuples
    """
    acc = []
    with open(deck_file, "r") as fp:
        reader = csv.reader(fp, delimiter=',', quotechar='"')
        for row in reader:
            count_str, card = row[:2]
            edition = None if len(row) == 2 else row[2]
            acc.append((int(count_str), card, edition))
    return acc


def check_card(card, edition):
    """
    returns True if the card is found on scryfall, else False
    """
    response = r.head("https://api.scryfall.com/cards/named",
                      params={"exact": card, "set": edition})
    return response.ok


def check_deck(cards):
    """
    returns a list of missing cards, if none are missing
    returns an empty list
    """
    acc = []
    for (_, card, edition) in cards:
        if not check_card(card, edition):
            acc.append((card, edition))
        time.sleep(0.050)       # Time between requests
    return acc


def fetch_card(card, edition):
    """
    returns the Image object for the card/edition
    """
    response = r.get("https://api.scryfall.com/cards/named",
                     params={"exact": card, "set": edition,
                             "format": "image", "version": "png"},
                     stream=True)
    return Image.open(response.raw)


def resize(size):
    """
    given a (width, height) tuple, returns a new tuple with a size proportional to 63:88
    """
    (width, height) = size
    semip = width + height

    new_width = int(semip * 63.0/151.0)
    new_height = int(semip * 88.0/151.0)
    return (new_width, new_height)


def fetch_deck(cards, size=None):
    """
    coverts the deck into a list of images of the passed size,
    if the size is not passed, takes it from the first card
    """
    base_card = fetch_card(cards[0][1], cards[0][2])
    size = size or base_card.size
    size = resize(size)

    images = []
    for (count, card,  edition) in cards:
        image = fetch_card(card, edition)
        image = image.resize(size)
        images.append(image)
        for _ in range(1, count):
            images.append(image.copy())
        time.sleep(0.050)       # Time between requests
    return images


def dimensions(sheet):
    """
    translates a sheet type into (rows, columns)
    """
    formats = {"A3": (3, 6),
               "A4": (3, 3),
               "TTS": (7, 10)}
    if sheet in formats:
        return formats[sheet]
    raise Exception("Unsupported format")


def layout(images, dimensions=(3, 6)):
    """
    lays out sheets of images, side by side, according to the passed dimensions (rows, cols)
    returns an array of new image sheets, assumes all passed cards are the same size
    """

    card = images[0]
    (width, height) = card.size

    (rows, cols) = dimensions

    cards_per_sheet = rows * cols
    chunks = [images[x:x+cards_per_sheet] for x in range(0, len(images), cards_per_sheet)]

    sheets = []
    for chunk in chunks:
        sheet = Image.new("RGB", (width * cols, height * rows), "white")

        for (idx, image) in zip(range(cards_per_sheet), chunk):
            row = idx // cols
            col = idx % cols
            sheet.paste(image, (width * col, height * row))

        sheets.append(sheet)

    return sheets


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--deck',
                        help="deck filename",
                        required=True)
    parser.add_argument('-o', "--output",
                        help="image output",
                        required=True)
    parser.add_argument('-s', "--sheet",
                        help="A3/A4/TTS",
                        default="A3")
    parser.add_argument('-t', '--test',
                        help="test deck",
                        action="store_true")
    args = parser.parse_args()

    cards = read_deck(args.deck)

    if args.test:
        missing_cards = check_deck(cards)
        if missing_cards:
            print("{0} missing".format(len(missing_cards)))
            for (card, edition) in missing_cards:
                print("{0}, {1}".format(card, edition))
        else:
            print("OK")
    else:
        dims = dimensions(args.sheet)
        images = fetch_deck(cards)
        sheets = layout(images, dims)

        if len(sheets) == 1:
            sheets[0].save(args.output)
        else:
            for idx in range(len(sheets)):
                sheets[idx].save("%03d_%s" % (idx, args.output))
