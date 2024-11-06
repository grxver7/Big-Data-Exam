import requests

def get_mt_card(card_id):
    url = f"https://api.magicthegathering.io/v1/cards/{card_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        card_data = response.json()
        return card_data
    else:
        print(f"Error: Unable to fetch card data for card ID {card_id}. Status code {response.status_code}")
        return None

def load_card_data():
    card_info = get_mt_card(1)
    print(card_info)

# Call the function to load and print card data
load_card_data()