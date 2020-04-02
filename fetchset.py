import json
import time
import argparse
import requests as r
from PIL import Image
import decker.layout as dl


def check_edition(edition):
    """
    given the 3 letter code for an edition, returns True if the edition is found on
    scryfall, else False
    """
    response = r.head("https://api.scryfall.com/sets/{}".format(edition))
    return response.ok


def fetch_edition(edition):
    """
    given the 3 letter code for a edition, returns a list of cards
    """
    acc = []
    page = 1

    while True:
        response = r.get("https://api.scryfall.com/cards/search",
                         params={"order": "set",
                                 "q": "e:{} unique:prints".format(edition),
                                 "page": page})
        data = response.json()
        cards = data["data"]
        acc.extend(cards)

        if not data["has_more"]:
            break

        page += 1
        time.sleep(0.050) # Time between requests

    return acc


def add_pngids(cards):
    """
    given a list of cards from the same set, sorted by collector number,
    adds a pngid to each one
    """
    edition = cards[0]["set"]

    max_pages = (len(cards) // 100) + 1
    pngids = [(edition, page, row, col)
              for page in range(max_pages)
              for row in range(10)
              for col in range(10)]

    for (pngid, card) in zip(pngids, cards):
        card["pngid"] = pngid
    return cards


def fetch_images(cards):
    """
    returns a list of images for the cards in the st
    """
    images = []
    for card in cards:
        response = r.get(card["image_uris"]["png"], stream=True)
        image = Image.open(response.raw)
        images.append(image)
        time.sleep(0.050)       # Time between requests
    return images


def write_cards(edition, index):
    """
    writes cards as rows of json to a file named {edition}.json
    """
    with open("{}.json".format(edition), "w", newline="") as f:
        for card in index:
            json.dump(card, f)
            f.write("\n")


def write_sheets(edition, sheets):
    """
    writes multiple image sheets named {edition}_{page}.png
    """
    for (page, sheet) in enumerate(sheets):
        sheet.save("{}_{:03d}.png".format(edition, page))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--edition',
                        help="3 letter edition code",
                        required=True)

    args = parser.parse_args()

    if not check_edition(args.edition):
        print("edition {} not found".format(args.edition))
        exit(1)

    cards = fetch_edition(args.edition)
    cards = add_pngids(cards)
    images = fetch_images(cards)
    sheets = dl.layout(images, (10, 10))

    write_cards(args.edition, cards)
    write_sheets(args.edition, sheets)
