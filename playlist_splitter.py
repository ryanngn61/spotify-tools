import random
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import streamlit as st
from collections import Counter

CLIENT_ID = st.secrets["SPOTIFY_CLIENT_ID"]
CLIENT_SECRET = st.secrets["SPOTIFY_CLIENT_SECRET"]
REDIRECT_URI = "https://127.0.0.1:8888/callback/"

# ======================================================
# AUTH
# ======================================================
auth_manager = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope="playlist-read-private playlist-modify-private playlist-modify-public"
)

def get_sp():
    token_info = auth_manager.refresh_access_token(
        st.secrets["SPOTIFY_REFRESH_TOKEN"]
    )
    return spotipy.Spotify(auth=token_info["access_token"])

# ======================================================
# HELPERS
# ======================================================
def extract_playlist_id(link):
    link = link.split("?")[0]
    return link.split("/")[-1]

def get_all_tracks(sp, playlist_id):
    tracks = []
    results = sp.playlist_items(
        playlist_id,
        limit=100,
        additional_types=["track"]
    )
    while True:
        tracks.extend(results["items"])
        if results["next"]:
            results = sp.next(results)
        else:
            break
    return tracks

def update_playlist(sp, user_id, playlist_name, track_ids):
    playlist_id = None
    results = sp.current_user_playlists(limit=50)
    while True:
        for playlist in results["items"]:
            if playlist["name"] == playlist_name:
                playlist_id = playlist["id"]
                break
        if playlist_id:
            break
        if results["next"]:
            results = sp.next(results)
        else:
            break

    if playlist_id is None:
        playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=False)
        playlist_id = playlist["id"]

    if len(track_ids) == 0:
        sp.playlist_replace_items(playlist_id, [])
        return

    sp.playlist_replace_items(playlist_id, track_ids[:100])
    for i in range(100, len(track_ids), 100):
        sp.playlist_add_items(playlist_id, track_ids[i:i + 100])

# ======================================================
# PLAYLIST SPLITTER & EXACT DUPLICATE AUDIT
# ======================================================
def split_playlist(playlist_a_link, playlist_b_link):
    sp = get_sp()

    playlist_a_id = extract_playlist_id(playlist_a_link)
    playlist_b_id = extract_playlist_id(playlist_b_link)

    playlist_a_info = sp.playlist(playlist_a_id)
    output_name = f"{playlist_a_info['name']} Split (Missing Songs)"

    st.markdown(f"### 🕵️‍♂️ Advanced Audit: `{playlist_a_info['name']}`")

    playlist_a = get_all_tracks(sp, playlist_a_id)
    playlist_b = get_all_tracks(sp, playlist_b_id)

    # 1. Gather Playlist B lookup
    playlist_b_lookup = set()
    for item in playlist_b:
        if item and "track" in item and item["track"]:
            track = item["track"]
            track_name = track.get("name", "").lower().strip()
            artist_name = track["artists"][0]["name"].lower().strip() if track.get("artists") else ""
            if track_name:
                playlist_b_lookup.add(f"{track_name} ||| {artist_name}")

    # --------------------------------------------------
    # 2. COUNT EXACT OCCURRENCES IN PLAYLIST A
    # --------------------------------------------------
    track_counts = Counter()
    track_details = {}
    local_tracks_a = []

    for item in playlist_a:
        if not item or "track" not in item or not item["track"]:
            continue
            
        track = item["track"]
        track_name = track.get("name", "Unknown Title").strip()
        artist_name = track["artists"][0]["name"].strip() if track.get("artists") else "Unknown Artist"
        track_key = f"{track_name.lower()} ||| {artist_name.lower()}"
        track_id = track.get("id")
        is_local = item.get("is_local", False) or (track_id and "local" in str(track_id))

        if is_local:
            local_tracks_a.append(f"📁 {track_name} — *{artist_name}*")
            continue

        # Count occurrences of normal tracks
        track_counts[track_key] += 1
        
        # Save track metadata for display
        if track_key not in track_details:
            track_details[track_key] = {
                "name": track_name,
                "artist": artist_name,
                "id": track_id,
                "url": track.get("external_urls", {}).get("spotify", "")
            }

    # Identify the actual duplicate entries (items with count > 1)
    duplicate_items = {k: v for k, v in track_counts.items() if v > 1}
    total_duplicate_extra_copies = sum(count - 1 for count in duplicate_items.values())

    # --------------------------------------------------
    # 3. IDENTIFY TRULY MISSING SONGS
    # --------------------------------------------------
    missing_tracks_from_b = []
    unique_output_track_ids = []

    for track_key, count in track_counts.items():
        # Check if missing from B
        if track_key not in playlist_b_lookup:
            details = track_details[track_key]
            missing_tracks_from_b.append(details)
            if details["id"]:
                unique_output_track_ids.append(details["id"])

    # --------------------------------------------------
    # DISPLAY METRICS CARD BREAKDOWN
    # --------------------------------------------------
    col_a, col_b, col_gap = st.columns(3)
    col_a.metric("Playlist A Total Items", len(playlist_a))
    col_b.metric("Playlist B Total Items", len(playlist_b))
    col_gap.metric("Total Gap Size", len(playlist_a) - len(playlist_b))

    st.markdown("#### 📊 Explaining the Gap:")
    col_dup, col_loc, col_miss = st.columns(3)
    col_dup.metric("Extra Duplicate Copies", total_duplicate_extra_copies)
    col_loc.metric("Local Files Found", len(local_tracks_a))
    col_miss.metric("True Missing Online Songs", len(missing_tracks_from_b))

    # --------------------------------------------------
    # DISPLAY DRILLDOWN LISTS
    # --------------------------------------------------
    
    # Section 1: Exact Duplicates List
    st.write("---")
    with st.expander(f"🌀 Exact Duplicate Songs Found ({len(duplicate_items)} unique tracks have duplicates)", expanded=True):
        if duplicate_items:
            for track_key, count in duplicate_items.items():
                details = track_details[track_key]
                col_song, col_link = st.columns([5, 1])
                with col_song:
                    st.markdown(f"**[{count}x copies]** {details['name']} — *{details['artist']}*")
                with col_link:
                    if details['url']:
                        st.markdown(f"[Open 🔗]({details['url']})")
        else:
            st.success("✅ Clean! No duplicate track names found in Playlist A.")

    # Section 2: Local Files
    with st.expander(f"📁 Local Files in Playlist A ({len(local_tracks_a)})", expanded=False):
        if local_tracks_a:
            for track in local_tracks_a:
                st.markdown(track)
        else:
            st.success("No local files found.")

    # Section 3: Genuinely Missing Songs
    with st.expander(f"❌ True Missing Songs from Playlist B ({len(missing_tracks_from_b)})", expanded=False):
        if not missing_tracks_from_b:
            st.success("No true missing online songs found!")
        else:
            for track in missing_tracks_from_b:
                col_song, col_link = st.columns([5, 1])
                with col_song:
                    st.markdown(f"👉 **{track['name']}** — *{track['artist']}*")
                with col_link:
                    if track['url']:
                        st.markdown(f"[Open 🔗]({track['url']})")

            if unique_output_track_ids:
                user_id = sp.current_user()["id"]
                random.shuffle(unique_output_track_ids)
                update_playlist(sp, user_id, output_name, unique_output_track_ids)
                st.success(f"🎉 Created fresh `{output_name}` playlist with these true missing items!")
