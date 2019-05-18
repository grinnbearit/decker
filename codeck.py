import argparse
import decker.core as dc


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", '--deck',
                        help="deck filename",
                        required=True)
    parser.add_argument("-s", "--sets",
                        help="sets directory",
                        default="sets")
    parser.add_argument("-a", "--all",
                        help="list all editions",
                        action="store_true")
    parser.add_argument("-i", "--ignore",
                        help="ignored editions",
                        nargs='+')
    parser.add_argument("-n", "--newest",
                        help="newest edition to consider")
    parser.add_argument("-o", "--oldest",
                        help="oldest edition to consider")

    args = parser.parse_args()

    deck = dc.read_deck(args.deck)
    edset = set(args.ignore) if args.ignore else set()
    codex = dc.read_codex(args.sets, args.newest, args.oldest, edset)

    missing_cards = []
    for card in deck:
        name = card["name"]
        if name in codex:
            if args.all:
                editions = ','.join(str(e) for e in codex[name])
                print(f"[{editions}], {name}")
            else:
                edition = codex[name][0]
                print(f"{edition}, {name}")
        else:
            missing_cards.append(name)

    if missing_cards:
        print("\n{0} missing".format(len(missing_cards)))
        for name in missing_cards:
            print(f"{name}")
