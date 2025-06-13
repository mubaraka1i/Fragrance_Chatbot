import random
from fragrance_db import fragrance_list

def ask_user_preferences():
    print("Welcome to the Fragrance Recommender!")

    just_notes = input("Do you want to skip all filtering and just get 5 good-smelling picks? (yes/no): ").strip().lower()

    if just_notes == "yes":
        return {
            "price": "any",
            "event": "any",
            "strength": "any",
            "gender": "any",
            "notes": [],
            "adjectives": [],
            "just_notes": True
        }

    print("\nAnswer the following or press Enter to skip:\n")

    gender = input("Gender preference (feminine / masculine / unisex / any): ").strip().lower() or "any"
    price = input("Price range (low / medium / high / expensive / any): ").strip().lower() or "any"
    event = input("Occasion (office, date, clubbing, daily, school, any): ").strip().lower() or "any"
    strength = input("Scent strength (strong / light / any): ").strip().lower() or "any"

    notes = input("Enter notes you like (comma separated, e.g., vanilla, citrus): ")
    notes = [n.strip().lower() for n in notes.split(",") if n.strip()] if notes else []

    adjectives = input("Describe the vibe (e.g., sweet, fresh, dark): ")
    adjectives = [a.strip().lower() for a in adjectives.split(",") if a.strip()] if adjectives else []

    return {
        "gender": gender,
        "price": price,
        "event": event,
        "strength": strength,
        "notes": notes,
        "adjectives": adjectives,
        "just_notes": False
    }

def recommend_fragrances(fragrance_list, filters, min_match_threshold=5):
    scored_matches = []

    for frag in fragrance_list:
        score = 0

        
        if 'type' in filters and filters['type'] == frag.get('type', '').lower():
            score += 1
        if 'gender' in filters and filters['gender'] == frag.get('gender', '').lower():
            score += 1
        if 'price' in filters and frag.get('price'):
            price = frag['price']
            if filters['price'] == 'low' and price <= 50:
                score += 1
            elif filters['price'] == 'medium' and 51 <= price <= 100:
                score += 1
            elif filters['price'] == 'high' and 101 <= price <= 199:
                score += 1
            elif filters['price'] == 'expensive' and price >= 200:
                score += 1
        if 'occasion' in filters and filters['occasion'] == frag.get('occasion', '').lower():
            score += 1
        if 'strength' in filters and filters['strength'] == frag.get('strength', '').lower():
            score += 1
        if 'note' in filters and filters['note'] != 'any':
            if filters['note'] in [n.lower() for n in frag.get('notes', [])]:
                score += 1
        if 'vibe' in filters and filters['vibe'] != 'any':
            if filters['vibe'] == frag.get('vibe', '').lower():
                score += 1

        if score >= min_match_threshold:
            scored_matches.append((score, frag))

    
    scored_matches.sort(reverse=True, key=lambda x: x[0])
    top_matches = [f for _, f in scored_matches[:3]]

    review_message = {
        "message": "Check out the website below for in-depth reviews on these fragrances!",
        "link": "https://www.fragrantica.com"
    }

    return top_matches, review_message



def main():
    filters = ask_user_preferences()
    results, review_message = recommend_fragrances(fragrance_list, filters)

    if results:
        print("\nRecommended Fragrances:")
        for frag in results:
            print("-", frag)

        print("\n" + review_message["message"])
        print(review_message["link"])






if __name__ == "__main__":
    main()
