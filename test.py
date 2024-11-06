import json
from mtgsdk import Card

def load_and_save_card():
    card = Card.find(386616)
    
    # Extract the card's information into a dictionary, using getattr() to handle missing attributes
    card_info = {
        "name": getattr(card, "name", None),
        "multiverse_id": getattr(card, "multiverse_id", None),
        "layout": getattr(card, "layout", None),
        "names": getattr(card, "names", None),
        "mana_cost": getattr(card, "mana_cost", None),
        "cmc": getattr(card, "cmc", None),
        "colors": getattr(card, "colors", None),
        "color_identity": getattr(card, "color_identity", None),
        "type": getattr(card, "type", None),
        "supertypes": getattr(card, "supertypes", None),
        "subtypes": getattr(card, "subtypes", None),
        "rarity": getattr(card, "rarity", None),
        "text": getattr(card, "text", None),
        "flavor": getattr(card, "flavor", None),
        "artist": getattr(card, "artist", None),
        "number": getattr(card, "number", None),
        "power": getattr(card, "power", None),
        "toughness": getattr(card, "toughness", None),
        "loyalty": getattr(card, "loyalty", None),
        "variations": getattr(card, "variations", None),
        "watermark": getattr(card, "watermark", None),
        "border": getattr(card, "border", None),
        "timeshifted": getattr(card, "timeshifted", None),
        "hand": getattr(card, "hand", None),
        "life": getattr(card, "life", None),
        "reserved": getattr(card, "reserved", None),
        "release_date": getattr(card, "release_date", None),
        "starter": getattr(card, "starter", None),
        "rulings": getattr(card, "rulings", None),
        "foreign_names": getattr(card, "foreign_names", None),
        "printings": getattr(card, "printings", None),
        "original_text": getattr(card, "original_text", None),
        "original_type": getattr(card, "original_type", None),
        "legalities": getattr(card, "legalities", None),
        "source": getattr(card, "source", None),
        "image_url": getattr(card, "image_url", None),
        "set": getattr(card, "set", None),
        "set_name": getattr(card, "set_name", None),
        "id": getattr(card, "id", None)
    }
    
    # Save the card information to data.json
    with open("data.json", "w", encoding="utf-8") as json_file:
        json.dump(card_info, json_file, ensure_ascii=False, indent=4)
    
    print("Card data has been saved to data.json")

# Call the function to load and save the card information
load_and_save_card()
