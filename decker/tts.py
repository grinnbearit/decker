import json


def card_to_objectstate(index, edition, collector_number):
    """
    returns an object state dict for a TTS deck
    """
    card = index[edition][collector_number]
    face_url = card["image_uris"]["png"]

    # taken from https://github.com/jeandeaual/tts-deckconverter
    if card["layout"] in ["normal", "token", "split", "flip", "leveler", "emblem"]:
        back_url = "http://cloud-3.steamusercontent.com/ugc/998016607072060763/7AFEF2CE9E7A7DB735C93CF33CC4C378CBF4B20D/"
    elif card["layout"] == "planar":
        back_url = "http://cloud-3.steamusercontent.com/ugc/998016607072060000/1713AE8643632456D06F1BBA962C5514DD8CCC76/"
    elif card["layout"] == "scheme":
        back_url = "http://cloud-3.steamusercontent.com/ugc/998016607072055936/0598975AB8EC26E8956D84F9EC73BBE5754E6C80/"

    object_state = {
        "FaceURL": face_url,
        "BackURL": back_url,
        "NumWidth": 1,
        "NumHeight": 1,
        "BackIsHidden": True,
        "UniqueBack": False,
        "Type": 0
    }
    return object_state


def card_to_description(card):
    """
    returns a description given a card layout
    """
    if card["layout"] in ["normal", "token", "planar", "leveler", "scheme", "emblem"]:
        description = "[b]{}[/b]\n\n{}".format(card["type_line"], card["oracle_text"])
    elif card["layout"] in ["split", "flip"]:
        acc = []
        for face in card["card_faces"]:
            acc.append("[b]{}[/b]\n\n{}".format(face["type_line"], face["oracle_text"]))
        description = "\n\n--------------------------\n\n".join(acc)

    return description


def card_to_containedobject(index, edition, collector_number, card_id, object_state):
    """
    returns a contained object dict for a TTS deck
    """
    card = index[edition][collector_number]
    nickname = card["name"]
    description = card_to_description(card)
    idx = str(card_id//100)
    custom_deck = {idx: object_state}

    contained_object = {"Name": "Card",
                        "Transform": {"posX": 0.0, "posY": 0.0, "posZ": 0.0,
                                      "rotX": 0.0, "rotY": 180.0, "rotZ": 0.0,
                                      "scaleX": 1.1339285, "scaleY": 1.0, "scaleZ": 1.11125},
                        "Nickname": nickname,
                        "Description": description,
                        "GMNotes": "",
                        "ColorDiffuse": {"r": 0.71323913, "g": 0.71323913, "b": 0.71323913},
                        "Locked": False,
                        "Grid": True,
                        "Snap": True,
                        "IgnoreFoW": False,
                        "MeasureMovement": False,
                        "DragSelectable": True,
                        "Autoraise": True,
                        "Sticky": True,
                        "Tooltip": True,
                        "GridProjection": False,
                        "HideWhenFaceDown": True,
                        "Hands": True,
                        "CardID": card_id,
                        "SidewaysCard": False,
                        "CustomDeck": custom_deck,
                        "XmlUI": "",
                        "LuaScript": "",
                        "LuaScriptState": "",
                        "GUID": ""}

    return contained_object


def deck_to_ttscard(index, edition, collector_number):
    """
    returns a dict representing a tts card
    """
    object_state = card_to_objectstate(index, edition, collector_number)
    contained_object = card_to_containedobject(index, edition, collector_number, 100, object_state)
    ttscard = {"SaveName": "",
               "GameMode": "",
               "Gravity": 0.5,
               "PlayArea": 0.5,
               "Date": "",
               "Table": "",
               "Sky": "",
               "Note": "",
               "Rules": "",
               "LuaScript": "",
               "LuaScriptState": "",
               "XmlUI": "",
               "ObjectStates": [contained_object],
               "TabStates": {},
               "VersionNumber": ""}
    return ttscard


def deck_to_ttsdeck(index, deck):
    """
    returns a dict representing a tts deck
    """
    exploded_deck = []
    for deckline in deck:
        exploded_card = [(deckline["edition"], deckline["collector_number"])]*deckline["count"]
        exploded_deck.extend(exploded_card)

    if len(exploded_deck) == 1:
        (edition, collector_number) = exploded_deck[0]
        return deck_to_ttscard(index, edition, collector_number)

    custom_deck = {}
    contained_objects = []
    deck_ids = list(range(100, (len(exploded_deck)+1)*100, 100))
    for (card_id, (edition, collector_number)) in zip(deck_ids, exploded_deck):
        idx = str(card_id//100)
        object_state = card_to_objectstate(index, edition, collector_number)
        custom_deck[idx] = object_state
        contained_object = card_to_containedobject(index, edition, collector_number, card_id, object_state)
        contained_objects.append(contained_object)

    ttsdeck = {"SaveName": "",
               "GameMode": "",
               "Gravity": 0.5,
               "PlayArea": 0.5,
               "Date": "",
               "Table": "",
               "Sky": "",
               "Note": "",
               "Rules": "",
               "LuaScript": "",
               "LuaScriptState": "",
               "XmlUI": "",
               "ObjectStates": [{"Name": "Deck",
                                 "Transform": {"posX": 0.0, "posY": 0.0, "posZ": 0.0,
                                               "rotX": 0.0, "rotY": 180.0, "rotZ": 180.0,
                                               "scaleX": 1.1339285, "scaleY": 1.0, "scaleZ": 1.11125},
                                 "Nickname": "",
                                 "Description": "",
                                 "GMNotes": "",
                                 "ColorDiffuse": {"r": 0.71323913, "g": 0.71323913, "b": 0.71323913},
                                 "Locked": False,
                                 "Grid": True,
                                 "Snap": True,
                                 "IgnoreFoW": False,
                                 "MeasureMovement": False,
                                 "DragSelectable": True,
                                 "Autoraise": True,
                                 "Sticky": True,
                                 "Tooltip": True,
                                 "GridProjection": False,
                                 "HideWhenFaceDown": True,
                                 "Hands": False,
                                 "SidewaysCard": False,
                                 "DeckIDs": deck_ids,
                                 "CustomDeck": custom_deck,
                                 "XmlUI": "",
                                 "LuaScript": "",
                                 "LuaScriptState": "",
                                 "ContainedObjects": contained_objects,
                                 "GUID": ""}],
               "TabStates": {},
               "VersionNumber": ""}

    return ttsdeck
