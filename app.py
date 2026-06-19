import streamlit as st
from new_releases import get_new_releases
from shuffle_playlist import shuffle_playlist
from split_playlists import update_english_playlist
from datetime import datetime, timedelta
from sheet_utils import (
    get_artists,
    add_artist,
    remove_artist,
    update_artist_image
)

from spotify_utils import (
    get_artist_from_link,
    get_artist_info
)
from public_shuffle import public_shuffle


st.divider()
st.header("🌎 Public Playlist Shuffler")

public_shuffle()


st.title("🎵 Ryan's Spotify Tools")

password = st.text_input(
    "Admin Password",
    type="password"
)

is_admin = (
    password == st.secrets["ADMIN_PASSWORD"]
)

if is_admin:
    st.success("🔒 Admin Mode Enabled")

# ===================================================
# ARTIST RELEASE TRACKER
# ===================================================

if is_admin:

    st.header("🎵 Artist Release Tracker")

    # -------------------
    # ADD ARTIST
    # -------------------
    st.subheader("Add Artist")
    
    col1, col2 = st.columns([10.5, 1])
    
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
                artist["id"],
                artist["image"]
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

                col1, col2, col3 = st.columns(
                    [1.7, 3, 0.8]
                )

                # ---------- IMAGE ----------
                with col1:

                    # Repair old artists that don't have an image yet
                    if not artist["image"]:

                        info = get_artist_info(
                            artist["id"]
                        )

                        update_artist_image(
                            artist["id"],
                            info["image"]
                        )

                        artist["image"] = info["image"]

                    if artist["image"]:

                        st.image(
                            artist["image"],
                            width=130
                        )

                # ---------- NAME ----------
                with col2:

                    st.markdown(
                        f"### {artist['name']}"
                    )

                # ---------- DELETE ----------
                with col3:

                    if is_admin:
                    
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

# ---------- DEFAULT VALUES ----------
default_days = 7
default_date = datetime.today()

# ---------- SESSION STATE ----------
if "release_days" not in st.session_state:
    st.session_state.release_days = default_days

if "release_end_date" not in st.session_state:
    st.session_state.release_end_date = default_date

if "releases" not in st.session_state:
    st.session_state.releases = []


# ---------- CONTROLS ----------
col1, col2, col3 = st.columns([1, 5, 0.8])

with col1:

    days_input = st.number_input(
        "Days",
        min_value=1,
        value=st.session_state.release_days,
        label_visibility="collapsed"
    )

with col2:

    end_date_input = st.date_input(
        "End Date",
        value=st.session_state.release_end_date,
        label_visibility="collapsed"
    )

with col3:

    refresh_pressed = st.button(
        "Refresh"
    )


# ---------- ONLY CALL SPOTIFY WHEN REFRESH IS PRESSED ----------
if refresh_pressed:

    st.session_state.release_days = days_input
    st.session_state.release_end_date = end_date_input

    end_datetime = datetime.combine(
        st.session_state.release_end_date,
        datetime.min.time()
    )

    start_datetime = (
        end_datetime -
        timedelta(days=st.session_state.release_days)
    )

    st.session_state.releases = get_new_releases(
        days=st.session_state.release_days,
        start_date=start_datetime
    )


# ---------- DISPLAY SAVED RESULTS ----------
releases = st.session_state.releases

badge_count = len(releases)


# ---------- RELEASE DISPLAY ----------
with st.expander(
    f"🎵 New Releases 🔴 {badge_count}"
):

    if not releases:

        st.info(
            "Press Refresh to check for releases."
        )

    else:

        for release in releases:

            col1, col2 = st.columns([2, 3])

            with col1:

                if release["image"]:

                    st.image(
                        release["image"],
                        width=200
                    )

            with col2:

                st.markdown(
                    f"## {release['album']}"
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
if is_admin:   
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
if is_admin:
    st.divider()
    
    st.header("📂 Playlist Tools")
    
    if st.button(
        "Update English Playlist"
    ):
    
        update_english_playlist()
    
        st.success(
            "English playlist updated!"
        )
