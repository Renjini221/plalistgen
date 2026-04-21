# Playlist Generator

A web app that generates a playlist from a mood, artist, or song name and lets you play the songs directly in the browser.

## Flow: From Clicking Generate to Playing a Song

### 1. User Input
The user types a mood ("sad lofi"), artist ("The Weeknd"), or song name ("Blinding Lights") into the search box and clicks **Generate**.

### 2. Form Submission
The browser sends a POST request to the Flask `/` route with the input as `prompt`.

### 3. Vibe Expansion (AI)
Flask calls `expand_vibe_to_queries(prompt)` which sends the input to the OpenRouter API (GPT-4o-mini). The AI returns 5 specific "Song Title Artist" search queries based on the input.

### 4. Song Fetching
For each of the 5 queries, Flask calls `get_songs(query)` which hits the Saavn API:

It picks the top 2 results per query, giving up to 10 songs total.

### 5. Metadata Fixing
For each song, if the artist is "Unknown" or the name looks generic (too long, all caps, contains words like "hits" or "mix"), Flask calls `fix_metadata(song_name)` which asks the AI to return the correct Title - Artist.

### 6. Deduplication
Songs are deduplicated by `(name, artist)` key so the same song doesn't appear twice.

### 7. Rendering
Flask passes the final song list to `index.html` via Jinja2. Each song card renders with:
- Album art
- Song title and artist
- A play button + progress bar + timer

### 8. Playing a Song
When the user clicks ▶ on a card, the `playSong()` JavaScript function:
1. Pauses all other playing audio
2. Calls `audio.play()` on the `<audio>` element in that card
3. Updates the progress bar in real time via `audio.ontimeupdate`
4. When the song ends, automatically clicks ▶ on the next card

## Other Features
- **Suggestions** — as the user types, the `/suggest` route queries Saavn and shows autocomplete options
- **Download .txt** — exports the playlist as a text file
- **Save Playlist** — saves the current playlist to `localStorage`
- **Load Playlist** — the `/load` page reads saved playlists from `localStorage` and renders them
