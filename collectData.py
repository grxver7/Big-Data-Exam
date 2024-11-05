import requests
import time

def get_mt_card(card_id):
    url = f"https://api.magicthegathering.io/v1/cards/{card_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        card_data = response.json()
        return card_data
    else:
        print(f"Error: Unable to fetch card data for card ID {card_id}. Status code {response.status_code}")
        return None

def load_card_data(start_id, batch_size):
    all_card_info = []
    current_id = start_id

    while True:  # Run indefinitely, modify this condition as needed
        card_info = get_mt_card(current_id)
        if card_info:
            all_card_info.append(card_info)
            print(f"Fetched card info for card ID {current_id}: {card_info}")

        # Wait for 10 seconds before fetching the next card
        time.sleep(10)
        
        current_id += 1  # Move to the next card ID

        # Optional: Stop after fetching a certain number of cards
        if len(all_card_info) >= batch_size:
            break

    return all_card_info

# Example usage
start_id = 1  # Start fetching from card number 1
batch_size = 1  # Adjust this to limit the number of cards fetched
all_card_data = load_card_data(start_id, batch_size)

# Process all_card_data as needed
