import streamlit as st
import test_sheet


from new_releases import get_new_releases
from shuffle_playlist import shuffle_playlist
from split_playlists import update_english_playlist

st.title("Ryan's Spotify Tools")

st.divider()

st.header("🎵 New Releases")

if st.button("Check New Releases"):

    releases = get_new_releases()

    if not releases:

        st.info("No new releases in the last 14 days.")

    else:

        for release in releases:

            col1, col2 = st.columns([1, 3])
        
            with col1:
                if release["image"]:
                    st.image(release["image"], width=150)
        
            with col2:
                st.subheader(release["album"])
                st.write(f"🎤 {release['artist']}")
                st.write(f"📅 Released: {release['date']}")
                st.link_button(
                    "Open in Spotify",
                    release["url"]
                )
        
            st.divider()
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
