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
st.subheader("Add Artist")

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

                with st.container(border=True):

                    # ---------- IMAGE ----------
                    image_col1, image_col2, image_col3 = st.columns([1, 2, 1])

                    with image_col2:

                        if info["image"]:
                        
                            st.markdown(
                                f"""
                                <div style="
                                    display:flex;
                                    justify-content:center;
                                ">
                                    <img
                                        src="{info['image']}"
                                        style="
                                            width:150x;
                                            height:150px;
                                            object-fit:cover;
                                            border-radius:10px;
                                        "
                                    >
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                    st.write("")

                    # ---------- NAME ----------
                    st.markdown(
                        f"""
                        <div style="
                            text-align:center;
                            font-size:30px;
                            font-weight:bold;
                        ">
                            {info["name"]}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    st.write("")
                    st.write("")

                    # ---------- REMOVE BUTTON ----------
                    button_col1, button_col2, button_col3 = st.columns([1, 2, 1])

                    with button_col2:

                        if st.button(
                            "❌ Remove",
                            key=f"delete_{artist['id']}"
                        ):

                            remove_artist(
                                artist["id"]
                            )

                            st.rerun()

        st.write("")

# ===================================================
# NEW RELEASES
# ===================================================

days = st.number_input(
    "Look back (days)",
    min_value=1,
    value=7,
    key="release_days"
)

start_datetime = None

use_custom_date = st.checkbox(
    "Use custom start date"
)

if use_custom_date:

    chosen_date = st.date_input(
        "Start date"
    )

    start_datetime = datetime.combine(
        chosen_date,
        datetime.min.time()
    )

releases = get_new_releases(
    days=days,
    start_date=start_datetime
)

badge_count = len(releases)

with st.expander(
    f"🎵 New Releases 🔴 {badge_count}"
):

    if not releases:

        st.info("No releases found.")

    else:

        for release in releases:

            col1, col2 = st.columns([2, 2])

            with col1:

                if release["image"]:

                    st.image(
                        release["image"],
                        width = 250
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
st.divider()

st.header("🔀 Shuffle Playlist")

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
st.divider()

st.header("📂 Playlist Tools")

if st.button(
    "Update English Playlist"
):

    update_english_playlist()

    st.success(
        "English playlist updated!"
    )
