```python
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


def get_new_releases(
    days=7,
    start_date=None
):

    # Load artists from Google Sheets
    artists = get_artists()

    # Determine date range
    if start_date:

        cutoff_date = start_date
        end_date = start_date + timedelta(days=days)

    else:

        cutoff_date = datetime.now() - timedelta(days=days)
        end_date = datetime.now()

    new_releases = []
    seen_albums = set()

    for artist in artists:

        # Skip bad rows
        if "name" not in artist or "id" not in artist:
            continue

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

                # Only include releases in range
                if cutoff_date <= released <= end_date:

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

            print(
                f"Skipping {artist_name}: {e}"
            )

    # Newest first
    new_releases.sort(
        key=lambda x: x["date"],
        reverse=True
    )

    return new_releases
```
