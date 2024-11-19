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
    start_time = time.time()  # Track start time for data retrieval
    cards = Card.all()  # Retrieve all cards
    card_list = []

    for card in cards:
        # Dynamically get all attributes from the card object
        card_info = {attr: getattr(card, attr, None) for attr in card.__dict__.keys()}
        card_list.append(card_info)

    retrieval_time = time.time() - start_time  # Calculate data retrieval time
    print(f"Data retrieval completed in {retrieval_time:.2f} seconds.")
    return card_list

def save_data_to_json(card_list):
    """Save card data to a JSON file."""
    directory = os.path.expanduser("~/raw_data")  # Expand ~ to home directory
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, "mtg_data.json")

    # Save the card list to JSON file
    start_time = time.time()
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(card_list, json_file, ensure_ascii=False, indent=4)

    save_time = time.time() - start_time  # Calculate time to save data
    print(f"Data saved to {file_path} in {save_time:.2f} seconds.")

if __name__ == "__main__":
    # Load and save card data
    card_list = load_card_data()
    save_data_to_json(card_list)
