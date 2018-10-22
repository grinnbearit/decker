import time
import requests as r
from PIL import Image


def check_card(card):
    """
    returns True if the card is found on scryfall, else False
    """
    response = r.head("https://api.scryfall.com/cards/named",
                      params={"set": card["edition"],
                              "exact": card["name"]})
    return response.ok


def check_deck(deck):
    """
    returns a list of missing cards, if none are missing
    returns an empty list
    """
    acc = []
    for card in deck:
        if not check_card(card):
            acc.append(card)
        time.sleep(0.050)       # Time between requests
    return acc


def fetch_card(card):
    """
    returns the Image object for the card
    """
    response = r.get("https://api.scryfall.com/cards/named",
                     params={"set": card["edition"], "exact": card["name"],
                             "format": "image", "version": "png"},
                     stream=True)
    return Image.open(response.raw)


def fetch_deck(deck, size=None):
    """
    returns a list of Image objects for the passed deck
    """
    acc = []
    for card in deck:
        image = fetch_card(card)
        acc.append(image)
        for _ in range(1, card["count"]):
            acc.append(image.copy())
        time.sleep(0.050)       # Time between requests
    return acc
