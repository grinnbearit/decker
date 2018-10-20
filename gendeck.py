import csv
import argparse
from PIL import Image


def read_deck(deck_file):
    """
    reads a csv deck file and returns a list of (edition, name, count) tuples
    """
    acc = []
    with open(deck_file, "r") as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            acc.append({"edition": row["edition"],
                        "name": row["name"],
                        "count": int(row["count"])})
    return acc


def deck_editions(deck):
    """
    given a deck, returns a set of editions that it uses
    """
    return set([card["edition"] for card in deck])


def read_index(path, editions):
    """
    loads a list of editions into an index
    """
    acc = {}
    for edition in editions:
        acc[edition] = {}
        with open("{}/{}.csv".format(path, edition), "r") as fp:
            reader = csv.DictReader(fp)
            for row in reader:
                acc[edition][row["name"]] = {"page": int(row["page"]),
                                             "column": int(row["column"]),
                                             "row": int(row["row"])}
    return acc


def check_deck(index, deck):
    """
    returns a list of missing cards, if none are missing
    returns an empty list
    """
    acc = []
    for card in deck:
        if card["edition"] not in index or\
           card["name"] not in index[card["edition"]]:
            acc.append(card)
    return acc


def deck_pages(index, deck):
    """
    given a deck, returns a list of pages it uses
    """
    return set([(card["edition"], index[card["edition"]][card["name"]]["page"])
                for card in deck])


def read_pngdex(path, pages):
    """
    loads a list of image sheets into a png index
    """
    acc = {}
    for (edition, page) in pages:
        if edition not in acc:
            acc[edition] = {}
        acc[edition][page] = Image.open("{}/{}_{:03d}.png".format(path, edition, page))
    return acc


def slice_card(index, pngdex, card):
    """
    returns the Image object for the card
    """
    coords = index[card["edition"]][card["name"]]
    png = pngdex[card["edition"]][coords["page"]]
    width = png.size[0]/10
    height = png.size[1]/10
    column = width * coords["column"]
    row = height * coords["row"]
    box = (column, row, column+width, row+height)
    return png.crop(box)


def slice_deck(index, pngdex, deck):
    """
    returns a list of Image objects for the passed deck
    """
    acc = []
    for card in deck:
        image = slice_card(index, pngdex, card)
        acc.append(image)
        for _ in range(1, card["count"]):
            acc.append(image.copy())
    return acc


def dimensions(frmt):
    """
    translates a format type into (columns, rows)
    """
    formats = {"A3": (6, 3),
               "A4": (3, 3),
               "TTS": (10, 7)}
    if frmt in formats:
        return formats[frmt]
    raise Exception("Unsupported format")


def layout(images, dimensions=(6, 3)):
    """
    lays out sheets of images, side by side, according to the passed dimensions (cols, rows)
    returns an array of new image sheets, assumes all passed cards are the same size
    """

    im = images[0]
    (width, height) = im.size

    (cols, rows) = dimensions

    cards_per_sheet = cols * rows
    chunks = [images[x:x+cards_per_sheet] for x in range(0, len(images), cards_per_sheet)]

    sheets = []
    for chunk in chunks:
        sheet = Image.new("RGB", (width * cols, height * rows), "white")

        for (idx, image) in zip(range(cards_per_sheet), chunk):
            col = idx % cols
            row = idx // cols
            sheet.paste(image, (width * col, height * row))

        sheets.append(sheet)

    return sheets


def read_back(filename):
    back = Image.open(filename)
    return back


def layout_backs(back, dimensions=(3, 6)):
    (width, height) = back.size
    (rows, cols) = dimensions
    sheet = Image.new("RGB", (width * cols, height * rows), "white")
    for row in range(rows):
        for col in range(cols):
            sheet.paste(back, (width * col, height * row))
    return sheet


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", '--deck',
                        help="deck filename",
                        required=True)
    parser.add_argument("-o", "--output",
                        help="image output",
                        required=True)
    parser.add_argument("-s", "--sets",
                        help="sets directory",
                        default="sets")
    parser.add_argument('-f', "--format",
                        help="A3/A4/TTS",
                        default="A3")
    parser.add_argument('-b', '--back',
                        help="add sheet of backs",
                        action="store_true")

    args = parser.parse_args()

    deck = read_deck(args.deck)
    editions = deck_editions(deck)
    index = read_index(args.sets, editions)

    missing_cards = check_deck(index, deck)

    if missing_cards:
        print("{0} missing".format(len(missing_cards)))
        for card in missing_cards:
            print("{0}, {1}".format(card["edition"], card["name"]))
        exit(1)

    pages = deck_pages(index, deck)
    pngdex = read_pngdex(args.sets, pages)

    dims = dimensions(args.format)
    images = slice_deck(index, pngdex, deck)
    sheets = layout(images, dims)

    if len(sheets) == 1:
        sheets[0].save(args.output)
    else:
        for idx in range(len(sheets)):
            sheets[idx].save("%03d_%s" % (idx, args.output))

    if args.back:
        back = read_back("back.png")
        sheet = layout_backs(back, dims)
        sheet.save("back_%s" % args.output)
