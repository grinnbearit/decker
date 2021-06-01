import argparse
import decker.edition as de


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--codex",
                        help="codex filename")

    args = parser.parse_args()

    codex = de.fetch_codex()
    de.write_codex(args.codex, codex)
