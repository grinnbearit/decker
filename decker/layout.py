from PIL import Image


def dimensions(frmt):
    """
    translates a format type into (columns, rows)
    """
    formats = {"A3": (3, 6),
               "A4": (3, 3)}
    if frmt in formats:
        return formats[frmt]
    raise Exception("Unsupported format")


def layout(images, dimensions=(3, 6), background="white"):
    """
    lays out sheets of images, side by side, according to the passed dimensions (rows, cols)
    returns an array of new image sheets.
    resizes all images to the smallest width height per sheet
    """
    (rows, cols) = dimensions

    cards_per_sheet = rows * cols
    chunks = [images[x:x+cards_per_sheet] for x in range(0, len(images), cards_per_sheet)]

    sheets = []
    for chunk in chunks:
        (width, height) = chunk[0].size

        for image in chunk:
            (new_width, new_height) = image.size
            width = new_width if new_width < width else width
            height = new_height if new_height < height else height

        sheet = Image.new("RGB", (width * cols, height * rows), background)
        for (idx, image) in zip(range(cards_per_sheet), chunk):
            col = idx % cols
            row = idx // cols
            resized = image.resize((width, height))
            sheet.paste(resized, (width * col, height * row), resized)

        sheets.append(sheet)

    return sheets


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


def _split_filename(filename):
    """
    returns (base, name) for sheets when passed a filename enabling
    prefixing.
    """
    path = filename.split("/")
    name = path[-1]
    base = "" if len(path) == 1 else "/".join(path[:-1]) + "/"
    return (base, name)


def write_sheet(filename, sheet, number):
    """
    write image sheet to disk with passed sheet number
    """
    (base, name) =  _split_filename(filename)
    sheet.save(base + "%03d_%s" % (number, name))


def write_sheets(filename, sheets):
    """
    write image sheets to disk
    """
    if len(sheets) == 1:
        sheets[0].save(filename)
    else:
        (base, name) = _split_filename(filename)
        for (idx, sheet) in enumerate(sheets):
            sheet.save(base + "%03d_%s" % (idx, name))
