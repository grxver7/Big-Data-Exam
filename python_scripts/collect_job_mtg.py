#!/usr/bin/env python
# coding: utf-8
import json
import os
import pyspark
from mtgsdk import Card
import time
import subprocess

def load_card_data():
    start_time = time.time()  # Start time for data retrieval
    cards = Card.all()  # Retrieve all cards
    loading_time = time.time() - start_time  # Calculate retrieval time
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
    
    return card_list

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

# Load card data
card_list = load_card_data()

# Save the data
save_data_to_json(card_list)

# Define the local file and HDFS target path
local_file = os.path.expanduser("~/raw_data/mtg_data.json")  # Expand ~ to home directory
hdfs_path = "/user/hadoop/data/raw/mtg_data.json"

# Create the HDFS directory if it doesn't exist
def create_hdfs_directory():
    try:
        subprocess.run(["hadoop", "fs", "-test", "-d", "/user/hadoop/data/raw"], check=True)
    except subprocess.CalledProcessError:
        subprocess.run(["hadoop", "fs", "-mkdir", "-p", "/user/hadoop/data/raw"], check=True)

# Delete all old data in the raw directory
def delete_all_old_data():
    try:
        subprocess.run(["hadoop", "fs", "-rm", "-r", "/user/hadoop/data/raw/*"], check=True)  # Deletes all files in raw directory
        print("Old data deleted from HDFS raw directory.")
    except subprocess.CalledProcessError:
        print("No existing data found in the raw directory, nothing to delete.")

# Upload the new file to HDFS
def upload_to_hdfs():
    # Check if the local file exists
    if not os.path.exists(local_file):
        print(f"{local_file} does not exist. Exiting upload.")
        return

    create_hdfs_directory()
    delete_all_old_data()  # Delete all old data before uploading new data

    result = subprocess.run(
        ["hadoop", "fs", "-put", local_file, hdfs_path],
        check=False,  # Don't raise an error automatically
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    if result.returncode == 0:
        print(f"Data successfully uploaded to HDFS at {hdfs_path}.")
    else:
        print(f"Error uploading data to HDFS: {result.stderr.decode()}")

# Run the script
upload_to_hdfs()