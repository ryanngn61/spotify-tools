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
    scope=(
        "playlist-read-private "
        "playlist-modify-private "
        "playlist-modify-public"
    )
)


def get_sp():

    token_info = auth_manager.refresh_access_token(
        st.secrets["SPOTIFY_REFRESH_TOKEN"]
    )

    return spotipy.Spotify(
        auth=token_info["access_token"]
    )


# ======================================================
# HELPERS
# ======================================================

def extract_playlist_id(link):

    link = link.split("?")[0]

    return link.split("/")[-1]


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
# CREATE OR UPDATE PLAYLIST
# ======================================================

def update_playlist(
    sp,
    user_id,
    playlist_name,
    track_ids
):

    playlist_id = None

    results = sp.current_user_playlists(
        limit=50
    )

    while True:

        for playlist in results["items"]:

            if playlist["name"] == playlist_name:

                playlist_id = playlist["id"]
                break

        if playlist_id:
            break

        if results["next"]:
            results = sp.next(results)
        else:
            break

    if playlist_id is None:

        playlist = sp.user_playlist_create(
            user=user_id,
            name=playlist_name,
            public=False
        )

        playlist_id = playlist["id"]

        print(f"Created playlist: {playlist_name}")

    if len(track_ids) == 0:

        sp.playlist_replace_items(
            playlist_id,
            []
        )

        return

    sp.playlist_replace_items(
        playlist_id,
        track_ids[:100]
    )

    for i in range(100, len(track_ids), 100):

        sp.playlist_add_items(
            playlist_id,
            track_ids[i:i + 100]
        )


# ======================================================
# PLAYLIST SPLITTER
# ======================================================

def split_playlist(
    playlist_a_link,
    playlist_b_link
):

    sp = get_sp()

    playlist_a_id = extract_playlist_id(
        playlist_a_link
    )

    playlist_b_id = extract_playlist_id(
        playlist_b_link
    )

    playlist_a_info = sp.playlist(
        playlist_a_id
    )

    output_name = (
        f"{playlist_a_info['name']} Split"
    )

    print(f"Creating: {output_name}")

    user_id = sp.current_user()["id"]

    playlist_a = get_all_tracks(
        sp,
        playlist_a_id
    )

    playlist_b = get_all_tracks(
        sp,
        playlist_b_id
    )

    print(f"Playlist A: {len(playlist_a)} songs")
    print(f"Playlist B: {len(playlist_b)} songs")

    # -------------------------
    # Build Playlist B lookup
    # -------------------------

    playlist_b_ids = set()

    for item in playlist_b:

        track = item["track"]

        if track and track["id"]:

            playlist_b_ids.add(
                track["id"]
            )

    # -------------------------
    # Build output playlist
    # -------------------------

    output_track_ids = []

    seen = set()

    removed_count = 0
    duplicate_count = 0

    for item in playlist_a:

        track = item["track"]

        if not track or not track["id"]:
            continue

        track_id = track["id"]

        # Remove duplicates in Playlist A

        if track_id in seen:

            duplicate_count += 1
            continue

        seen.add(track_id)

        # Remove songs that exist in Playlist B

        if track_id in playlist_b_ids:

            removed_count += 1
            continue

        output_track_ids.append(
            track_id
        )

    print(f"Removed from Playlist B: {removed_count}")
    print(f"Duplicate songs removed: {duplicate_count}")
    print(f"Final playlist size: {len(output_track_ids)}")

    random.shuffle(
        output_track_ids
    )

    update_playlist(
        sp,
        user_id,
        output_name,
        output_track_ids
    )

    print("Done!")
