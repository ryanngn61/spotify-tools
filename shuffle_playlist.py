import random
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import streamlit as st


CLIENT_ID = st.secrets["SPOTIFY_CLIENT_ID"]
CLIENT_SECRET = st.secrets["SPOTIFY_CLIENT_SECRET"]
REDIRECT_URI = "https://127.0.0.1:8888/callback/"


# ======================================================
# AUTH
# ======================================================
auth_manager = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope="playlist-read-private playlist-modify-private playlist-modify-public"
)


def get_sp():

    token_info = auth_manager.refresh_access_token(
        st.secrets["SPOTIFY_REFRESH_TOKEN"]
    )

    return spotipy.Spotify(
        auth=token_info["access_token"]
    )


# ======================================================
# GET ALL TRACKS
# ======================================================
def get_all_tracks(sp, playlist_id):

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


# ======================================================
# EXTRACT PLAYLIST ID
# ======================================================
def extract_playlist_id(link):

    link = link.split("?")[0]

    return link.split("/")[-1]


# ======================================================
# SHUFFLE PLAYLIST
# ======================================================
def shuffle_playlist(playlist_link):

    # Get fresh token every run
    sp = get_sp()

    playlist_id = extract_playlist_id(
        playlist_link
    )

    playlist_info = sp.playlist(
        playlist_id
    )

    original_name = playlist_info["name"]

    new_name = f"{original_name} Shuffled"

    print(f"Original playlist: {original_name}")
    print(f"Shuffled playlist: {new_name}")

    user_id = sp.current_user()["id"]

    existing_playlist_id = None

    results = sp.current_user_playlists(
        limit=50
    )

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

    # Create playlist if needed
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

    # Get tracks
    tracks = get_all_tracks(
        sp,
        playlist_id
    )

    track_ids = []

    for item in tracks:

        track = item["track"]

        if track and track["id"]:

            track_ids.append(
                track["id"]
            )

    print(f"Songs found: {len(track_ids)}")

    random.shuffle(
        track_ids
    )

    # Replace first 100 songs
    sp.playlist_replace_items(
        existing_playlist_id,
        track_ids[:100]
    )

    # Add remaining songs
    for i in range(100, len(track_ids), 100):

        sp.playlist_add_items(
            existing_playlist_id,
            track_ids[i:i + 100]
        )

    print("Done!")


# ======================================================
# LOCAL TESTING
# ======================================================
if __name__ == "__main__":

    playlist_link = input(
        "Paste playlist link: "
    ).strip()

    shuffle_playlist(
        playlist_link
    )
