import argparse
import itertools as it
import decker.core as dc
import decker.layout as dl
from collections import defaultdict


def artist_reprints(artex):
    """
    returns {artist: [(old_pngid, new_pngid)]} for all their illustrations
    from oldest to newest
    """
    acc = defaultdict(list)
    for (artist, illustrations) in artex.items():
        for (illustration, old_new) in illustrations.items():
            acc[artist].append((old_new["old"][-1] if "old" in old_new else None,
                                old_new["new"][-1] if "new" in old_new else None))
    return acc


def generate_pnglists(artprints, length):
    """
    returns {"new": [pnglist], "unchanged": [pnglist], "updated": [(old_pnglist, new_pnglist)]}
    where `length` determines the number of pngs in the pnglist
    """
    acc = {"new": [], "unchanged": [], "updated": []}
    for (artist, reprints) in artprints.items():
        for chunk in [reprints[x:x+length] for x in range(0, len(reprints), length)]:
            (chunked_old_pngids, chunked_new_pngids) = zip(*chunk)
            if any(chunked_old_pngids) and any(chunked_new_pngids):
                old_pngids = [pngid for pngid in chunked_old_pngids if pngid]
                new_pngids = [new_pngid or old_pngid for (old_pngid, new_pngid) in chunk]
                acc["updated"].append((old_pngids, new_pngids))
            elif any(chunked_old_pngids):
                old_pngids = [pngid for pngid in chunked_old_pngids if pngid]
                acc["unchanged"].append(old_pngids)
            else:
                new_pngids = [pngid for pngid in chunked_new_pngids if pngid]
                acc["new"].append(new_pngids)
    return acc


def render_pnglists(path, pnglists):
    """
    returns imglists corresponding to the passed pnglists
    """
    images = dc.render_pngids(path, list(it.chain(*pnglists)))
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path",
                        help="editions directory",
                        default="editions")
    parser.add_argument("-i", "--ignore",
                        help="ignored editions",
                        nargs='+')
    parser.add_argument("-n", "--newest",
                        help="newest edition to consider")
    parser.add_argument("-o", "--oldest",
                        help="oldest edition to consider")
    parser.add_argument("-c", "--current",
                        help="current edition (last updated)")
    parser.add_argument("-r", "--remove",
                        help="prints a command to delete updated pngs",
                        action="store_true")
    parser.add_argument("-l", "--layout",
                        help="wallpaper layout",
                        nargs=2, type=int, default=(1, 3))
    parser.add_argument("-g", "--generate",
                        help="generates new and updated wallpapers",
                        action="store_true")

    args = parser.parse_args()

    edset = set(args.ignore) if args.ignore else set()
    codex = dc.read_codex("codex.csv")
    artex = dc.read_artex(args.path, codex, args.newest, args.oldest, edset, args.current)
    artprints = artist_reprints(artex)

    (rows, columns) = args.layout
    categorised = generate_pnglists(artprints, rows*columns)

    if args.generate:
        new_pnglists = categorised["new"] + [new_pngid for (_, new_pngid)
                                             in categorised["updated"]]
        imglists = render_pnglists(args.path, new_pnglists)
        for (pnglist, imglist) in zip(new_pnglists, imglists):
            sheets = dl.layout(imglist, (columns, rows))
            filename = encode_pnglist(pnglist) + ".png"
            dl.write_sheets(filename, sheets)
        exit(0)

    if args.remove:
        files = [encode_pnglist(old_pnglist) + ".png"
                 for (old_pnglist, _) in categorised["updated"]]
        print("rm " + " ".join(files))
        exit(0)

    if categorised["unchanged"]:
        print("unchanged:")
        for old_pnglist in categorised["unchanged"]:
            print(encode_pnglist(old_pnglist))
        print()

    if categorised["updated"]:
        print("updated:")
        for (old_pnglist, new_pnglist) in categorised["updated"]:
            print("{} -> {}".format(encode_pnglist(old_pnglist),
                                    encode_pnglist(new_pnglist)))
        print()

    if categorised["new"]:
        print("new:")
        for new_pnglist in categorised["new"]:
            print(encode_pnglist(new_pnglist))
