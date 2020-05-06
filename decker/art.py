import decker.codex as dx
import decker.edition as de
from collections import defaultdict
from swissknife.collections import OrderedDefaultDict


def read_artex(path, codex, newest=None, oldest=None, ignore=set(), current=None):
    """
    Using a codex, returns a map of {artist_id: {illustration_id: {new: [pngid], old: [pngid]} where
    pngids are sorted from oldest to newest. `new` are pngids released after `current` and `old`
    includes `current`.

    `illustration_ids` are stored in an OrderedDict, sorted from oldest to newest

    path: the editions path
    codex: a sorted list of downloaded editions
    newest: the newest edition to consider
    oldest: the oldest edition to consider
    ignore: a set of editions to ignore
    current: the current edition
    """
    acc = defaultdict(lambda: OrderedDefaultDict(lambda: defaultdict(list)))
    (neweds, oldeds) = dx.filter_editions(codex, newest, oldest, ignore, current)
    edlist = [("new", e) for e in neweds] + [("old", e) for e in oldeds]
    edlist.reverse()
    for (old_new, edition) in edlist:
        cards = de.read_edition(path, edition)
        for card in cards:
            if de.is_double_faced(card):
                for face in card["card_faces"]:
                    acc[face["artist_id"]][face["illustration_id"]][old_new].append(face["pngid"])
            elif card["artist"] == "":
                continue
            else:
                for artist_id in card["artist_ids"]:
                    acc[artist_id][card["illustration_id"]][old_new].append(card["pngid"])
    return acc
