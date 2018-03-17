import re
import sys
import csv
import argparse
from PIL import Image
import requests as r
import itertools as it
from scrapy import Selector


# Card Back https://i.imgur.com/P7qYTcI.png
def fetch(card, edition=None):
    """
    returns the most likely image url for the passed card
    """
    base = "https://magiccards.info"
    query = card + " e:" + edition if edition else card
    response = r.get(base + "/query", params={"q": query, "s": "edition"})
    src = Selector(text=response.text).xpath("//td/img[@style='border: 1px solid black;']/@src").extract()[0]
    url = base + src
    return url


def read_deck(deck_file):
    """
    reads a csv deck file and returns a list of (count, url) tuples
    """
    acc = []
    with open(deck_file, "r") as fp:
        reader = csv.reader(fp, delimiter=',', quotechar='"')
        for row in reader:
            count_str, card = row[:2]
            edition = None if len(row) == 2 else row[2]
            acc.append((int(count_str), fetch(card, edition)))
    return acc


def resize(size):
    """given a (width, height) tuple, returns a new tuple with a size proportional to 63:88"""
    (width, height) = size
    semip = width + height

    new_width = int(semip * 63.0/151.0)
    new_height = int(semip * 88.0/151.0)

    return (new_width, new_height)


def load_images(cards, size=None):
    """
    coverts the card list into a list of images with the passed size
    if the size is not passed, takes it from the first card
    """
    base_card = Image.open(r.get(cards[0][1], stream=True).raw)
    size = size or base_card.size

    size = resize(size)

    images = []
    for (count, url) in cards:
        image = Image.open(r.get(url, stream=True).raw)
        image = image.resize(size)
        images.append(image)
        for x in range(1, count):
            images.append(image.copy())

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
    """lays out sheets of images, side by side, according to the passed dimensions (rows, cols)

    returns an array of new image sheets, assumes all passed cards are the same size"""

    card = images[0]
    (width, height) = card.size

    (rows, cols) = dimensions

    cards_per_sheet = rows * cols
    chunks = [images[x:x+cards_per_sheet] for x in range(0, len(images), cards_per_sheet)]

    sheets = []
    for chunk in chunks:
        sheet = Image.new("RGB", (width * cols, height * rows), "white")

        for (idx, image) in zip(range(cards_per_sheet), chunk):
            row = idx / cols
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
    args = parser.parse_args()

    dims = dimensions(args.sheet)
    cards = read_deck(args.deck)
    images = load_images(cards)
    sheets = layout(images, dims)

    if len(sheets) == 1:
        sheets[0].save(args.output)

    else:
        for idx in range(len(sheets)):
            sheets[idx].save("%03d_%s" % (idx, args.output))
