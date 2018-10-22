from PIL import Image


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
    """
    returns an Image used for the card back
    """
    back = Image.open(filename)
    return back


def layout_backs(back, dimensions=(6, 3)):
    """
    Lays out backs to be printed
    """
    (width, height) = back.size
    (cols, rows) = dimensions
    sheet = Image.new("RGB", (width * cols, height * rows), "white")
    for row in range(rows):
        for col in range(cols):
            sheet.paste(back, (width * col, height * row))
    return sheet


def write_sheets(filename, sheets):
    """
    write image sheets to disk
    """
    if len(sheets) == 1:
        sheets[0].save(filename)
    else:
        path = filename.split("/")
        name = path[-1]
        base = "" if len(path) == 1 else "/".join(path[:-1]) + "/"

        for (idx, sheet) in enumerate(sheets):
            sheet.save(base + "%03d_%s" % (idx, name))
