import json
from mtgsdk import Card
import time

def load_and_save_all_cards():
    start_time = time.time()  # Start time for data retrieval
    cards = Card.all()  # Retrieve all cards
    loading_time = time.time() - start_time  # Calculate retrieval time
    print(f"Data retrieval completed in {loading_time:.2f} seconds.")

    card_list = []
    count = 0  # Counter to track the number of entries

    start_time = time.time()
    # Iterate over each card and extract information
    for card in cards:
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
        card_list.append(card_info)
        count += 1  # Increment the counter

    retrieval_time = time.time() - start_time  # Calculate loading time
    print(f"Data processing completed in {retrieval_time:.2f} seconds.")
    print(f"Total number of cards retrieved: {count}")

    start_time = time.time()  # Start time for saving data
    # Save all card information to data.json
    with open("data.json", "w", encoding="utf-8") as json_file:
        json.dump(card_list, json_file, ensure_ascii=False, indent=4)
    
    save_time = time.time() - start_time  # Calculate save time
    print(f"All card data has been saved to data.json in {save_time:.2f} seconds.")

# Call the function to load and save all card information
load_and_save_all_cards()
