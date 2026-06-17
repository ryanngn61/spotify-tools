import streamlit as st

from shuffle_playlist import shuffle_playlist
from split_playlists import update_english_playlist

st.title("Ryan's Spotify Tools")

# ==========================
# ENGLISH PLAYLIST BUTTON
# ==========================
st.header("Update English Playlist")

if st.button("Update English Playlist"):

    st.write("Button clicked")
    st.write("About to update playlist...")

    update_english_playlist()

    st.write("Returned from update_english_playlist()")
    st.success("English playlist updated!")

st.divider()

# ==========================
# SHUFFLE PLAYLIST BUTTON
# ==========================
st.header("Shuffle Playlist")

playlist_link = st.text_input("Paste Spotify playlist link")

if st.button("Shuffle Playlist"):

    st.write("Button clicked")

    if playlist_link:

        st.write("About to call shuffle_playlist()")

        shuffle_playlist(playlist_link)

        st.write("Returned from shuffle_playlist()")
        st.success("Playlist shuffled!")

    else:
        st.warning("Please paste a playlist link.")
