import json
from fragrance import Fragrance

def flatten(data):
    if isinstance(data, list):
        result = []
        for item in data:
            result.extend(flatten(item))
        return result
    elif isinstance(data, dict):
        return [data]
    else:
        return []

try:
    with open("fragrances.json", "r") as f:
        data = json.load(f)

    flattened_data = flatten(data)

    fragrance_list = []

    for item in flattened_data:
        fragrance_list.append(Fragrance(
            item.get("name", "Unknown"),
            item.get("link", ""),
            item.get("notes", []),
            item.get("price", 0),
            item.get("events", []),
            item.get("strength", ""),
            item.get("gender", "unisex"),
            item.get("type", [])
        ))

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
