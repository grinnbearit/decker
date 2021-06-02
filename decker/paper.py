import time
import requests as r
from PIL import Image
from io import BytesIO
import decker.core as dc


def face_to_image(face):
    """
    downloads an image from scryfall,
    sleeps after the request for rate limiting
    """
    face_url = face["image_uris"]["png"]
    response = r.get(face_url)
    image = Image.open(BytesIO(response.content))
    time.sleep(0.050)
    return image


def deck_to_images(index, deck):
    """
    converts a deck into a list of images
    """
    images = []
    for deckline in deck:
        card = index[deckline["edition"]][deckline["collector_number"]]

        if dc.is_double_faced(card):
            for face in card["card_faces"]:
                image = face_to_image(face)
                images.append(image)
                for _ in range(deckline["count"]-1):
                    images.append(image.copy())

        else:
            image = face_to_image(card)
            images.append(image)
            for _ in range(deckline["count"]-1):
                images.append(image.copy())

    return images


def back_to_images(back, count):
    """
    returns `count` images of the card back `back`
    """
    if back == "planar":
        back_url = "http://cloud-3.steamusercontent.com/ugc/998016607072060000/1713AE8643632456D06F1BBA962C5514DD8CCC76/"
    elif back == "scheme":
        back_url = "http://cloud-3.steamusercontent.com/ugc/998016607072055936/0598975AB8EC26E8956D84F9EC73BBE5754E6C80/"
    else:
        back_url = "http://cloud-3.steamusercontent.com/ugc/998016607072060763/7AFEF2CE9E7A7DB735C93CF33CC4C378CBF4B20D/"

    response = r.get(back_url)

    images = []
    image = Image.open(BytesIO(response.content))
    for _ in range(count):
        images.append(image.copy())
    return images
