import csv
import json
from PIL import Image
import itertools as it
import decker.edition as de
from collections import defaultdict


def read_cardlist(cardlist_file):
    """
    reads a csv file and returns a list of (name, count) tuples
    """
    acc = []
    with open(cardlist_file, "r") as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            row["count"] = int(row["count"])
            acc.append(row)
    return acc


def read_index(path, editions):
    """
    loads a list of editions into an index of {(edition, name): [collector_numbers]}
    """
    acc = {}
    for edition in editions:
        acc[edition] = defaultdict(list)
        for card in de.read_edition(path, edition):
            acc[edition][card["name"]].append(card["collector_number"])
    return acc


def cardlist_to_deck(index, cardlist):
    """
    Returns an mtga formatted deck from a cardlist

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
