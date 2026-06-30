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
from playlist_splitter import split_playlist

st.set_page_config(page_title="Ryan's Spotify Tools", page_icon="🎵", layout="wide")
st.title("🎵 Ryan's Spotify Tools")

# ===================================================
# 1. PLAYLIST SPLITTER (NOW AT THE VERY TOP - PUBLIC)
# ===================================================
st.header("📂 Playlist Tools")
st.subheader("➖ Playlist Splitter")

playlist_a_link = st.text_input(
    "Playlist A Link",
    placeholder="Paste first Spotify playlist URL...",
    key="playlist_a"
)

playlist_b_link = st.text_input(
    "Playlist B Link",
    placeholder="Paste second Spotify playlist URL...",
    key="playlist_b"
)

if st.button("Create Split Playlist", type="primary"):
    if playlist_a_link and playlist_b_link:
        split_playlist(playlist_a_link, playlist_b_link)
        st.success("🎉 Split playlist created!")
    else:
        st.warning("⚠️ Paste both playlist links.")

st.divider()

# ===================================================
# 2. ADMIN AUTHENTICATION
# ===================================================
password = st.text_input("Admin Password", type="password")
is_admin = (password == st.secrets["ADMIN_PASSWORD"])

if is_admin:
    st.success("🔒 Admin Mode Enabled")
    
    # Rest of the tools organized in tabs for clean admin access
    tab1, tab2 = st.tabs(["🎯 Release Tracker & Watchlist", "🔀 Admin Shuffler"])
    
    # -----------------------------------------------
    # TAB 1: ARTIST RELEASE TRACKER & WATCHLIST
    # -----------------------------------------------
    with tab1:
        st.header("🎵 Artist Release Tracker")
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
                artist = get_artist_from_link(artist_link)
                success = add_artist(artist["name"], artist["id"], artist["image"])
                if success:
                    st.success(f"Added {artist['name']}")
                    st.rerun()
                else:
                    st.warning("Artist already exists")
            except Exception as e:
                st.error(e)

        st.write("---")
        
        # WATCHLIST
        artists = get_artists()
        st.subheader(f"🎧 Release Watchlist ({len(artists)} artists)")
        
        for i in range(0, len(artists), 2):
            row_cols = st.columns(2)
            for j in range(2):
                if i + j >= len(artists):
                    break
                artist = artists[i + j]
                with row_cols[j]:
                    col1, col2, col3 = st.columns([1.7, 3, 0.8])
                    with col1:
                        if not artist["image"]:
                            info = get_artist_info(artist["id"])
                            update_artist_image(artist["id"], info["image"])
                            artist["image"] = info["image"]
                        if artist["image"]:
                            st.image(artist["image"], width=130)
                    with col2:
                        st.markdown(f"### {artist['name']}")
                    with col3:
                        if st.button("❌", key=f"delete_{artist['id']}"):
                            remove_artist(artist["id"])
                            st.rerun()

        st.write("---")
        
        # NEW RELEASES PANEL
        st.subheader("🔴 Track New Releases")
        default_days = 7
        default_date = datetime.today()

        if "release_days" not in st.session_state:
            st.session_state.release_days = default_days
        if "release_end_date" not in st.session_state:
            st.session_state.release_end_date = default_date
        if "releases" not in st.session_state:
            st.session_state.releases = []

        ncol1, ncol2, ncol3 = st.columns([1, 5, 0.8])
        with ncol1:
            days_input = st.number_input("Days", min_value=1, value=st.session_state.release_days, label_visibility="collapsed")
        with ncol2:
            end_date_input = st.date_input("End Date", value=st.session_state.release_end_date, label_visibility="collapsed")
        with ncol3:
            refresh_pressed = st.button("Refresh")

        if refresh_pressed:
            st.session_state.release_days = days_input
            st.session_state.release_end_date = end_date_input
            end_datetime = datetime.combine(st.session_state.release_end_date, datetime.min.time())
            start_datetime = end_datetime - timedelta(days=st.session_state.release_days)
            st.session_state.releases = get_new_releases(days=st.session_state.release_days, start_date=start_datetime)

        releases = st.session_state.releases
        if not releases:
            st.info("Press Refresh to check for releases.")
        else:
            for release in releases:
                rcol1, rcol2 = st.columns([2, 3])
                with rcol1:
                    if release["image"]:
                        st.image(release["image"], width=200)
                with rcol2:
                    st.markdown(f"## {release['album']}")
                    st.write(f"🎤 {release['artist']}")
                    st.write(f"📅 {release['date']}")
                    st.link_button("Open in Spotify", release["url"])
                st.divider()

    # -----------------------------------------------
    # TAB 2: ADMIN SHUFFLERS & UPDATES
    # -----------------------------------------------
    with tab2:
        st.header("🔀 Admin Master Controls")
        
        if st.button("Update English Playlist"):
            update_english_playlist()
            st.success("English playlist updated!")
            
        st.divider()
        
        st.subheader("Shuffle Playlist")
        playlist_link = st.text_input("Spotify Playlist Link")
        if st.button("Shuffle Playlist"):
            if playlist_link:
                shuffle_playlist(playlist_link)
                st.success("Playlist shuffled!")
            else:
                st.warning("Paste a playlist link.")

# ===================================================
# 3. PUBLIC VIEW (When not logged in as admin)
# ===================================================
else:
    st.info("👋 Welcome! Extra tools (Release Tracker, Master Shufflers) are locked behind the Admin login.")
    st.divider()
    st.header("🌎 Public Playlist Shuffler")
    public_shuffle()
