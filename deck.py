import sys
import csv
from PIL import Image
import itertools as it

def read_cards(deck_file):
    """reada a csv deck file and returns a list of (filname, count) tuples"""
    with open(deck_file, "r") as deck_fp:
        deck_reader = csv.reader(deck_fp)
        cards = []
        for (card, count) in deck_reader:
            cards.append((card, int(count)))
        return cards


def resize(size):
    """given a (width, height) tuple, returns a new tuple with a size proportional to 63:88"""
    (width, height) = size

    if width % 63 == 0 and height % 88 == 0:
        return (width, height)

    new_width = ((width / 63) + 1) * 63
    new_height = ((height / 88) + 1) * 88

    return (new_width, new_height)


def load_images(cards, size=None):
    """coverts the card list into a list of images with the passed size

    if the size is not passed, takes it from the first card"""

    base_card = Image.open(cards[0][0])
    size = size or base_card.size

    size = resize(size)

    images = []
    for (card, count) in cards:
        image = Image.open(card)
        image = image.resize(size)
        images.append(image)
        for x in range(1, count):
            images.append(image.copy())

    return images


def layout(images, dimensions=(5, 5)):
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
    if len(sys.argv) < 3:
        print "The deck and output files are required arguments"
        sys.exit(0)

    deck = sys.argv[1]
    output = sys.argv[2]

    cards = read_cards(deck)
    images = load_images(cards)
    sheets = layout(images)

    if len(sheets) == 1:
        sheets[0].save(output)
    else:
        for idx in range(len(sheets)):
            sheets[idx].save("%d_%s" % (idx, output))
