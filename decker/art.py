import operator as o
import decker.codex as dx
import decker.edition as de
from collections import OrderedDict
from swissknife.collections import OrderedDefaultDict


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
