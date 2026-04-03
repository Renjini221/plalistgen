from flask import Flask,render_template,request
import requests
app = Flask(__name__)

def fix_metadata(song_name):
    url="https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": "Bearer Apikey",
        "Content-Type": "application/json"
    }
    prompt = f"""
    Give me  correct song title and artist for this:{song_name}
    Format strictly:title - Artist
    No extra text
    """

    data = {
    "model":"openai/gpt-3.5-turbo",
    "messages": [{"role":"user","content":prompt}]
    }
    try:
        res=requests.post(url,headers=headers,json=data).json()
        output = res["choices"][0]["message"]["content"]
        if "-" in output:
           title, artist = output.split("-", 1)
           return title.strip(), artist.strip()
    except:
         pass
    return song_name,"unknown"


def get_songs(query):
    url = f"https://saavn.sumit.co/api/search/songs?query={query}"
    try:
        res = requests.get(url).json()
    except:
        return[]
    songs = []

    results = res.get("data",{}).get("results",[])
    for item in results[:10]:
        audio_list = item.get("downloadUrl",[])
        img_list = item.get("image",[])

        name = item.get("name","")
        artist = item.get("primaryArtists") or "Unknown"

        clean_name = name.split("(")[0].strip()
        
        if artist == "Unknown" or len(name) > 40:
            new_name,new_artist = fix_metadata(clean_name)

        songs.append({
            "name":new_name,
            "artist": new_artist,
            "audio":audio_list[-1]["url"]if audio_list else "",
            "img":img_list[-1]["url"] if img_list else ""
        })    


    return songs
    
@app.route("/",methods=["GET","POST"])
def index():
        songs = []

        if request.method == "POST":
            prompt = request.form.get("prompt")

            if prompt:
                songs=get_songs(prompt)

        return render_template("index.html",songs=songs)
if __name__=="__main__":
   app.run(debug=True)  
