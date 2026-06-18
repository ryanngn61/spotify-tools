import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


CLIENT_ID = st.secrets["SPOTIFY_CLIENT_ID"]
CLIENT_SECRET = st.secrets["SPOTIFY_CLIENT_SECRET"]

spotify = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )
)


def extract_artist_id(link):

    # Remove query parameters
    link = link.split("?")[0]

    return link.rstrip("/").split("/")[-1]


def get_artist_info(artist_id):

    artist = spotify.artist(artist_id)

    image = None

    if artist["images"]:
        image = artist["images"][0]["url"]

    return {
        "name": artist["name"],
        "id": artist["id"],
        "image": image
    }


def get_artist_from_link(link):

    artist_id = extract_artist_id(link)

    return get_artist_info(artist_id)
