import decker.core as dc
import decker.codex as dx
import decker.paper as dp
import decker.layout as dl
import decker.edition as de
from ordered_set import OrderedSet
from collections import OrderedDict
from swissknife.collections import OrderedDefaultDict


def read_printex(path, editions):
    """
    Generates a mapping of card name to unique illustrations
    `editions` is a list of all relevant editions from newest to oldest

    returns a map of {name: [fid]} where fid is a tuple of (edition, collector_number, is_back)
    that uniquely identifies a card face.

    More recent cards with the same illustration replace older ones.

    path: the editions path
    """
    name_illustrations = OrderedDefaultDict(OrderedDict)
    for edition in reversed(editions):
        for card in de.read_edition(path, edition):

            if card["artist"] == "":
                continue

            if (card["layout"] == "normal") &\
               ("illustration_id" not in card):
                continue

            if not card["highres_image"]:
                continue

            if dc.is_double_faced(card):
                fids = [(edition, card["collector_number"], is_back) for is_back in [False, True]]

                for (fid, face) in zip(fids, card["card_faces"]):
                    illustrations = name_illustrations[face["name"]]

                    if (face["illustration_id"] not in illustrations) or \
                       (illustrations[face["illustration_id"]][0] <= card["released_at"]):
                        illustrations[face["illustration_id"]] = (card["released_at"], fid)
            else:
                fid = (edition, card["collector_number"], False)
                illustrations = name_illustrations[card["name"]]

                if (card["illustration_id"] not in illustrations) or \
                   (illustrations[card["illustration_id"]][0] <= card["released_at"]):
                    illustrations[card["illustration_id"]] = (card["released_at"], fid)

    acc = OrderedDefaultDict(list)
    for (name, illustrations) in name_illustrations.items():
        for (_, (_, fid)) in illustrations.items():
            acc[name].append(fid)

    return acc


def read_artex(path, editions):
    """
    Generates a mapping of artist to unique illustrations
    `editions` is a list of all relevant editions from newest to oldest

    returns a map of {name: [fid]} where fid is a tuple of (edition, collector_number, is_back)
    that uniquely identifies a card face.

    More recent cards with the same illustration replace older ones.

    path: the editions path
    """
    artist_illustrations = OrderedDefaultDict(OrderedDict)
    for edition in reversed(editions):
        for card in de.read_edition(path, edition):

            if card["artist"] == "":
                continue

            if (card["layout"] == "normal") &\
               ("illustration_id" not in card):
                continue

            if not card["highres_image"]:
                continue

            if dc.is_double_faced(card):
                fids = [(edition, card["collector_number"], is_back) for is_back in [False, True]]

                for (fid, face) in zip(fids, card["card_faces"]):
                    illustrations = artist_illustrations[face["artist_id"]]

                    if (face["illustration_id"] not in illustrations) or \
                       (illustrations[face["illustration_id"]][0] <= card["released_at"]):
                        illustrations[face["illustration_id"]] = (card["released_at"], fid)
            else:
                fid = (edition, card["collector_number"], False)

                for artist_id in card["artist_ids"]:
                    illustrations = artist_illustrations[artist_id]

                    if (card["illustration_id"] not in illustrations) or \
                       (illustrations[card["illustration_id"]][0] <= card["released_at"]):
                        illustrations[card["illustration_id"]] = (card["released_at"], fid)

    acc = OrderedDefaultDict(list)
    for (artist_id, illustrations) in artist_illustrations.items():
        for (_, (_, fid)) in illustrations.items():
            acc[artist_id].append(fid)

    return acc


def generate_fidlists(wallex, length=3, minimum=3, rollover=True):
    """
    Wallex should be an Ordered Dictionary of {category: [fid]}
    Returns a list of fidlists where each fidlist contains fids from the same category
    length: the number of fids in each fidlist
    minimum: the number of items necessary for a category to be consisdered
    rollover: If True, ensures that the last fidlist generated adds items from the one before to reach `length`
    """
    acc = OrderedSet()
    for (_, fids) in wallex.items():
        modlen = len(fids) % length
        if len(fids) >= minimum:
            for chunk in [fids[x:x+length] for x in range(0, len(fids) - modlen, length)]:
                acc.add(tuple(chunk))

            if modlen > 0:
                if rollover:
                    acc.add(tuple(fids[-length:]))
                else:
                    acc.add(tuple(fids[-modlen:]))
    return acc


def encode_fidlist(fidlist):
    """
    converts a fidlist into a string
    """
    return "_".join(["{0}.{1}.{2}".format(edition, collector_number, 1 if is_back else 0)
                     for (edition, collector_number, is_back)
                     in fidlist])


def decode_fidstr(fidstr):
    """
    converts a string into a fidlist
    """
    acc = []
    for fid in fidstr.split("_"):
        (edition, collector_number, is_back) = fid.split(".")
        acc.append((edition, collector_number, is_back == "1"))
    return tuple(acc)


def fid_to_image(index, fid):
    """
    Converts a fid into an image
    """
    (edition, collector_number, is_back) = fid
    card = index[edition][collector_number]

    if dc.is_double_faced(card):
        face = card["card_faces"][1] if is_back else card["card_faces"][0]
        image = dp.face_to_image(face)
    else:
        image = dp.face_to_image(card)

    return image


def render_fidlist(index, fidlist):
    """
    returns a sheet corresponding to the passed fidlist
    """
    images = [fid_to_image(index, fid) for fid in fidlist]
    sheet = dl.layout(images, (1, 3), "black")[0]
    return sheet
