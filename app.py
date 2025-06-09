from flask import Flask, render_template, request, jsonify, session
from fragrance_db import fragrance_list
import random

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

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
    

    yes_keywords = ["yes", "yeah", "yep", "sure", "ok", "okay", "definitely", "ye", "y", "yup", "ya", "indeed",
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
           "not for me", "i'll pass", "not gonna happen", "not today", "nuh uh", "nope nope",
           "mm mm", "no sir", "no ma'am", "not a chance", "over my dead body", "when pigs fly",
           "nopee", "nahh", "naww", "nooo", "noooo"
]
    unsure_keywords = ["maybe", "idk", "not sure", "kinda", "kind of", "sort of", "unsure", "ehh", "somewhat",
           "i dunno", "dunno", "i don't know", "probably", "possibly", "perhaps", "could be",
           "might", "might be", "i guess", "i suppose", "i think so", "maybe so", "hmm",
           "ummm", "umm", "hmmm", "idrk", "i don't really know", "beats me", "who knows",
           "hard to say", "tough call", "on the fence", "50/50", "flip a coin", "whatever",
           "doesn't matter", "either way", "both", "either", "neither", "meh", "eh", "shrug",
           "could go either way", "up in the air", "tbd", "to be determined", "we'll see",
           "maybeee", "maybee", "idkk", "idkkk", "hmmmmm", "ehhhh", "mehhh"
]

    if user_input == "restart":
        session.clear()
        session["stage"] = "restart_check"
        session["filters"] = {}
        return jsonify(reply=["Do you want to find new fragrances with different filters?"])

    if stage == "restart_check":
        if any(word in user_input for word in yes_keywords):
            session["stage"] = "type_check"
            return jsonify(reply=[
                "Great! Let's find you some new options.",
                "Do you have a type of fragrance in mind?"
            ])
        elif any(word in user_input for word in no_keywords):
            random_frags = random.sample(fragrance_list, 3)
            session.clear()
            return jsonify(reply=[
                "Here are 3 fragrances for you to try:",
                format_recommendations(random_frags),
                "Hope one of these catches your interest! Type 'restart' if you'd like to try again."
            ])
        else:
            return jsonify(reply="I didn't quite catch that. Do you want to find new fragrances with different filters?")

    if stage == "intro":
        session["stage"] = "type_check"
        return jsonify(reply=[
            "Hi, I'm Bebo, your virtual FragranceAI!",
            "Do you already have a type of fragrance in mind?"
        ])

    elif stage == "type_check":
        if any(word in user_input for word in yes_keywords):
            session["stage"] = "specify_type"
            return jsonify(reply=[
                "Cool! What type are you thinking?",
                "Choose from: fresh, fruity, woody, spicy, floral, sweet, green, powdery, smoky, musky, gourmand, earthy, aquatic, creamy, herbal, metallic, dark, cozy, bold, airy, warm, mysterious, youthful."
            ])
        elif any(word in user_input for word in no_keywords):
            session["stage"] = "gender"
            return jsonify(reply="No problem! Let's start narrowing it down. Do you prefer a feminine, masculine, or unisex scent?")
        elif any(word in user_input for word in unsure_keywords):
            session["stage"] = "explore_uncertainty"
            return jsonify(reply="No worries. Is there a particular smell or fragrance you've liked before?")
        else:
            return jsonify(reply="I didn't quite catch that. Do you have a fragrance type in mind?")

    elif stage == "explore_uncertainty":
        session["stage"] = "gender"
        return jsonify(reply="Thanks! Let's build from that. Do you prefer a feminine, masculine, or unisex scent?")

    elif stage == "specify_type":
        filters["type"] = user_input
        session["filters"] = filters
        session["stage"] = "gender"
        return jsonify(reply="Nice choice! Do you prefer a feminine, masculine, or unisex scent?")

    elif stage == "gender":
        if user_input not in ["feminine", "masculine", "unisex"]:
            return jsonify(reply="Please choose one: feminine, masculine, or unisex.")
        filters["gender"] = user_input
        session["filters"] = filters
        session["stage"] = "price"
        return jsonify(reply="What's your price range? (low = $10–$50, medium = $51–$100, high = $101–$199, expensive = $200+, or any)")

    elif stage == "price":
        if user_input not in ["low", "medium", "high", "expensive", "any"]:
            return jsonify(reply="Please choose: low, medium, high, expensive, or any")
        filters["price"] = user_input
        session["filters"] = filters
        session["stage"] = "event"
        return jsonify(reply="What occasion is it for? (office, night out, daily, school, gym, special occasion, warm weather, cold weather, romantic, or any)")

    elif stage == "event":
        filters["occasion"] = user_input
        session["filters"] = filters
        session["stage"] = "strength"
        return jsonify(reply="Do you want it to be strong or light?")

    elif stage == "strength":
        filters["strength"] = user_input
        session["filters"] = filters
        session["stage"] = "notes"
        return jsonify(reply="Any specific notes? (vanilla, citrus, oud, incense, leather, tea, amber, boozy, any)")

    elif stage == "notes":
        filters["note"] = user_input
        session["filters"] = filters
        recommendations = recommend_with_threshold(fragrance_list, filters)
        session.clear()

        if not recommendations:
            return jsonify(reply=[
                "Sorry, no fragrances matched your preferences. Some of the traits you selected may contrast with each other (e.g., light and heavy, fresh and deep), making them unlikely to appear together in a single scent. Try adjusting one of your filters for better results. Try 'restart' to search again!"
            ])
        return jsonify(reply=[
            format_recommendations(recommendations),
            "Hope one of these fits your vibe! Type 'restart' if you'd like to try again."
        ])



    return jsonify(reply="Sorry, I didn't understand that. Type 'restart' to start over.")

def recommend_with_threshold(fragrance_list, filters):
    matches = []
    fragrance_filters = {}

    if filters.get("gender") and filters["gender"] != "any":
        fragrance_filters["gender"] = filters["gender"]
    if filters.get("price") and filters["price"] != "any":
        fragrance_filters["price"] = filters["price"]
    if filters.get("occasion") and filters["occasion"] != "any":
        fragrance_filters["event"] = filters["occasion"]
    if filters.get("strength") and filters["strength"] != "any":
        fragrance_filters["strength"] = filters["strength"]
    if filters.get("note") and filters["note"] != "any":
        fragrance_filters["notes"] = [filters["note"]]
    if filters.get("vibe") and filters["vibe"] != "any":
        fragrance_filters["adjectives"] = [filters["vibe"]]

    for frag in fragrance_list:
        if frag.matches(fragrance_filters):
            matches.append(frag)

    return matches[:3]

def format_recommendations(fragrances):
    lines = []
    for frag in fragrances:
        lines.append(f"• {frag.name} (${frag.price})")
        lines.append(f'<a href="{frag.link}" target="_blank">{frag.link}</a>')
        lines.append("")  
        lines.append("")  
    return "<br>".join(lines)


if __name__ == "__main__":
    app.run(debug=True, port=502)

