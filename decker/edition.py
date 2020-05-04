import os
import json
import time
import requests as r
from PIL import Image
import itertools as it


# Some editions are reserved keywords in windows
EDDEX = {"con": "con_"}


def check_edition(edition):
    """
    given the code for an edition, returns True if the edition is found on
    scryfall, else False
    """
    response = r.head("https://api.scryfall.com/sets/{}".format(edition))
    return response.ok


def is_double_faced(card):
    """
    checks if the card has artwork on both sides
    """
    return card["layout"] in ["transform", "double_faced_token", "art_series"]


def fetch_edition(edition):
    """
    given the 3 letter code for a edition, returns a list of cards from
    scryfall, adds a pngid to all illustrations
    """
    def increment_pngid(prepngid):
        (edition, page, row, col) = prepngid
        if row == 9 and col == 9:
            return (edition, page+1, 0, 0)
        elif col == 9:
            return (edition, page, row+1, 0)
        else:
            return (edition, page, row, col+1)


    acc = []
    scryfall_page = 1
    pngid = (edition, 0, 0, 0)

    while True:
        response = r.get("https://api.scryfall.com/cards/search",
                         params={"order": "set",
                                 "q": "e:{} unique:prints".format(edition),
                                 "page": scryfall_page})

        data = response.json()
        for card in data["data"]:
            if is_double_faced(card):
                card["card_faces"][0]["pngid"] = pngid
                pngid = increment_pngid(pngid)
                card["card_faces"][1]["pngid"] = pngid
            else:
                card["pngid"] = pngid

            acc.append(card)
            pngid = increment_pngid(pngid)

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
            if is_double_faced(card):
                for face in card["card_faces"]:
                    face["pngid"] = tuple(face["pngid"])
            else:
                card["pngid"] = tuple(card["pngid"])
            cards.append(card)
    return cards


def fetch_imdix(cards, print_progress=True):
    """
    Given a list of cards returns a list of (pngid, image)
    """
    imdix = []
    counter = 1
    max_count = len(cards)

    for card in cards:

        if print_progress:
            print("{0:4d}/{1} {2}".format(counter, max_count, card["name"]))
            counter += 1

        if is_double_faced(card):
            for face in card["card_faces"]:
                pngid = face["pngid"]
                response = r.get(face["image_uris"]["png"], stream=True)
                image = Image.open(response.raw)
                imdix.append((pngid, image))
        else:
            response = r.get(card["image_uris"]["png"], stream=True)
            image = Image.open(response.raw)
            imdix.append((card["pngid"], image))

        time.sleep(0.050)       # Time between requests

    return imdix


def upsert_sheets(path, edition, imdix):
    """
    writes new sheets updated with images in the imdix,
    assumes that all images in an edition are the same size
    """
    width, height = imdix[0][1].size

    sheets = {}
    for ((_, page, row, col), image) in imdix:

        if page not in sheets:
            sheetname = "{}/{}_{:03d}.png".format(path, edition, page)
            if os.path.exists(sheetname):
                sheets[page] = (sheetname, Image.open(sheetname))
            else:
                sheets[page] = (sheetname, Image.new("RGB", (width * 10, height * 10), "white"))

        sheets[page][1].paste(image, (width*col, height*row))

    for (_, (sheetname, image)) in sheets.items():
        image.save(sheetname)
