import argparse
import decker.codex as dx


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path",
                        help="editions directory",
                        default="editions")
    parser.add_argument("-c", "--codex",
                        help="codex filename",
                        default="codex.csv")

    args = parser.parse_args()

    codex = dx.fetch_codex()
    dx.update_codex(args.path, codex)
    dx.write_codex(args.codex, codex)
