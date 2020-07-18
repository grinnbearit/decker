import os
import argparse
import decker.edition as de


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path",
                        help="editions directory",
                        default="editions")
    parser.add_argument('-e', '--edition',
                        help="edition code",
                        required=True)
    parser.add_argument("--progress",
                        help="prints fetch set progress",
                        action="store_true")
    parser.add_argument("--start", type=int,
                        help="card from edition to start from")
    parser.add_argument("--end", type=int,
                        help="card from edition to end at")
    parser.add_argument("-m", "--metadata",
                        help="if set, doesn't redownload card list",
                        action="store_true")

    args = parser.parse_args()

    if not de.check_edition(args.edition):
        print("edition {} not found".format(args.edition))
        exit(1)

    if args.metadata:
        cards = de.read_edition(args.path, args.edition)
    else:
        cards = de.fetch_edition(args.edition)
        de.write_edition(args.path, cards)

    subcards = cards[slice(args.start or 0, args.end or None)]
    imdix = de.fetch_imdix(subcards, args.progress)

    de.upsert_sheets(args.path, args.edition, imdix)
