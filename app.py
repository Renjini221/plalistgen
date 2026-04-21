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

def fix_metadata(song_name):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY')}",
        "Content-Type": "application/json"
    }
    prompt = f"""
    Give me correct song title and artist for this: {song_name}
    Format strictly: Title - Artist
    No extra text
    """
    data = {
        "model": "google/gemini-flash-1.5",
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        res = requests.post(url, headers=headers, json=data).json()
        output = res["choices"][0]["message"]["content"]
        if "-" in output:
            title, artist = output.split("-", 1)
            return title.strip(), artist.strip()
    except:
        pass
    return song_name, "Unknown"

def get_songs(query):
    url = f"https://saavn.sumit.co/api/search/songs?query={query}"
    try:
        res = requests.get(url).json()
    except:
        return []
    songs = []
    results = res.get("data", {}).get("results", [])
    for item in results[:2]:
        audio_list = item.get("downloadUrl", [])
        img_list = item.get("image", [])
        name = item.get("name", "")
        artist = item.get("primaryArtists") or "Unknown"
        clean_name = name.split("(")[0].strip()
        if artist == "Unknown" or len(name) > 40:
            new_name, new_artist = fix_metadata(clean_name)
        else:
            new_name, new_artist = name, artist
        if not new_name or new_name.lower() in ["title","unknown",""]:
            continue    
        songs.append({
            "name": new_name,
            "artist": new_artist,
            "audio": audio_list[-1]["url"] if audio_list else "",
            "img": img_list[-1]["url"] if img_list else ""
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
    url = f"https://saavn.sumit.co/api/search/songs?query={q}"
    try:
        res = requests.get(url).json()
        results = res.get("data", {}).get("results", [])
        suggestions = []
        for item in results[:5]:
            name = item.get("name", "")
            artist = item.get("primaryArtists") or ""
            suggestions.append(f"{name} - {artist}")
        return jsonify(suggestions)
    except:
        return jsonify([])

@app.route("/load")
def load():
    return render_template("load.html")

application = app
