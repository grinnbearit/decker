import os
import argparse
import decker.edition as de


def is_edition_highres(cards):
    for card in cards:
        if not card["highres_image"]:
            return False
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path",
                        help="editions directory",
                        default="editions")
    parser.add_argument('-e', '--edition',
                        help="edition code",
                        required=True)
    parser.add_argument("-l", "--lowres",
                        help="stores an edition with some lowres only cards",
                        action="store_true")


    args = parser.parse_args()

    if not de.check_edition(args.edition):
        print("edition {} not found".format(args.edition))
        exit(1)

    cards = de.fetch_edition(args.edition)

    if not args.lowres:
        if not is_edition_highres(cards):
            print(f"not all cards in {args.edition} have highres prints")
            exit(-1)

    de.write_edition(args.path, cards)
