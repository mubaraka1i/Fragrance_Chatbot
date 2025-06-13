from flask import Flask, render_template, request, jsonify, session
from fragrance_db import fragrance_list
import random
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "default-fallback-key")

def get_session_value(key, default):
    return session.get(key, default)

@app.route("/")
def home():
    session.clear()
    session["stage"] = "intro"
    session["filters"] = {}
    return render_template("chat.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").strip().lower()
    filters = session.get("filters", {})
    stage = session.get("stage", "intro")

    if user_input == "more" and filters and stage != "post_recommendation":
        already_shown = session.get("already_shown", [])
        recommendations = recommend_with_threshold(fragrance_list, filters)
        new_recommendations = [f for f in recommendations if f.name not in already_shown]

        if not new_recommendations:
            return jsonify(reply=[
                "You've seen all matching fragrances based on your current filters.",
                "Type 'restart' to try new filters or adjust your preferences."
            ])

        selected = random.sample(new_recommendations, min(5, len(new_recommendations)))
        already_shown += [f.name for f in selected]
        session["already_shown"] = already_shown

        return jsonify(reply=[format_recommendations(selected), "Hope one of these fits your vibe! Type 'more' to see more options or 'restart' to try different filters."])

    yes_keywords = ["yes", "yeah", "yep", "sure", "ok", "okay", "definitely", "ye", "yup", "ya", "indeed",
                    "bet", "fo sho", "for sure", "absolutely", "100%", "hell yeah", "hell yes", "yessir",
                    "yess", "yasss", "yass", "si", "oui", "aye", "affirmative", "roger", "copy that",
                    "word", "facts", "true", "real", "valid", "straight up", "no cap", "on god",
                    "obviously", "duh", "of course", "naturally", "totally", "completely", "perfect",
                    "sounds good", "let's go", "i'm down", "down", "let's do it", "why not", "go for it",
                    "yessss", "yeahhh", "yuppp", "sureee", "okayy", "okayyy", "yeppp", "yepp"]

    no_keywords = ["no", "nope", "nah", "na", "naw", "hell no", "hell nah", "no way", "not happening",
                   "absolutely not", "never", "not really", "not at all", "negative", "nada", "zilch",
                   "no thanks", "no thx", "i'm good", "pass", "hard pass", "skip", "next", "nvm",
                   "nevermind", "forget it", "not interested", "not feeling it", "not my vibe",
                   "not for me", "i'll pass", "not gonna happen", "not today", "nuh uh", "no sir", "no ma'am", "not a chance", "over my dead body", "when pigs fly",
                   "nopee", "nahh", "naww", "nooo", "noooo"]

    unsure_keywords = ["maybe", "idk", "not sure", "kinda", "kind of", "sort of", "unsure", "ehh", "somewhat",
                       "i dunno", "dunno", "i don't know", "probably", "possibly", "perhaps", "could be",
                       "might", "might be", "i guess", "i suppose", "i think so", "maybe so", "hmm",
                       "ummm", "umm", "hmmm", "idrk", "i don't really know", "beats me", "who knows",
                       "hard to say", "tough call", "on the fence", "50/50", "flip a coin", "whatever",
                       "doesn't matter", "either way", "both", "either", "neither", "meh", "eh", "shrug",
                       "could go either way", "up in the air", "tbd", "to be determined", "we'll see",
                       "maybeee", "maybee", "idkk", "idkkk", "hmmmmm", "ehhhh", "mehhh"]

    if user_input == "restart":
        session.clear()
        session["stage"] = "restart_check"
        session["filters"] = {}
        return jsonify(reply=["Do you want to find new fragrances with different filters?"])

    if stage == "restart_check":
        if user_input in yes_keywords:

            session["stage"] = "type_check"
            return jsonify(reply=["Great! Let's find you some new options.", "Do you have a type of fragrance in mind?"])
        elif user_input in no_keywords:

            unisex_frags = [frag for frag in fragrance_list if frag.gender == "unisex"]
            random_frags = random.sample(unisex_frags, 3) if len(unisex_frags) >= 3 else unisex_frags
            session.clear()
            return jsonify(reply=["No problem! Here are some unisex fragrances for you to try:",
                                   format_recommendations(random_frags),
                                   "Hope one of these catches your interest! Type 'restart' if you'd like to try again."])
        else:
            return jsonify(reply="I didn't quite catch that. Do you want to find new fragrances with different filters?")

    if stage == "intro":
        session["stage"] = "type_check"
        return jsonify(reply=["Hi, I'm Bebo, your virtual FragranceAI!", "Do you already have a type of fragrance in mind?"])

    elif stage == "type_check":
        if user_input in yes_keywords:

            session["stage"] = "specify_type"
            return jsonify(reply=["Cool! What type are you thinking?", "Choose from: fresh, fruity, woody, spicy, floral, sweet, green, powdery, smoky, musky, gourmand, earthy, aquatic, creamy, herbal, metallic, dark, cozy, bold, airy, warm, mysterious, youthful. (Or type 'any' if you're open to all types.)"])
        elif user_input in no_keywords:

            session["stage"] = "gender"
            return jsonify(reply="No problem! Let's start narrowing it down. Do you prefer a feminine, masculine, or unisex scent?")
        elif user_input in unsure_keywords:

            session["stage"] = "explore_uncertainty"
            return jsonify(reply="No worries. Is there a particular smell or fragrance you've liked before?")
        else:
            return jsonify(reply="I didn't quite catch that. Do you have a fragrance type in mind?")

    elif stage == "explore_uncertainty":
        session["stage"] = "gender"
        return jsonify(reply="Ok, let's build from that. Do you prefer a feminine, masculine, or unisex scent?")

    elif stage == "specify_type":
        valid_types = ["fresh", "fruity", "woody", "spicy", "floral", "sweet", "green", 
                       "powdery", "smoky", "musky", "gourmand", "earthy", "aquatic", 
                       "creamy", "herbal", "metallic", "dark", "cozy", "bold", "airy", 
                       "warm", "mysterious", "youthful", "any"]

        user_type = user_input.lower().strip()
        if user_type not in valid_types:
            return jsonify(reply=["Please choose a valid type before we continue: fresh, fruity, woody, spicy, floral, sweet, green, powdery, smoky, musky, gourmand, earthy, aquatic, creamy, herbal, metallic, dark, cozy, bold, airy, warm, mysterious, youthful. Or type 'any'."])

        filters["type"] = user_type
        session["filters"] = filters
        session["stage"] = "gender"
        return jsonify(reply="Nice choice! Do you prefer a feminine, masculine, or unisex scent?")

    elif stage == "gender":
        gender_map = {"f": "feminine", "m": "masculine", "u": "unisex"}
        if user_input in gender_map:
            filters["gender"] = gender_map[user_input]
        elif user_input in ["feminine", "masculine", "unisex"]:
            filters["gender"] = user_input
        else:
            return jsonify(reply="Please choose one: feminine(f), masculine(m), or unisex(u).")
        session["filters"] = filters
        session["stage"] = "price"
        return jsonify(reply="What's your budget? ($50, $100, $150, $200, $200+, or no budget)")

    elif stage == "price":
        user_input_clean = user_input.replace(" ", "").lower()

        valid_prices = {
            "50": (0, 50),
            "$50": (0, 50),
            "100": (0, 100),
            "$100": (0, 100),
            "150": (0, 150),
            "$150": (0, 150),
            "200": (0, 200),
            "$200": (0, 200),
            "200+": (200, None),
            "$200+": (200, None),
            "no budget": (0, None),
            "nobudget": (0, None),
            "no-budget": (0, None)
        }

        if user_input_clean in valid_prices:
            min_price, max_price = valid_prices[user_input_clean]
            filters["min_price"] = min_price
            filters["max_price"] = max_price
            session["filters"] = filters
            session["stage"] = "event"
            return jsonify(reply="What occasion is it for? (office, night out, daily, school, gym, special occasion, warm weather, cold weather, romantic, or any)")
        else:
            return jsonify(reply="Please enter one of the following: 50, 100, 150, 200, 200+, or no budget.")

    elif stage == "event":
        valid_occasions = ["office", "night out", "daily", "school", "gym", 
                           "special occasion", "warm weather", "cold weather", 
                           "romantic", "any"]

        user_occasion = user_input.lower().strip()
        if user_occasion not in valid_occasions:
            return jsonify(reply=["Please choose one valid occasion from: office, night out, daily, school, gym, special occasion, warm weather, cold weather, romantic, or any."])

        filters["occasion"] = user_occasion
        session["filters"] = filters
        session["stage"] = "strength"
        return jsonify(reply="Do you want it to be strong, light, or either?")

    elif stage == "strength":
        user_input = user_input.lower().strip()
        if user_input in ["either", "any"]:
            filters["strength"] = "any"
        elif user_input in ["strong", "light"]:
            filters["strength"] = user_input
        else:
            return jsonify(reply="Please choose: strong, light, or either")
        session["filters"] = filters
        session["stage"] = "notes"
        return jsonify(reply="Any specific note? (vanilla, citrus, oud, incense, leather, tea, amber, boozy, or skip)")

    elif stage == "notes":
        valid_notes = ["vanilla", "citrus", "oud", "incense", "leather", "tea", "amber", "boozy", "any", "skip"]
        user_input = user_input.lower().strip()

        if user_input not in valid_notes:
            return jsonify(reply=[
                "Please choose a valid note before we continue.",
                "Options: vanilla, citrus, oud, incense, leather, tea, amber, boozy.",
                "Or type 'any' or 'skip' if you're open to all notes."
            ])

        filters["note"] = "any" if user_input in ["any", "skip"] else user_input
        session["filters"] = filters
        recommendations = recommend_with_threshold(fragrance_list, filters)

        if not recommendations:
            session["stage"] = "restart_check"
            return jsonify(reply=[
                "Sorry, no fragrances matched your preferences. Some of the traits you selected may contrast with each other (e.g., light and heavy, fresh and deep), making them unlikely to appear together.",
                "Type 'restart' to search again and try adjusting one of your filters. *TIP* Increasing the price will broaden your search!"
            ])

        session["already_shown"] = [f.name for f in recommendations[:5]]
        session["stage"] = "post_recommendation"
        return jsonify(reply=[
            format_recommendations(recommendations[:5]),
            "Hope one of these fits your vibe! Type 'more' to see more options with the same filter or 'restart' to start over.",
    "Check out the website below for in-depth reviews on these fragrances!",
    '<a href="https://www.fragrantica.com" target="_blank">https://www.fragrantica.com</a>'
        ])

    elif stage == "post_recommendation":
        if user_input == "more" and filters:
            already_shown = session.get("already_shown", [])
            recommendations = recommend_with_threshold(fragrance_list, filters)
            new_recommendations = [f for f in recommendations if f.name not in already_shown]

            if not new_recommendations:
                return jsonify(reply=[
                    "You've seen all matching fragrances based on your current filters.",
                    "Type 'restart' to try new filters or adjust your preferences."
                ])

            selected = random.sample(new_recommendations, min(5, len(new_recommendations)))
            already_shown += [f.name for f in selected]
            session["already_shown"] = already_shown

            return jsonify(reply=[
                format_recommendations(selected),
                "Hope one of these fits your vibe! Type 'more' to see more options or 'restart' to try different filters."
            ])

        elif user_input == "restart":
            session.clear()
            session["stage"] = "restart_check"
            session["filters"] = {}
            return jsonify(reply=["Do you want to find new fragrances with different filters?"])
        else:
            return jsonify(reply="Please type 'more' to see additional options or 'restart' to start over with new filters.")

    return jsonify(reply="Sorry, I didn't understand that. Type 'restart' to start over.")

def recommend_with_threshold(fragrance_list, filters):
    matches = []
    fragrance_filters = {}

    if filters.get("gender") and filters["gender"] != "any":
        fragrance_filters["gender"] = filters["gender"]
    if filters.get("occasion") and filters["occasion"] != "any":
        fragrance_filters["event"] = filters["occasion"]
    if filters.get("strength") and filters["strength"] != "any":
        fragrance_filters["strength"] = filters["strength"]
    if filters.get("note") and filters["note"] != "any":
        fragrance_filters["note"] = filters["note"]
    if filters.get("type") and filters["type"] != "any":
        fragrance_filters["type"] = filters["type"]
    if filters.get("min_price") is not None:
        fragrance_filters["min_price"] = filters["min_price"]
    if filters.get("max_price") is not None:
        fragrance_filters["max_price"] = filters["max_price"]

    for frag in fragrance_list:
        if frag.matches(fragrance_filters):
            matches.append(frag)
    return matches

def format_recommendations(fragrances):
    lines = []
    for frag in fragrances:
        lines.append(f"• {frag.name} (${frag.price})")
        lines.append(f'<a href="{frag.link}" target="_blank">{frag.link}</a>')
        lines.append("")
        lines.append("")
    return "<br>".join(lines)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


    
