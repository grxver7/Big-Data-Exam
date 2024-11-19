# -*- coding: utf-8 -*-
"""
Collect and save Magic: The Gathering card data to a JSON file
"""

import os
import time
import json
from mtgsdk import Card

def load_card_data():
    """Load MTG card data using the mtgsdk."""
    cards = Card.all()
    card_list = []

    for card in cards:
        card_info = {attr: getattr(card, attr, None) for attr in card.__dict__.keys()}
        card_list.append(card_info)

    return card_list

def save_data_to_json(card_list):
    """Save card data to a JSON file."""
    directory = os.path.expanduser("~/raw_data")
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, "mtg_data.json")

    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(card_list, json_file, ensure_ascii=False, indent=4)
    print(f"Data saved to {file_path}")

if __name__ == "__main__":
    card_list = load_card_data()
    save_data_to_json(card_list)
