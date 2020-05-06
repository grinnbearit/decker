import csv
import decker.edition as de
from collections import defaultdict
from swissknife.collections import OrderedSet

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
        cards = de.read_edition(path, edition)
        for card in cards:
            acc[card["name"]].add(edition)
    return acc
