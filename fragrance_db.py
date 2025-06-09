import json
from fragrance import Fragrance

try:
    with open("fragrances.json", "r") as f:
        data = json.load(f)
    
    fragrance_list = [
        Fragrance(
            item.get("name", "Unknown"),
            item.get("link", ""),
            item.get("notes", []),
            item.get("price", 0),
            item.get("events", []),
            item.get("strength", ""),
            item.get("adjectives", []),
            item.get("gender", "unisex")
        ) for item in data
    ]
    
    print(f"Loaded {len(fragrance_list)} fragrances successfully")
    
except FileNotFoundError:
    print("Warning: fragrances.json file not found. Using empty fragrance list.")
    fragrance_list = []
except json.JSONDecodeError as e:
    print(f"Error parsing fragrances.json: {e}")
    fragrance_list = []
except Exception as e:
    print(f"Unexpected error loading fragrances: {e}")
    fragrance_list = []