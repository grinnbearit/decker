import sys
import csv
import time
import argparse
import requests as r
from PIL import Image


def check_set(edition):
    """
    given the 3 letter code for a set, returns True if the set is found on
    scryfall, else False
    """
    response = r.head("https://api.scryfall.com/sets/{}".format(edition))
    return response.ok


def fetch_set(edition):
    """
    given the 3 letter code for a set, returns a list of cards
    """
    acc = []
    page = 1

    while True:
        response = r.get("https://api.scryfall.com/cards/search",
                         params={"order": "set",
                                 "q": "e:{}".format(edition),
                                 "unique": "prints",
                                 "page": page})
        data = response.json()
        cards = [(card["collector_number"], card["name"], card["rarity"], card["image_uris"]["png"])
                 for card in data["data"]]
        acc.extend(cards)

        if not data["has_more"]:
            break

        page += 1
        time.sleep(0.050) # Time between requests

    return acc


def fetch_deck(cards):
    """
    coverts the list of cards into a list of images
    """
    images = []
    for card in cards:
        response = r.get(card[3], stream=True)
        image = Image.open(response.raw)
        images.append(image)
        time.sleep(0.050)       # Time between requests
    return images


def layout(images):
    """
    lays out the cards in a sheet as a single row
    """
    im = images[0]
    (width, height) = im.size

    sheet = Image.new("RGB", (width * len(images), height), "white")
    for (pos, image) in enumerate(images):
        sheet.paste(image, (width * pos, 0))

    return sheet


def write_index(filename, cards):
    """
    creates a csv index of cards
    """
    with open(filename, "w", newline="") as f:
        idxwriter = csv.writer(f)
        idxwriter.writerow(["idx", "collector_number", "name", "rarity", "png"])
        for (idx, card) in enumerate(cards):
            idxwriter.writerow([idx, card[0], card[1], card[2], card[3]])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--edition',
                        help="3 letter edition code",
                        required=True)

    args = parser.parse_args()

    if not check_set(args.edition):
        print("set {} not found".format(args.edition))
        exit(1)

    cards = fetch_set(args.edition)
    images = fetch_deck(cards)
    sheet = layout(images)

    write_index("{}.csv".format(args.edition), cards)
    sheet.save("{}.png".format(args.edition))
