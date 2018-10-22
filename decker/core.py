import csv
from PIL import Image


# Some editions are reserved keywords in windows
EDDEX = {"con": "con_"}


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


def deck_editions(deck):
    """
    given a deck, returns a set of editions that it uses
    """
    return set([card["edition"] for card in deck])


def read_index(path, editions):
    """
    loads a list of editions into an index
    """
    acc = {}
    for edition in editions:
        acc[edition] = {}
        edfile = EDDEX[edition] if edition in EDDEX else edition
        with open("{}/{}.csv".format(path, edfile), "r") as fp:
            reader = csv.DictReader(fp)
            for row in reader:
                acc[edition][row["name"]] = {"page": int(row["page"]),
                                             "column": int(row["column"]),
                                             "row": int(row["row"])}
    return acc


def check_card(index, card):
    """
    returns True if the card is found in the index, else False
    """
    return card["edition"] in index and\
        card["name"] in index[card["edition"]]


def check_deck(index, deck):
    """
    returns a list of missing cards, if none are missing
    returns an empty list
    """
    acc = []
    for card in deck:
        if not check_card(index, card):
            acc.append(card)
    return acc


def deck_pages(index, deck):
    """
    given a deck, returns a list of pages it uses
    """
    return set([(card["edition"], index[card["edition"]][card["name"]]["page"])
                for card in deck])


def read_pngdex(path, pages):
    """
    loads a list of image sheets into a png index
    """
    acc = {}
    for (edition, page) in pages:
        if edition not in acc:
            acc[edition] = {}
        acc[edition][page] = Image.open("{}/{}_{:03d}.png".format(path, edition, page))
    return acc


def slice_card(index, pngdex, card):
    """
    returns the Image object for the card
    """
    coords = index[card["edition"]][card["name"]]
    png = pngdex[card["edition"]][coords["page"]]
    width = png.size[0]/10
    height = png.size[1]/10
    column = width * coords["column"]
    row = height * coords["row"]
    box = (column, row, column+width, row+height)
    return png.crop(box)


def slice_deck(index, pngdex, deck):
    """
    returns a list of Image objects for the passed deck
    """
    acc = []
    for card in deck:
        image = slice_card(index, pngdex, card)
        acc.append(image)
        for _ in range(1, card["count"]):
            acc.append(image.copy())
    return acc
