import random
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth


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


def public_shuffle():

    CLIENT_ID = st.secrets["SPOTIFY_CLIENT_ID"]
    CLIENT_SECRET = st.secrets["SPOTIFY_CLIENT_SECRET"]

    REDIRECT_URI = "https://spotifytool.streamlit.app"

    SCOPE = (
        "playlist-read-private "
        "playlist-modify-private "
        "playlist-modify-public"
    )

    auth_manager = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE
    )

    # ---------------- LOGIN ----------------
    auth_url = auth_manager.get_authorize_url()

    st.link_button(
        "Login with Spotify",
        auth_url
    )

    params = st.query_params

    if "code" not in params:
        return

    code = params["code"]

    token_info = auth_manager.get_access_token(code)

    sp = spotipy.Spotify(
        auth=token_info["access_token"]
    )

    user = sp.current_user()

    st.success(
        f"Logged in as {user['display_name']}"
    )

    # ---------------- PLAYLIST BOX ----------------
    playlist_link = st.text_input(
        "Spotify Playlist Link",
        key="public_playlist_link"
    )

    if st.button(
        "Shuffle Playlist",
        key="public_shuffle_button"
    ):

        try:

            playlist_id = extract_playlist_id(
                playlist_link
            )

            playlist_info = sp.playlist(
                playlist_id
            )

            original_name = playlist_info["name"]

            new_name = f"{original_name} Shuffled"

            user_id = user["id"]

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

            random.shuffle(track_ids)

            # Replace first 100
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

            st.success(
                f"Created '{new_name}'"
            )

        except Exception as e:

            st.error(e)
