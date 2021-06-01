import argparse
import decker.edition as de


# editions without metadata
SKIP = set(["twisted","modern","uncommon","vintage","protour","grixis","arena","tinkerer","livethedream"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--codex",
                        help="codex filename")

    args = parser.parse_args()

    codex = de.fetch_codex()
    filtered = [row for row in codex if row["edition"] not in SKIP]
    de.write_codex(args.codex, filtered)
