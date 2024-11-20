#!/usr/bin/env python
# coding: utf-8
import json
import os
import time
import subprocess
from concurrent.futures import ThreadPoolExecutor
from mtgsdk import Card

def load_card_data():
    start_time = time.time()  # Start time for data retrieval
    cards = Card.all()  # Retrieve all cards
    loading_time = time.time() - start_time  # Calculate retrieval time

    # Directly use list comprehension for faster construction
    card_list = [
        {
            "name": card.name,
            "multiverse_id": card.multiverse_id,
            "layout": card.layout,
            "names": card.names,
            "mana_cost": card.mana_cost,
            "cmc": card.cmc,
            "colors": card.colors,
            "color_identity": card.color_identity,
            "type": card.type,
            "supertypes": card.supertypes,
            "subtypes": card.subtypes,
            "rarity": card.rarity,
            "text": card.text,
            "flavor": card.flavor,
            "artist": card.artist,
            "number": card.number,
            "power": card.power,
            "toughness": card.toughness,
            "loyalty": card.loyalty,
            "variations": card.variations,
            "watermark": card.watermark,
            "border": card.border,
            "timeshifted": card.timeshifted,
            "hand": card.hand,
            "life": card.life,
            "reserved": card.reserved,
            "release_date": card.release_date,
            "starter": card.starter,
            "rulings": card.rulings,
            "foreign_names": card.foreign_names,
            "printings": card.printings,
            "original_text": card.original_text,
            "original_type": card.original_type,
            "legalities": card.legalities,
            "source": card.source,
            "image_url": card.image_url,
            "set": card.set,
            "set_name": card.set_name,
            "id": card.id
        }
        for card in cards
    ]
    
    retrieval_time = time.time() - start_time  # Calculate loading time
    return card_list, retrieval_time

def save_data_to_json(card_list):
    # Define the target directory and file path
    directory = os.path.expanduser("~/raw_data/")  # Expand ~ to home directory
    file_path = os.path.join(directory, "mtg_data.json")

    # Ensure the directory exists
    os.makedirs(directory, exist_ok=True)

    start_time = time.time()  # Start time for saving data

    # Save card information to mtg_data.json
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(card_list, json_file, ensure_ascii=False, indent=4)

    save_time = time.time() - start_time  # Calculate save time
    print(f"All card data has been saved to {file_path} in {save_time:.2f} seconds.")
    return file_path

# Create the HDFS directory if it doesn't exist
def create_hdfs_directory():
    try:
        subprocess.run(["hadoop", "fs", "-test", "-d", "/user/hadoop/data/raw"], check=True)
    except subprocess.CalledProcessError:
        subprocess.run(["hadoop", "fs", "-mkdir", "-p", "/user/hadoop/data/raw"], check=True)

def delete_all_old_data():
    # Directly remove old data if present
    subprocess.run(["hadoop", "fs", "-rm", "-r", "/user/hadoop/data/raw/*"], check=True)

def upload_to_hdfs(local_file, hdfs_path):
    # Check if the local file exists
    if not os.path.exists(local_file):
        print(f"{local_file} does not exist. Exiting upload.")
        return

    # Upload the file to HDFS
    subprocess.run(["hadoop", "fs", "-put", local_file, hdfs_path], check=True)
    print(f"Data successfully uploaded to HDFS at {hdfs_path}.")

def process_and_upload():
    # Load card data and save it to a JSON file
    card_list, retrieval_time = load_card_data()
    print(f"Data retrieval time: {retrieval_time:.2f} seconds.")
    
    # Save data to local JSON file
    local_file = save_data_to_json(card_list)
    
    # Define the HDFS path
    hdfs_path = "/user/hadoop/data/raw/mtg_data.json"
    
    # Create HDFS directory if it doesn't exist and delete old data
    create_hdfs_directory()
    delete_all_old_data()
    
    # Upload the data to HDFS
    upload_to_hdfs(local_file, hdfs_path)

# Run the script
if __name__ == "__main__":
    start_time = time.time()
    process_and_upload()
    total_time = time.time() - start_time
    print(f"Total process time: {total_time:.2f} seconds.")