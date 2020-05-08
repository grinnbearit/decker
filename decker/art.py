import operator as o
import itertools as it
import decker.codex as dx
import decker.layout as dl
import decker.edition as de
from collections import OrderedDict
from swissknife.collections import OrderedDefaultDict


def generate_pnglists(wallex, length=3, minimum=1, rollover=True):
    """
    Wallex should be an Ordered Dictionary of {category: [pngids]}

    Returns a list of pnglists where each pnglist contains pngids from the same category

    length: the number of pngs in each pnglist
    minimum: the number of items necessary for a category to be consisdered
    rollover: If True, ensures that the last pnglist generated adds items from the one before to reach `length`
    """
    acc = []
    for (_, pngids) in wallex.items():
        if len(pngids) > minimum:
            for chunk in [pngids[x:x+length] for x in range(0, len(pngids) - (len(pngids) % length), length)]:
                acc.append(tuple(chunk))

            if rollover:
                acc.append(tuple(pngids[-length:]))
            else:
                acc.append(tuple(pngids[-(len(pngids) % length):]))
    return acc


def render_pnglists(path, pnglists):
    """
    returns imglists corresponding to the passed pnglists
    """
    images = de.render_pngids(path, list(it.chain(*pnglists)))
    cropped = [dl.border_crop(image) for image in images]
    indices = list(it.accumulate([len(pnglist) for pnglist in pnglists]))
    return [cropped[start:stop] for (start, stop) in zip([0]+indices, indices)]


def encode_pngid(pngid):
    """
    converts a pngid into a string
    """
    (edition, page, column, row) = pngid
    offset = page * 100 + column * 10 + row
    return f"{edition}{offset}"


def encode_pnglist(pnglist):
    """
    encodes a list of pngids into a string
    """
    return "".join(encode_pngid(pngid) for pngid in pnglist)


def read_artex(path, codex, newest=None, oldest=None, ignore=set()):
    """
    Using a codex, returns a map of {artist_id: [pngid]} where
    pngids are sorted from oldest to newest. Newer versions of the
    same illustration replace the original.

    path: the editions path
    codex: a sorted list of downloaded editions
    newest: the newest edition to consider
    oldest: the oldest edition to consider
    ignore: a set of editions to ignore
    """

    artist_illustrations = OrderedDefaultDict(OrderedDict)
    for edition in reversed(dx.filter_editions(codex, newest, oldest, ignore)):
        for card in de.read_edition(path, edition):
            if card["artist"] == "":
                continue

            elif de.is_double_faced(card):
                for face in card["card_faces"]:
                    illustrations = artist_illustrations[face["artist_id"]]
                    if (face["illustration_id"] not in illustrations) or \
                       (illustrations[face["illustration_id"]][0] <= card["released_at"]):
                        illustrations[face["illustration_id"]] = (card["released_at"], face["pngid"])
            else:
                for artist_id in card["artist_ids"]:
                    illustrations = artist_illustrations[artist_id]
                    if (card["illustration_id"] not in illustrations) or \
                       (illustrations[card["illustration_id"]][0] <= card["released_at"]):
                        illustrations[card["illustration_id"]] = (card["released_at"], card["pngid"])

    acc = OrderedDefaultDict(list)
    for (artist_id, illustrations) in artist_illustrations.items():
        for (_, (_, pngid)) in illustrations.items():
            acc[artist_id].append(pngid)

    return acc
