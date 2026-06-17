import streamlit as st

from shuffle_playlist import shuffle_playlist
from split_playlists import update_english_playlist

st.title("Ryan's Spotify Tools")

st.header("Update English Playlist")

if st.button("Update English Playlist"):
    update_english_playlist()
    st.success("English playlist updated!")

st.divider()

st.header("Shuffle Playlist")

playlist_link = st.text_input("Paste Spotify playlist link")

if st.button("Shuffle Playlist"):

    if playlist_link:
        shuffle_playlist(playlist_link)
        st.success("Playlist shuffled!")
    else:
        st.warning("Please paste a playlist link.")
