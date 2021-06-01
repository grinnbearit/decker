import argparse
import decker.codex as dx


# editions without metadata
SKIP = set(["twisted","modern","uncommon", "legacy", "vintage","protour","grixis","arena","tinkerer","livethedream"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path",
                        help="editions directory",
                        default="editions")
    parser.add_argument("-c", "--codex",
                        help="codex filename")

    args = parser.parse_args()

    codex = dx.fetch_codex()
    filtered = [row for row in codex if row["edition"] not in SKIP]
    dx.update_codex(args.path, filtered)
    dx.write_codex(args.codex, filtered)
