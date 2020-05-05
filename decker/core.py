import json
import csv
from PIL import Image
import itertools as it
import decker.edition as de
from collections import defaultdict
from swissknife.collections import OrderedSet, OrderedDefaultDict


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
        cards = de.read_edition(path, edition)
        for card in cards:
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


def filter_editions(codex, newest, oldest, ignore, current):
    """
    returns two lists of editions, (new, old) split at current, sorted
    from newest to oldest

    only considers editions between `newest` and `oldest`, ignores `ignore`
    """
    newest_flag = newest is None
    current_flag = False

    newacc = []
    oldacc = []
    for row in codex:
        edition = row["edition"]

        if newest == edition:
            newest_flag = True

        if current == edition:
            current_flag = True

        if newest_flag and\
           row["edition"] not in ignore:
            if current_flag:
                oldacc.append(edition)
            else:
                newacc.append(edition)

        if oldest == edition:
            break

    return (newacc, oldacc)


def read_cardex(path, codex, newest=None, oldest=None, ignore=set()):
    """
    Using a codex, returns a map of {name: editions} where
    editions is sorted from newest to oldest

    path: the editions path
    codex: a sorted list of downloaded editions
    newest: the newest edition to consider
    oldest: the oldest edition to consider
    ignore: a set of editions to ignore
    """
    acc = defaultdict(OrderedSet)
    (editions, _) = filter_editions(codex, newest, oldest, ignore, None)
    for edition in editions:
        edfile = EDDEX[edition] if edition in EDDEX else edition
        with open(f"{path}/{edfile}.json", "r") as fp:
            reader = csv.DictReader(fp)
            for line in fp.readlines():
                row = json.loads(line)
                acc[row["name"]].add(edition)
    return acc


def read_artex(path, codex, newest=None, oldest=None, ignore=set(), current=None):
    """
    Using a codex, returns a map of {artist_id: {illustration_id: {new: [pngid], old: [pngid]} where
    pngids are sorted from oldest to newest. `new` are pngids released after `current` and `old`
    includes `current`.

    `illustration_ids` are stored in an OrderedDict, sorted from oldest to newest

    path: the editions path
    codex: a sorted list of downloaded editions
    newest: the newest edition to consider
    oldest: the oldest edition to consider
    ignore: a set of editions to ignore
    current: the current edition
    """
    acc = defaultdict(lambda: OrderedDefaultDict(lambda: defaultdict(list)))
    (neweds, oldeds) = filter_editions(codex, newest, oldest, ignore, current)
    edlist = [("new", e) for e in neweds] + [("old", e) for e in oldeds]
    edlist.reverse()
    for (old_new, edition) in edlist:
        edfile = EDDEX[edition] if edition in EDDEX else edition
        with open(f"{path}/{edfile}.json", "r") as fp:
            reader = csv.DictReader(fp)
            for line in fp.readlines():
                row = json.loads(line)
                if row["layout"] in ["transform", "double_faced_token", "art_series"]:
                    for face in row["card_faces"]:
                        acc[face["artist_id"]][face["illustration_id"]][old_new].append(tuple(face["pngid"]))
                elif row["artist"] == "":
                    continue
                else:
                    for artist_id in row["artist_ids"]:
                        acc[artist_id][row["illustration_id"]][old_new].append(tuple(row["pngid"]))
    return acc
