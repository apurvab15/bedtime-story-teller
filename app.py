"""Flask web server for the bedtime story generator."""

import os

from flask import Flask, jsonify, render_template, request

from pipeline import build_story_request, generate_story_with_judge

app = Flask(
    __name__,
    template_folder="web/templates",
    static_folder="web/static",
)


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/api/generate")
def api_generate():
    data = request.get_json(silent=True) or {}

    objects = [
        str(data.get("object1", "")).strip(),
        str(data.get("object2", "")).strip(),
        str(data.get("object3", "")).strip(),
    ]
    if not all(objects):
        return jsonify({"error": "Please provide all three objects of interest."}), 400

    try:
        age = int(data.get("age", 7))
    except (TypeError, ValueError):
        return jsonify({"error": "Age must be a number."}), 400

    if age < 5 or age > 10:
        return jsonify({"error": "Age must be between 5 and 10."}), 400

    length = str(data.get("length", "medium")).lower()
    if length not in ("short", "medium", "long"):
        length = "medium"

    user_request = build_story_request(objects, age, length)
    result = generate_story_with_judge(user_request, age=age, length=length)

    return jsonify(result)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() in ("1", "true", "yes")
    app.run(host="0.0.0.0", port=port, debug=debug)
