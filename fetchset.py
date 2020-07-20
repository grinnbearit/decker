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

    args = parser.parse_args()

    if not de.check_edition(args.edition):
        print("edition {} not found".format(args.edition))
        exit(1)

    cards = de.fetch_edition(args.edition)
    de.write_edition(args.path, cards)
