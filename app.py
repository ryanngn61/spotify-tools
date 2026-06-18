import streamlit as st
from new_releases import get_new_releases
from shuffle_playlist import shuffle_playlist
from split_playlists import update_english_playlist

from sheet_utils import (
    get_artists,
    add_artist,
    remove_artist
)

from spotify_utils import (
    get_artist_from_link,
    get_artist_info
)


st.title("🎵 Ryan's Spotify Tools")


# ===================================================
# ARTIST RELEASE TRACKER
# ===================================================
st.header("🎵 Artist Release Tracker")


# -------------------
# ADD ARTIST
# -------------------
st.subheader("➕ Add Artist")

col1, col2 = st.columns([6, 1])

with col1:
    artist_link = st.text_input(
        "Spotify Artist Link",
        label_visibility="collapsed",
        placeholder="Paste Spotify artist link..."
    )

with col2:
    add_pressed = st.button("Add")

if add_pressed:

    try:

        artist = get_artist_from_link(
            artist_link
        )

        success = add_artist(
            artist["name"],
            artist["id"]
        )

        if success:

            st.success(
                f"Added {artist['name']}"
            )

            st.rerun()

        else:

            st.warning(
                "Artist already exists"
            )

    except Exception as e:

        st.error(e)


# ===================================================
# WATCHLIST
# ===================================================
artists = get_artists()

with st.expander(
    f"🎧 Release Watchlist ({len(artists)} artists)"
):

    for i in range(0, len(artists), 2):

        row_cols = st.columns(2)

        for j in range(2):

            if i + j >= len(artists):
                break

            artist = artists[i + j]

            with row_cols[j]:

                try:

                    info = get_artist_info(
                        artist["id"]
                    )

                except:

                    st.warning(
                        f"Couldn't load {artist['name']}"
                    )

                    continue

                col1, col2, col3 = st.columns(
                    [1, 3, 1]
                )

                with col1:

                    if info["image"]:

                        st.image(
                            info["image"],
                            width=70
                        )

                with col2:

                    st.write(
                        f"**{info['name']}**"
                    )

                with col3:

                    if st.button(
                        "❌",
                        key=f"delete_{artist['id']}"
                    ):

                        remove_artist(
                            artist["id"]
                        )

                        st.rerun()

        st.divider()

# ===================================================
# NEW RELEASES
# ===================================================
with st.expander("🎵 Check New Releases"):

    if st.button("Check New Releases"):

        releases = get_new_releases()

        if not releases:

            st.info(
                "No new releases found."
            )

        else:

            for release in releases:

                col1, col2 = st.columns(
                    [1, 3]
                )

                with col1:

                    if release["image"]:

                        st.image(
                            release["image"],
                            width=150
                        )

                with col2:

                    st.subheader(
                        release["album"]
                    )

                    st.write(
                        f"🎤 {release['artist']}"
                    )

                    st.write(
                        f"📅 {release['date']}"
                    )

                    st.link_button(
                        "Open in Spotify",
                        release["url"]
                    )

                st.divider()


# ===================================================
# SHUFFLE PLAYLIST
# ===================================================
with st.expander("🔀 Shuffle Playlist"):

    playlist_link = st.text_input(
        "Spotify Playlist Link"
    )

    if st.button("Shuffle Playlist"):

        if playlist_link:

            shuffle_playlist(
                playlist_link
            )

            st.success(
                "Playlist shuffled!"
            )

        else:

            st.warning(
                "Paste a playlist link."
            )


# ===================================================
# PLAYLIST TOOLS
# ===================================================
with st.expander("📂 Playlist Tools"):

    if st.button(
        "Update English Playlist"
    ):

        update_english_playlist()

        st.success(
            "English playlist updated!"
        )
