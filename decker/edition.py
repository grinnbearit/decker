import os
import csv
import json
import time
import requests as r
from bs4 import BeautifulSoup
from datetime import datetime


# Some editions are reserved keywords in windows
EDDEX = {"con": "con_"}


def check_edition(edition):
    """
    given the code for an edition, returns True if the edition is found on
    scryfall, else False
    """
    response = r.head("https://api.scryfall.com/sets/{}".format(edition))
    return response.ok


def fetch_edition(edition):
    """
    given the 3 letter code for a edition, returns a list of cards from
    scryfall
    """
    acc = []
    scryfall_page = 1

    while True:
        response = r.get("https://api.scryfall.com/cards/search",
                         params={"order": "set",
                                 "q": "e:{} unique:prints".format(edition),
                                 "page": scryfall_page})

        data = response.json()
        acc.extend(data["data"])
        if not data["has_more"]:
            break

        scryfall_page += 1
        time.sleep(0.050) # Time between requests

    return acc


def write_edition(path, cards):
    """
    writes edition metadata as rows of json to a file named path/{edition}.json
    assumes all cards are from the same edition
    """
    edition = cards[0]["set"]
    edfile = EDDEX[edition] if edition in EDDEX else edition

    with open("{}/{}.json".format(path, edfile), "w", newline="") as f:
        for card in cards:
            json.dump(card, f)
            f.write("\n")


def read_edition(path, edition):
    """
    returns a list of cards for the passed edition
    """
    edfile = EDDEX[edition] if edition in EDDEX else edition

    cards = []
    with open(f"{path}/{edfile}.json", "r") as fp:
        for line in fp.readlines():
            card = json.loads(line)
            card["released_at"] = datetime.fromisoformat(card["released_at"]).date()
            cards.append(card)
    return cards


def fetch_codex():
    """
    returns a list of all editions in reverse chronological order
    from https://scryfall.com/sets
    """
    response = r.get("https://scryfall.com/sets")
    soup = BeautifulSoup(response.text, "html.parser")

    acc = []
    for row in soup.find("table", class_="checklist").find_all("tr")[1:]:
        divisions = row.find_all("td")
        edition = divisions[0].small.text.lower()
        offset = len(edition) + 1
        name = divisions[0].text.strip()[:-offset]
        cards = int(divisions[1].text.strip())
        date = datetime.strptime(divisions[2].text.strip(), "%Y-%m-%d").date()
        acc.append({"edition": edition,
                    "name": name,
                    "cards": cards,
                    "date": date})
    return acc


def write_codex(codex_file, codex):
    """
    writes the codex as a csv to `codex_file`
    """
    with open(codex_file, 'w') as csvfile:
        fieldnames = ["edition", "name", "cards", "date"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        for row in codex:
            writer.writerow(row)
