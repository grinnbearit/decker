import os
import argparse
import decker.art as da
import decker.codex as dx
import decker.layout as dl


def read_wallex(path, codex, art, newest=None, oldest=None, ignore=set()):
    if art == "artists":
        return da.read_artex(path, codex, newest, oldest, ignore)
    else:
        return da.read_namex(path, codex, newest, oldest, ignore)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path",
                        help="editions directory",
                        default="editions")
    parser.add_argument("-a", "--art", choices=["artists", "names"],
                        help="Sets the type of wallpapers generated",
                        required=True)
    parser.add_argument("-w", "--wallpapers",
                        help="wallpapers directory",
                        default=".")
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
    wallex = read_wallex(args.path, codex, args.art, args.newest, args.oldest, igset)
    pnglists = da.generate_pnglists(wallex)

    if args.current:
        old_wallex =  read_wallex(args.path, codex, args.art, args.current, args.oldest, igset)
        old_pnglists = da.generate_pnglists(old_wallex)
    else:
        old_pnglists = []

    if args.remove:
        obs_pnglists = [pnglist for pnglist in old_pnglists if pnglist not in set(pnglists)]
        if args.show:
            for pnglist in obs_pnglists:
                print(da.encode_pnglist(pnglist))
            print(len(obs_pnglists))
        else:
            for pnglist in obs_pnglists:
                os.remove("{}/{}.png".format(args.wallpapers, da.encode_pnglist(pnglist)))
        exit(0)

    new_pnglists = [pnglist for pnglist in pnglists if pnglist not in set(old_pnglists)]

    if args.show:
        for pnglist in new_pnglists:
            print(da.encode_pnglist(pnglist))
        print(len(new_pnglists))
        exit(0)

    sublists = new_pnglists[(args.start or 0):(args.end or -1)]
    imglists = da.render_pnglists(args.path, sublists)
    for (pnglist, imglist) in zip(sublists, imglists):
        sheets = dl.layout(imglist, (1, len(imglist)))
        filename = "{}/{}.png".format(args.wallpapers, da.encode_pnglist(pnglist))
        dl.write_sheets(filename, sheets)
