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

        cards = []
        for card in data["data"]:
            if card["layout"] in ["transform", "double_faced_token"]:
                card_a = card["card_faces"][0]
                card_b = card["card_faces"][1]
                cards.append({"name": card_a["name"],
                              "rarity": card["rarity"],
                              "png_uri": card_a["image_uris"]["png"]})
                cards.append({"name": card_b["name"],
                              "rarity": card["rarity"],
                              "png_uri": card_b["image_uris"]["png"]})
            else:
                cards.append({"name": card["name"],
                              "rarity": card["rarity"],
                              "png_uri": card["image_uris"]["png"]})
        acc.extend(cards)

        if not data["has_more"]:
            break

        page += 1
        time.sleep(0.050) # Time between requests

    return acc


def fetch_images(cards):
    """
    returns a list of images for the cards in the st
    """
    images = []
    for card in cards:
        response = r.get(card["png_uri"], stream=True)
        image = Image.open(response.raw)
        images.append(image)
        time.sleep(0.050)       # Time between requests
    return images


def build_index(cards, images):
    """
    Given a list of cards and images, returns (index, sheets)
    with an index pointing to multiple sheets with cards
    laid out in a 10x10 grid
    """
    (width, height) = images[0].size

    index = []
    sheets = []

    unchunked = list(zip(range(len(cards)), cards, images))
    chunks = [unchunked[x:x+100] for x in range(0, len(images), 100)]

    for chunk in chunks:
        sheet = Image.new("RGB", (width * 10, height * 10), "white")

        for (idx, card, image) in chunk:
            page = idx // 100
            column = idx % 10
            row = (idx % 100) // 10

            index.append({"name": card["name"],
                          "rarity": card["rarity"],
                          "page": page,
                          "column": column,
                          "row": row})

            sheet.paste(image, (width * column, height * row))

        sheets.append(sheet)

    return (index, sheets)


def write_index(edition, index):
    """
    writes a csv index of cards named {edition}.csv
    """
    with open("{}.csv".format(edition), "w", newline="") as f:
        idxwriter = csv.DictWriter(f, fieldnames=["name", "rarity", "page", "column", "row"])
        idxwriter.writeheader()
        idxwriter.writerows(index)


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

    if not check_set(args.edition):
        print("set {} not found".format(args.edition))
        exit(1)

    cards = fetch_set(args.edition)
    images = fetch_images(cards)
    (index, sheets) = build_index(cards, images)

    write_index(args.edition, index)
    write_sheets(args.edition, sheets)
