from flask import Flask, render_template, request
import requests

app = Flask(__name__)

def get_songs(query):
    url = f"https://saavn.sumit.co/api/search/songs?query={query}"

    try:
        res = requests.get(url).json()
    except:
        return []

    songs = []

    # ✅ correct path
    results = res.get("data", {}).get("results", [])

    for item in results[:10]:
        songs.append({
            "name": item.get("name"),
           "artist": item.get("primaryArtists") or "Unknown Artist",
            "audio": item.get("downloadUrl")[-1]["url"],
            "img": item.get("image")[-1]["url"]
        })

    return songs


@app.route("/", methods=["GET", "POST"])
def index():
    songs = []

    if request.method == "POST":
        prompt = request.form.get("prompt")

        if prompt:
            songs = get_songs(prompt)

    return render_template("index.html", songs=songs)


if __name__ == "__main__":
    app.run(debug=True)