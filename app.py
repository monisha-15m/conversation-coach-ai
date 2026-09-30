import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-3.6-flash"

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not configured in the environment.")

client = genai.Client(api_key=API_KEY)

try:
    from chatbot_config import SYSTEM_PROMPT
except ImportError:
    SYSTEM_PROMPT = """
You are AstroBot, a focused educational space-information chatbot.
Answer only questions directly related to astronomy, space science,
space exploration, planets, stars, galaxies, cosmology, spacecraft,
satellites, rockets, astronauts, missions, telescopes, and related
scientific concepts.

If a question is unrelated to space or study, politely say that AstroBot
is designed only for educational space and astronomy questions and ask
the user to ask a space-related question instead.

Keep answers accurate, clear, educational, and easy to understand.
Do not pretend to know uncertain facts. If information may have changed,
state the limitation rather than inventing details.
"""

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()

    if not message:
        return jsonify({"reply": "Please enter a question."}), 400

    try:
        prompt = f"{SYSTEM_PROMPT}\n\nUser question:\n{message}"

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        reply = response.text or "I couldn't generate a response. Please try another space-related question."
        return jsonify({"reply": reply})

    except Exception as error:
        app.logger.exception("Gemini API error: %s", error)
        return jsonify({
            "reply": "I'm having trouble connecting right now. Please try again in a moment."
        }), 500


if __name__ == "__main__":
    app.run()
