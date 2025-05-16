# Version 5.0

from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_mail import Mail, Message
import json
import random
import os
from datetime import timedelta


app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = "the_improv_cooperative"
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=365)

# Flask-Mail Configuration
app.config["MAIL_SERVER"] = "smtp.gmail.com"  # Replace with your email provider's SMTP server
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "jigappfeedback@gmail.com"  # Replace with your email
app.config["MAIL_PASSWORD"] = "wxxb yhjl hbqy rlml"  # App password
app.config["MAIL_DEFAULT_SENDER"] = "jigappfeedback@gmail.com"  # Replace with your email
mail = Mail(app)



def openSuggestionsFile(category):
    suggestions_file_path = os.path.join(os.path.dirname(__file__), "suggestions", f"{category}.json")

    with open(suggestions_file_path) as suggestions_file:
        data = json.load(suggestions_file)
        suggestions = data.get("family", [])
        flagged = data.get("flagged", [])

    return suggestions, flagged

def get_suggestions(category):
    suggestions, flagged = openSuggestionsFile(category)
    hidden = session.get("hidden", [])

    familyFriendly = session.get("familyFriendly", False)
    if familyFriendly:
        filtered_list = [s for s in suggestions if s not in hidden]
    else:
        filtered_list = [s for s in suggestions + flagged if s not in hidden]

    return filtered_list


list = []
category = None

def newSuggestion(list):
    currentSuggestion = session.get("currentSuggestion", None)
    newSuggestion = random.choice(list)
        
    while currentSuggestion == newSuggestion:
        newSuggestion = random.choice(list)

    # Update the session with the new suggestion
    session["currentSuggestion"] = newSuggestion

    return newSuggestion

@app.route("/")
def index():
    category = "oneword"  # Default category
    session["category"] = category

    familyFriendly = session.get("familyFriendly", False)

    suggestion = "tap to generate"

    return render_template("index.html", familyFriendly=familyFriendly, category=category, suggestion=suggestion)

@app.route("/category/<category>", methods=["GET", "POST"])
def category_page(category):
    # Save the category in the session
    session["category"] = category

    # Get suggestions for the category
    suggestions = get_suggestions(category)
    if not suggestions:
        return "Invalid category", 400

    # Generate a random suggestion
    suggestion = newSuggestion(suggestions)

    # Return the suggestion as plain text for POST requests
    if request.method == "POST":
        return suggestion, 200, {"Content-Type": "text/plain"}

    # Render the template with the category and suggestion
    return render_template("index.html", category=category, suggestion=suggestion)
        
@app.route("/new", methods=["POST"])
def new():
   
    # Check if a category is set in the session
    category = session.get("category", "oneword")

    suggestions = get_suggestions(category)
    if not suggestions:
        return "Invalid category", 400

    suggestion = newSuggestion(suggestions)
    return suggestion, 200, {"Content-Type": "text/plain"}

@app.route("/toggle-family-friendly", methods=["POST"])
def toggle_family_friendly():
    data = request.get_json()
    session['familyFriendly'] = data.get("familyFriendly", False)
    print(f"Family-friendly filter set to: {session['familyFriendly']}") 
    return jsonify(success=True)

@app.route("/hide_suggestion", methods=["POST"])
def hide_suggestion():
    data = request.get_json()
    suggestion = data.get("suggestion")
    hidden = session.get("hidden", [])

    hidden.append(suggestion)

    return jsonify(success=True, hidden=hidden)

@app.route("/hidden", methods=["GET"])
def get_hidden_suggestions():
    hidden = session.get("hidden", [])
    return jsonify(hidden=hidden)

@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    if request.method == "POST":
        # Get the feedback from the form
        feedback_name = request.form.get("name")
        feedback_text = request.form.get("feedback")
        if feedback_name == "":
            feedback_name = "Secret person"

        # Send the feedback via email
        try:
            msg = Message("New Feedback Received", recipients=["jo.osborne23@gmail.com"])
            msg.body = f"Feedback: {feedback_text}\nFrom: {feedback_name}"
            mail.send(msg)
            return render_template("thank_you.html")  # Redirect to a thank-you page
        except Exception as e:
            print(f"Error sending email: {e}")
            return "An error occurred while sending your feedback. Please try again later.", 500

    # Render the feedback form
    return render_template("feedback.html")


if __name__ == "__main__":
    app.run(debug=True, use_reloader=True, host="0.0.0.0", port=5001)
