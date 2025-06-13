class Fragrance:
    def __init__(self, name, link, notes, price, events, strength, gender, type_):
        self.name = str(name).strip() if name else "Unknown"
        self.link = str(link).strip() if link else ""

        try:
            self.price = float(price) if price is not None else 0
            if self.price < 0:
                self.price = 0
        except (ValueError, TypeError):
            self.price = 0

        self.notes = self._safe_string_list(notes)
        self.events = self._safe_string_list(events)
        self.type = self._safe_string_list(type_)
        self.strength = str(strength).lower().strip() if strength else ""
        self.gender = str(gender).lower().strip() if gender else "unisex"

    def _safe_string_list(self, items):
        if not items:
            return []
        result = []
        for item in items:
            if item is not None:
                try:
                    result.append(str(item).lower().strip())
                except:
                    continue
        return result

    def matches(self, filters):
        if filters.get("gender") and filters["gender"] != "any":
            if self.gender != filters["gender"] and self.gender != "unisex":
                return False

        if filters.get("min_price") is not None:
            if self.price < filters["min_price"]:
                return False

        if filters.get("max_price") is not None:
            if self.price > filters["max_price"]:
                return False

        event_synonyms = {
            "office": ["work", "business", "formal", "professional", "daily"],
            "night out": ["party", "clubbing", "evening", "bar"],
            "school": ["class", "university", "college"],
            "gym": ["fitness", "exercise", "training"],
        }

        event_key = filters.get("event") or filters.get("occasion")
        if event_key and event_key != "any":
            event_key = event_key.lower().strip()
            allowed_events = [event_key] + event_synonyms.get(event_key, [])
            if not any(e in self.events for e in allowed_events):
                return False

        if filters.get("strength") and filters["strength"] != "any":
            if self.strength != filters["strength"]:
                return False

        note_synonyms = {
            "citrus": ["lime", "orange", "bergamot", "mandarin", "lemon", "grapefruit", "calabrian bergamot", "blood orange"],
            "vanilla": ["bourbon vanilla", "madagascar vanilla"],
            "oud": ["agarwood"],
            "tea": ["green tea", "matcha"],
            "amber": ["ambergris"],
            "leather": ["suede"],
        }

        note_filter = filters.get("note")
        if note_filter:
            if isinstance(note_filter, str):
                note_filter = [note_filter]
            filter_notes = [note.lower().strip() for note in note_filter if note and str(note).strip()]

            expanded_notes = []
            for note in filter_notes:
                expanded_notes.append(note)
                expanded_notes.extend(note_synonyms.get(note, []))

            fragrance_notes = [note.lower().strip() for note in self.notes]
            if expanded_notes and not any(n in fragrance_notes for n in expanded_notes):
                return False

        type_filter = filters.get("type")
        if type_filter:
            if isinstance(type_filter, str):
                type_filter = [type_filter]
            filter_types = [t.lower().strip() for t in type_filter if t and str(t).strip()]
            fragrance_types = [t.lower().strip() for t in self.type]
            if filter_types and not any(t in fragrance_types for t in filter_types):
                return False

        return True

    def __str__(self):
        return f"{self.name} (${self.price})"

    def __repr__(self):
        return f"Fragrance(name='{self.name}', price={self.price}, gender='{self.gender}')"

