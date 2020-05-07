import csv
import json
from PIL import Image
import itertools as it
import decker.edition as de
from collections import defaultdict


def read_deck(deck_file):
    """
    reads a csv deck file and returns a list of (edition, name, count) tuples
    """
    acc = []
    with open(deck_file, "r") as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            row["count"] = int(row["count"])
            acc.append(row)
    return acc


def deck_editions(deck):
    """
    given a deck, returns a set of editions that it uses
    """
    return set([deckline["edition"] for deckline in deck])


def read_pngdex(path, editions):
    """
    loads a list of editions into an index of {(edition, name): [pngid]}
    """
    acc = {}
    for edition in editions:
        acc[edition] = defaultdict(list)
        for card in de.read_edition(path, edition):
            if de.is_double_faced(card):
                pngids = [face["pngid"] for face in card["card_faces"]]
                acc[edition][card["name"]].append(pngids)
            else:
                acc[edition][card["name"]].append(card["pngid"])
    return acc


def check_deck(pngdex, deck):
    """
    returns a list of missing card names, if none are missing
    returns an empty list
    """
    acc = []
    for deckline in deck:
        if deckline["edition"] not in pngdex or\
           deckline["name"] not in pngdex[deckline["edition"]]:
            acc.append(deckline)
    return acc


def deck_to_pngids(pngdex, deck):
    """
    Returns a list of sheet coordinates for the passed deck.

    If multiple copies of a card are needed, and multiple versions of that card
    exist, cycle through the different versions

    If a card is double faced, adds two pngids for it in sequence.
    """
    acc = []
    for deckline in deck:
        name_pngids = pngdex[deckline["edition"]][deckline["name"]]
        deckline_pngids = it.islice(it.cycle(name_pngids), deckline["count"])
        if type(name_pngids[0]) is list:
            for pnglist in deckline_pngids:
                acc.extend(pnglist)
        else:
            acc.extend(deckline_pngids)
    return acc
