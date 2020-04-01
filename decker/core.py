import json
import csv
from PIL import Image
from collections import defaultdict


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
        acc[edition] = defaultdict(list)
        edfile = EDDEX[edition] if edition in EDDEX else edition
        with open("{}/{}.json".format(path, edfile), "r") as fp:
            for line in fp.readlines():
                row = json.loads(line)
                acc[edition][row["name"]].append(row["pngdex"])
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
    return set([(card["edition"], coords["page"])
                for card in deck
                for coords in index[card["edition"]][card["name"]]])


def read_pngdex(path, pages):
    """
    loads a list of image sheets into a png index
    """
    acc = {}
    for (edition, page) in pages:
        edfile = EDDEX[edition] if edition in EDDEX else edition
        if edition not in acc:
            acc[edition] = {}
        acc[edition][page] = Image.open("{}/{}_{:03d}.png".format(path, edfile, page))
    return acc


def slice_card(index, pngdex, card):
    """
    returns the list of Image objects for the card
    """
    acc = []
    for coords in index[card["edition"]][card["name"]]:
        png = pngdex[card["edition"]][coords["page"]]
        width = png.size[0]/10
        height = png.size[1]/10
        column = width * coords["column"]
        row = height * coords["row"]
        box = (column, row, column+width, row+height)
        acc.append(png.crop(box))
    return acc


def slice_deck(index, pngdex, deck):
    """
    returns a list of Image objects for the passed deck
    """
    acc = []
    for card in deck:
        images = slice_card(index, pngdex, card)
        for i in range(card["count"]):
            acc.append(images[i % len(images)])
    return acc


def read_codex(codex_file):
    """
    reads a csv codex file and returns a list of codex
    tuples sorted newest to oldest
    """
    acc = []
    with open(codex_file, "r") as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            acc.append(row)
    return acc


def _read_editions(codex, newest, oldest, ignore):
    """
    helper function for `read_cardex`
    returns a list of relevant editions given constraints
    """
    newest_flag = newest is None
    oldest_flag = False

    acc = []
    for row in codex:
        edition = row["edition"]

        if newest == edition:
            newest_flag = True

        if newest_flag and\
           not oldest_flag and\
           row["edition"] not in ignore:
            acc.append(edition)

        if oldest == edition:
            oldest_flag = True

    return acc


def read_cardex(path, codex, newest=None, oldest=None, ignore=set()):
    """
    Using a codex, returns a map of {name: editions} where
    editions is sorted from newest to oldest

    path: the sets path
    codex: a sorted list of downloaded sets
    newest: the newest set to consider
    oldest: the oldest set to consider
    ignore: a set of editions to ignore
    """
    acc = {}
    for edition in _read_editions(codex, newest, oldest, ignore):
        edfile = EDDEX[edition] if edition in EDDEX else edition
        with open(f"{path}/{edfile}.json", "r") as fp:
            reader = csv.DictReader(fp)
            for line in fp.readlines():
                row = json.loads(line)
                editions = acc.get(row["name"], [])
                editions.append(edition)
                acc[row["name"]] = editions
    return acc
