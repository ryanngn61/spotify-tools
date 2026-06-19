import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth


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

    auth_url = auth_manager.get_authorize_url()

    st.link_button(
        "Login with Spotify",
        auth_url
    )

    params = st.query_params

    if "code" in params:

        code = params["code"]

        token_info = auth_manager.get_access_token(code)

        sp = spotipy.Spotify(
            auth=token_info["access_token"]
        )

        user = sp.current_user()

        st.success(
            f"Logged in as {user['display_name']}"
        )
