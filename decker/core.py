import re
import json
import decker.edition as de
from collections import defaultdict



MTGA_RE = re.compile("^(\d+) (.+) \(([0-9A-Z]+)\) ([0-9a-zA-Z★]+)$")
def read_deck(deck_file):
    """
    reads an mtga formatted deck file,
    returns a list of {count, name, edition, collector_number} dicts
    """
    acc = []
    with open(deck_file, "r") as fp:
        for line in fp.readlines():
            (count, name, edition, collector_number) = re.match(MTGA_RE, line).groups()
            acc.append({"count": int(count),
                        "name": name,
                        "edition": edition.lower(),
                        "collector_number": collector_number})
    return acc


def deck_editions(deck):
    """
    returns a set of editions used in this deck
    """
    acc = set()
    for deckline in deck:
        acc.add(deckline["edition"])
    return acc


def read_namex(path, editions):
    """
    loads a list of editions into an index of {(edition, name): [collector_numbers]}
    """
    acc = {}
    for edition in editions:
        acc[edition] = defaultdict(list)
        for card in de.read_edition(path, edition):
            acc[edition][card["name"]].append(card["collector_number"])
    return acc


def read_tokex(path, editions):
    """
    loads a list of editions into an index of {name: [(edition, collector_number)]}
    for all token cards
    """
    acc = defaultdict(list)
    for edition in editions:
        for card in de.read_edition(path, edition):
            if card["layout"] in ["token", "emblem", "double_faced_token"]:
                acc[card["name"]].append((card["set"], card["collector_number"]))
    return acc


def read_index(path, editions):
    """
    loads a list of editions into an index of {(edition, collector_number): card}
    """
    acc = {}
    for edition in editions:
        acc[edition] = defaultdict(dict)
        for card in de.read_edition(path, edition):
            acc[edition][card["collector_number"]] = card
    return acc
