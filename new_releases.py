from datetime import datetime, timedelta

import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from sheet_utils import get_artists


# ======================
# SPOTIFY LOGIN
# ======================
CLIENT_ID = st.secrets["SPOTIFY_CLIENT_ID"]
CLIENT_SECRET = st.secrets["SPOTIFY_CLIENT_SECRET"]

spotify = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )
)


def get_new_releases():

    # Load artists from Google Sheets
    artists = get_artists()

    # Look back 14 days
    cutoff_date = datetime.now() - timedelta(days=14)

    new_releases = []
    seen_albums = set()

    for artist in artists:

        artist_name = artist["name"]
        artist_id = artist["id"]

        try:

            albums = spotify.artist_albums(
                artist_id,
                album_type="album,single",
                limit=50
            )

            for album in albums["items"]:

                # Skip duplicates
                if album["id"] in seen_albums:
                    continue

                seen_albums.add(album["id"])

                release_date = album["release_date"]

                # Handle Spotify date formats
                try:
                    released = datetime.strptime(
                        release_date,
                        "%Y-%m-%d"
                    )

                except:
                    try:
                        released = datetime.strptime(
                            release_date,
                            "%Y-%m"
                        )

                    except:
                        released = datetime.strptime(
                            release_date,
                            "%Y"
                        )

                # Only include recent releases
                if released >= cutoff_date:

                    image_url = None

                    if album["images"]:
                        image_url = album["images"][0]["url"]

                    spotify_url = album["external_urls"]["spotify"]

                    new_releases.append({
                        "artist": artist_name,
                        "album": album["name"],
                        "date": release_date,
                        "image": image_url,
                        "url": spotify_url
                    })

        except Exception as e:
            print(f"Skipping {artist_name}: {e}")

    # Sort newest first
    new_releases.sort(
        key=lambda x: x["date"],
        reverse=True
    )

    return new_releases
