import os
import argparse
import itertools as it
import decker.art as da
import decker.codex as dx
import decker.layout as dl
import decker.edition as de
from collections import defaultdict


def generate_pnglists(artex, length):
    """
    returns a list of pnglists where each pnglist contains pngids from the same artist
    `length` determines the number of pngs in the pnglist
    """
    acc = []
    for (_, pngids) in artex.items():
        for chunk in [pngids[x:x+length] for x in range(0, len(pngids), length)]:
            acc.append(chunk)
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path",
                        help="editions directory",
                        default="editions")
    parser.add_argument("-w", "--wallpapers",
                        help="wallpapers directory",
                        required=True)
    parser.add_argument("-i", "--ignore",
                        help="ignored editions",
                        nargs='+')
    parser.add_argument("-n", "--newest",
                        help="newest edition to consider")
    parser.add_argument("-o", "--oldest",
                        help="oldest edition to consider")
    parser.add_argument("-c", "--current",
                        help="the current edition (for removal)")
    parser.add_argument("-s", "--show",
                        help="lists wallpapers instead of generating them," +\
                        " combined with -r to list obsolete wallpapers",
                        action="store_true")
    parser.add_argument("-r", "--remove",
                        help="deletes obsolete wallpapers, doesn't generate new ones," +\
                        " requires --current",
                        action="store_true")
    parser.add_argument("--start", type=int,
                        help="wallpaper to start from")
    parser.add_argument("--end", type=int,
                        help="wallpaper to end at")

    args = parser.parse_args()

    igset = set(args.ignore) if args.ignore else set()
    codex = dx.read_codex("codex.csv")
    artex = da.read_artex(args.path, codex, args.newest, args.oldest, igset)
    pnglists = generate_pnglists(artex, 3)

    if args.remove and (args.current is None):
        parser.error("--remove requires --current")

    if args.remove:
        old_artex = da.read_artex(args.path, codex, args.current, args.oldest, igset)
        old_pnglists = generate_pnglists(old_artex, 3)
        old_encoded = [encode_pnglist(pnglist) + ".png" for pnglist in old_pnglists]
        new_encoded = [encode_pnglist(pnglist) + ".png" for pnglist in pnglists]
        obsolete = set(old_encoded).difference(set(new_encoded))
        if args.show:
            for encoded in obsolete:
                print(encoded)
            print(len(obsolete))
        else:
            for encoded in obsolete:
                os.remove("{}/{}".format(args.wallpapers, encoded))
        exit(0)

    if args.show:
        for pnglist in pnglists:
            print(encode_pnglist(pnglist) + ".png")
        print(len(pnglists))
        exit(0)

    sublists = pnglists[(args.start or 0):(args.end or -1)]
    imglists = render_pnglists(args.path, sublists)
    for (pnglist, imglist) in zip(sublists, imglists):
        sheets = dl.layout(imglist, (1, len(imglist)))
        filename = "{}/{}.png".format(args.wallpapers, encode_pnglist(pnglist))
        dl.write_sheets(filename, sheets)
    exit(0)
