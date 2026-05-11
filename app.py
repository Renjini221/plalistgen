from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

def expand_vibe_to_queries(vibe):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY')}",
        "Content-Type": "application/json"
    }
    prompt = f"""You are a music expert. The user typed: "{vibe}"
Return exactly 5 real, well-known song search queries based on this.
Format: "Song Title Artist Name", one per line. No numbering, no extra text."""
    data = {"model": "openai/gpt-3.5-turbo", "messages": [{"role": "user", "content": prompt}]}
    try:
        res = requests.post(url, headers=headers, json=data).json()
        queries = [l.strip() for l in res["choices"][0]["message"]["content"].strip().split("\n") if l.strip()]
        return queries[:5]
    except:
        return [vibe]

def get_songs(query):
    url = f"https://itunes.apple.com/search?term={query}&media=music&limit=2"
    try:
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()
    except:
        return []

    songs = []
    for item in data.get("results", []):
        name = item.get("trackName", "")
        artist = item.get("artistName", "Unknown")
        audio = item.get("previewUrl", "")
        img = item.get("artworkUrl100", "")
        if not name or not audio:
            continue
        songs.append({
            "name": name,
            "artist": artist,
            "audio": audio,
            "img": img
        })
    return songs

@app.route("/", methods=["GET", "POST"])
def index():
    songs = []
    if request.method == "POST":
        prompt = request.form.get("prompt")
        if prompt:
            queries = expand_vibe_to_queries(prompt)
            seen = set()
            for q in queries:
                for s in get_songs(q):
                    key = (s["name"].lower(), s["artist"].lower())
                    if key not in seen:
                        seen.add(key)
                        songs.append(s)
    return render_template("index.html", songs=songs)

@app.route("/suggest")
def suggest():
    q = request.args.get("q", "")
    url = f"https://itunes.apple.com/search?term={q}&media=music&limit=5"
    try:
        res = requests.get(url).json()
        results = res.get("results", [])
        suggestions = []
        for item in results:
            name = item.get("trackName", "")
            artist = item.get("artistName", "")
            suggestions.append(f"{name} - {artist}")
        return jsonify(suggestions)
    except:
        return jsonify([])

@app.route("/load")
def load():
    return render_template("load.html")

application = app
