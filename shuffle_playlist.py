import random
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# ======================
# SPOTIFY APP SETTINGS
# ======================
CLIENT_ID = "e0781282454f4400b5e3cd5e954541f0"
CLIENT_SECRET = "294807a855d941569fc205fa1dcc9b41"
REDIRECT_URI = "https://127.0.0.1:8888/callback/"

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope="playlist-read-private playlist-modify-private playlist-modify-public"
    )
)


def get_all_tracks(playlist_id):
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


def extract_playlist_id(link):
    link = link.split("?")[0]
    return link.split("/")[-1]


# ======================
# ASK FOR PLAYLIST
# ======================
playlist_link = input("Paste playlist link: ").strip()

playlist_id = extract_playlist_id(playlist_link)

playlist_info = sp.playlist(playlist_id)
original_name = playlist_info["name"]

new_name = f"{original_name} Shuffled"

print(f"Original playlist: {original_name}")
print(f"Shuffled playlist: {new_name}")

# ======================
# FIND EXISTING SHUFFLED PLAYLIST
# ======================
user_id = sp.current_user()["id"]

existing_playlist_id = None

results = sp.current_user_playlists(limit=50)

while True:

    for playlist in results["items"]:
        if playlist["name"] == new_name:
            existing_playlist_id = playlist["id"]
            break

    if existing_playlist_id:
        break

    if results["next"]:
        results = sp.next(results)
    else:
        break

# Create playlist if it doesn't exist
if existing_playlist_id is None:

    playlist = sp.user_playlist_create(
        user=user_id,
        name=new_name,
        public=False
    )

    existing_playlist_id = playlist["id"]

    print("Created new shuffled playlist.")

else:
    print("Using existing shuffled playlist.")

# ======================
# LOAD SONGS
# ======================
tracks = get_all_tracks(playlist_id)

track_ids = []

for item in tracks:
    track = item["track"]

    if track and track["id"]:
        track_ids.append(track["id"])

print(f"Songs found: {len(track_ids)}")

# Shuffle
random.shuffle(track_ids)

# ======================
# CLEAR OLD PLAYLIST
# ======================
sp.playlist_replace_items(existing_playlist_id, [])

# ======================
# ADD SONGS
# ======================
sp.playlist_add_items(
    existing_playlist_id,
    track_ids[:100]
)

for i in range(100, len(track_ids), 100):
    sp.playlist_add_items(
        existing_playlist_id,
        track_ids[i:i + 100]
    )

print("Done!")

