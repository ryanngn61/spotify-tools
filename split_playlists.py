import random
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import streamlit as st

CLIENT_ID = st.secrets["SPOTIFY_CLIENT_ID"]
CLIENT_SECRET = st.secrets["SPOTIFY_CLIENT_SECRET"]

REDIRECT_URI = "https://127.0.0.1:8888/callback/"

# ======================

# PLAYLIST IDS

# ======================

ALL_PLAYLIST_ID = "3FADEfuEpHzQZ0W1YQswAd"
KPOP_PLAYLIST_ID = "5PmLL2PgjdokVs1YxJpNBs"
ENGLISH_PLAYLIST_ID = "3BIYwp2n5EBtoQT0BpsOn9"

# ======================

# ARTISTS TO KEEP

# ======================

KEEP_ARTIST_IDS = {
"2EoyTW14yqnbqmk90NjbLT",  # PRYVT
"6dhfy4ByARPJdPtMyrUYJK",  # Yerin Baek
"3eVa5w3URK5duf6eyVDbu9",  # ROSÉ
}

# ======================

# GET FRESH SPOTIFY CLIENT

# ======================

def get_spotify_client():

auth_manager = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=(
        "playlist-read-private "
        "playlist-modify-private "
        "playlist-modify-public"
    )
)

token_info = auth_manager.refresh_access_token(
    st.secrets["SPOTIFY_REFRESH_TOKEN"]
)

return spotipy.Spotify(
    auth=token_info["access_token"]
)


def get_all_tracks(playlist_id, sp):

tracks = []

results = sp.playlist_items(
    playlist_id,
    limit=100,
    additional_types=["track"]
)

while True:

    tracks.extend(results["items"])

    if results["next"]:
        results = sp.next(results)
    else:
        break

return tracks

def update_english_playlist():

# Fresh token every run
sp = get_spotify_client()

print("Loading playlists...")

all_music = get_all_tracks(
    ALL_PLAYLIST_ID,
    sp
)

kpop_music = get_all_tracks(
    KPOP_PLAYLIST_ID,
    sp
)

print(f"All Music songs: {len(all_music)}")
print(f"K-pop songs: {len(kpop_music)}")

kpop_track_ids = set()

for item in kpop_music:

    track = item["track"]

    if track and track["id"]:
        kpop_track_ids.add(track["id"])

english_track_ids = []
seen = set()

print("Building English playlist...")

for item in all_music:

    track = item["track"]

    if not track or not track["id"]:
        continue

    track_id = track["id"]

    if track_id in seen:
        continue

    keep_song = False

    for artist in track["artists"]:

        if artist["id"] in KEEP_ARTIST_IDS:
            keep_song = True
            break

    if track_id in kpop_track_ids and not keep_song:
        continue

    english_track_ids.append(track_id)
    seen.add(track_id)

print(f"English playlist size: {len(english_track_ids)}")

print("Shuffling playlist...")
random.shuffle(english_track_ids)

print("Updating playlist...")

sp.playlist_replace_items(
    ENGLISH_PLAYLIST_ID,
    english_track_ids[:100]
)

for i in range(100, len(english_track_ids), 100):

    sp.playlist_add_items(
        ENGLISH_PLAYLIST_ID,
        english_track_ids[i:i + 100]
    )

print("Done!")

if **name** == "**main**":
update_english_playlist()
