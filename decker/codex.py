import csv
import requests as r
import decker.edition as de
from datetime import datetime
from bs4 import BeautifulSoup
from operator import itemgetter
from ordered_set import OrderedSet
from collections import defaultdict


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


def fetch_codex():
    """
    returns a list of all editions in reverse chronological order
    from https://scryfall.com/sets

    `all_cards` are the total number of cards in the set currently available on
    scryfall

    `stored_cards` and `highres_cards` are set by `update_codex`
    """
    response = r.get("https://scryfall.com/sets")
    soup = BeautifulSoup(response.text, "html.parser")

    acc = []
    for row in soup.find("table", class_="checklist").find_all("tr")[1:]:
        if (row.find(class_="pillbox") and\
            not row.find(class_="pillbox-item disabled", text="en")):

            divisions = row.find_all("td")
            edition = divisions[0].small.text.lower()
            offset = len(edition) + 1
            name = divisions[0].text.strip()[:-offset]
            cards = int(divisions[1].text.strip())
            date = datetime.strptime(divisions[2].text.strip(), "%Y-%m-%d").date()
            acc.append({"date": date,
                        "edition": edition,
                        "name": name,
                        "all_cards": cards,
                        "stored_cards": -1,
                        "highres_cards": -1})
    return sorted(acc, key=itemgetter("date", "edition"), reverse=True)


def update_codex(path, codex):
    """
    updates `stored_cards` and `highres_cards` in the passed codex
    """
    for row in codex:
        if de.stored_edition(path, row["edition"]):
            cards = de.read_edition(path, row["edition"])
            stored_cards = len(cards)
            highres_cards = 0

            for card in cards:
                if card["highres_image"]:
                    highres_cards += 1

            row["stored_cards"] = stored_cards
            row["highres_cards"] = highres_cards
        else:
            row["stored_cards"] = 0
            row["highres_cards"] = 0
    return codex


def write_codex(codex_file, codex):
    """
    writes the codex as a csv to `codex_file`
    """
    with open(codex_file, 'w') as csvfile:
        fieldnames = ["date", "edition", "name", "all_cards", "stored_cards", "highres_cards"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        for row in codex:
            writer.writerow(row)


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
    returns a list of editions from `newest` to `oldest` ignores `ignore`
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
