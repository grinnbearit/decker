import time
import requests as r
from PIL import Image


def check_deck(deck):
    """
    returns a list of missing cards, if none are missing
    returns an empty list
    """
    acc = []
    for deckline in deck:
        response = r.head("https://api.scryfall.com/cards/named",
                          params={"set": deckline["edition"],
                                  "exact": deckline["name"]})
        if not response.ok:
            acc.append(deckline)

    time.sleep(0.050)       # Time between requests

    return acc


def fetch_deck(deck, size=None):
    """
    returns a list of Image objects for the passed deck
    """
    acc = []
    for deckline in deck:
        response = r.get("https://api.scryfall.com/cards/named",
                         params={"set": deckline["edition"],
                                 "exact": deckline["name"],
                                 "format": "image",
                                 "version": "png"},
                         stream=True)

        image = Image.open(response.raw)
        acc.append(image)

        for _ in range(1, deckline["count"]):
            acc.append(image.copy())

        time.sleep(0.050)       # Time between requests

    return acc
