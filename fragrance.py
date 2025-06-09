# Updated Fragrance class with proper filtering and error handling
class Fragrance:
    def __init__(self, name, link, notes, price, events, strength, adjectives, gender):
        self.name = name
        self.link = link
        try:
            self.price = float(price) if price else 0
        except (ValueError, TypeError):
            self.price = 0
        
        self.notes = [n.lower().strip() for n in notes] if notes else []
        self.events = [e.lower().strip() for e in events] if events else []
        self.strength = strength.lower().strip() if strength else ""
        self.adjectives = [a.lower().strip() for a in adjectives] if adjectives else []
        self.gender = gender.lower().strip() if gender else ""
    
    def matches(self, filters):
        # Gender filter - handle unisex fragrances properly
        if filters.get("gender") and filters["gender"] != "any":
            if self.gender != filters["gender"] and self.gender != "unisex":
                return False
        
        # Price filter - fixed ranges to match Flask app definitions
        if filters.get("price") and filters["price"] != "any":
            if filters["price"] == "low" and (self.price < 10 or self.price > 50):
                return False
            elif filters["price"] == "medium" and (self.price < 51 or self.price > 100):
                return False
            elif filters["price"] == "high" and (self.price < 101 or self.price > 199):
                return False
            elif filters["price"] == "expensive" and self.price < 200:
                return False
        
        # Event filter
        if filters.get("event") and filters["event"] != "any":
            if filters["event"] not in self.events:
                return False
        
        # Strength filter
        if filters.get("strength") and filters["strength"] != "any":
            if self.strength != filters["strength"]:
                return False
        
        # Notes filter - normalize case for comparison
        if filters.get("notes"):
            filter_notes = [note.lower().strip() for note in filters["notes"] if note.strip()]
            if filter_notes and not any(note in self.notes for note in filter_notes):
                return False
        
        # Adjectives filter - normalize case for comparison
        if filters.get("adjectives"):
            filter_adjectives = [adj.lower().strip() for adj in filters["adjectives"] if adj.strip()]
            if filter_adjectives and not any(adj in self.adjectives for adj in filter_adjectives):
                return False
        
        return True
    
    def __str__(self):
        return f"{self.name} (${self.price})"
    
    def __repr__(self):
        return f"Fragrance(name='{self.name}', price={self.price}, gender='{self.gender}')"