import os, glob
import argparse
import decker.art as da
import decker.core as dc
import decker.codex as dx


def read_wallex(path, art, editions):
    if art == "prints":
        return da.read_printex(path, editions)
    else:
        return da.read_artex(path, editions)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path",
                        help="editions directory",
                        default="editions")
    parser.add_argument("-a", "--art", choices=["artists", "prints"],
                        help="Sets the type of wallpapers generated",
                        required=True)
    parser.add_argument("-i", "--ignore",
                        help="ignored editions",
                        nargs='+')
    parser.add_argument("-n", "--newest",
                        help="newest edition to consider")
    parser.add_argument("-o", "--oldest",
                        help="oldest edition to consider")
    parser.add_argument("-d", "--directory",
                        help="location for sheets",
                        default="~/Pictures")
    parser.add_argument("-l", "--list",
                        help=" list the files to be deleted, kept or created, takes no action",
                        nargs='*', choices=["d", "k", "c"])

    args = parser.parse_args()

    igset = set(args.ignore) if args.ignore else set()
    codex = dx.read_codex("codex.csv")
    editions = dx.filter_editions(codex, args.newest, args.oldest, igset)
    index = dc.read_index(args.path, editions)

    wallex = read_wallex(args.path, args.art, editions)
    fidlists = da.generate_fidlists(wallex)

    directory = os.path.expanduser(args.directory)

    existing = set()
    for filename in os.listdir(directory):
        if filename.endswith(".png"):
            existing.add(da.decode_fidstr(filename[:-4]))


    listset = set(args.list) if args.list else set()

    to_delete = existing.difference(fidlists)
    to_keep = fidlists.intersection(existing)
    to_create = fidlists.difference(existing)

    if listset:
        if "d" in listset and to_delete:
            print("To Delete -")
            for fidlist in to_delete:
                print("{}.png".format(da.encode_fidlist(fidlist)))

        if "k" in listset and to_keep:
            print("To Keep -")
            for fidlist in to_keep:
                print("{}.png".format(da.encode_fidlist(fidlist)))

        if "c" in listset and to_create:
            print("To Create -")
            for fidlist in to_create:
                print("{}.png".format(da.encode_fidlist(fidlist)))

        exit(0)

    directory = os.path.expanduser(args.directory)

    for fidlist in to_delete:
        filename = "{}/{}.png".format(directory, da.encode_fidlist(fidlist))
        os.remove(filename)

    for fidlist in to_create:
        filename = "{}/{}.png".format(directory, da.encode_fidlist(fidlist))
        sheet = da.render_fidlist(index, fidlist)
        sheet.save(filename)
