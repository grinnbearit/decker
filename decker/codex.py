import csv
import decker.edition as de
from collections import defaultdict
from swissknife.collections import OrderedSet


def read_cardlist(cardlist_file):
    """
    reads a csv file and returns a list of {name, count} dicts
    """
    acc = []
    with open(cardlist_file, "r") as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            row["count"] = int(row["count"])
            acc.append(row)
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


def filter_editions(codex, newest, oldest, ignore):
    """
    returns two lists of editions, (new, old) split at current, sorted
    from newest to oldest

    only considers editions between `newest` and `oldest`, ignores `ignore`
    """
    newest_flag = newest is None

    acc = []
    for edition in [row["edition"] for row in codex]:

        if newest == edition:
            newest_flag = True

        if newest_flag and edition not in ignore:
            acc.append(edition)

        if oldest == edition:
            break

    return acc


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
    for edition in filter_editions(codex, newest, oldest, ignore):
        for card in de.read_edition(path, edition):
            acc[card["name"]].add(edition)
    return acc


def list_editions(cardex, cardlist):
    """
    returns a set of needed editions
    """
    acc = set()
    for cardline in cardlist:
        acc.add(list(cardex[cardline["name"]])[0])
    return acc


def cardlist_to_deck(cardex, namex, cardlist):
    """
    Returns an mtga formatted deck from a cardlist

    If multiple copies of a card are needed, and multiple versions of that card
    exist, cycles through the different versions
    """
    acc = []
    for cardline in cardlist:
        edition = list(cardex[cardline["name"]])[0]
        collector_numbers = namex[edition][cardline["name"]]
        cn_count = cardline["count"]//len(collector_numbers)
        for idx, cn in enumerate(collector_numbers):
            overflow = cardline["count"] % len(collector_numbers)
            count = cn_count + 1 if idx < overflow else cn_count

            if count != 0:
                deckline = {"count": count,
                            "name": cardline["name"],
                            "edition": edition,
                            "collector_number": cn}

                acc.append(deckline)

    return acc
