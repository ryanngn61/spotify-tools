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
    scope=(
        "playlist-read-private "
        "playlist-modify-private "
        "playlist-modify-public"
    )
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

# ======================================================
# CREATE OR UPDATE PLAYLIST
# ======================================================
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
        playlist = sp.user_playlist_create(
            user=user_id,
            name=playlist_name,
            public=False
        )
        playlist_id = playlist["id"]

    if len(track_ids) == 0:
        sp.playlist_replace_items(playlist_id, [])
        return

    sp.playlist_replace_items(playlist_id, track_ids[:100])
    for i in range(100, len(track_ids), 100):
        sp.playlist_add_items(playlist_id, track_ids[i:i + 100])

# ======================================================
# PLAYLIST SPLITTER & AUDIT TOOL
# ======================================================
def split_playlist(playlist_a_link, playlist_b_link):
    sp = get_sp()

    playlist_a_id = extract_playlist_id(playlist_a_link)
    playlist_b_id = extract_playlist_id(playlist_b_link)

    playlist_a_info = sp.playlist(playlist_a_id)
    output_name = f"{playlist_a_info['name']} Split"

    st.markdown(f"### 🕵️‍♂️ Duplicate Audit: `{playlist_a_info['name']}`")

    playlist_a = get_all_tracks(sp, playlist_a_id)
    playlist_b = get_all_tracks(sp, playlist_b_id)

    # Display basic counts
    col_stats1, col_stats2, col_stats3 = st.columns(3)
    col_stats1.metric("Playlist A Items", len(playlist_a))
    col_stats2.metric("Playlist B Items", len(playlist_b))
    col_stats3.metric("Missing From B", len(playlist_a) - len(playlist_b))

    # --------------------------------------------------
    # 1. COUNT OCCURRENCES IN PLAYLIST A
    # --------------------------------------------------
    track_id_counts = Counter()
    track_details = {} 

    for item in playlist_a:
        if not item or "track" not in item or not item["track"]:
            continue
        
        track = item["track"]
        if "id" in track and track["id"]:
            track_id = track["id"]
            track_id_counts[track_id] += 1
            
            if track_id not in track_details:
                artist_name = track["artists"][0]["name"] if track["artists"] else "Unknown Artist"
                track_details[track_id] = {
                    "name": track["name"],
                    "artist": artist_name,
                    "url": track["external_urls"].get("spotify", "")
                }

    # --------------------------------------------------
    # 2. DISPLAY DUPLICATES DIRECTLY IN APP
    # --------------------------------------------------
    duplicates = {tid: count for tid, count in track_id_counts.items() if count > 1}
    
    st.write("---")
    st.subheader(f"🚨 Found Duplicates ({len(duplicates)} unique tracks duplicate)")
    
    total_duplicate_copies = 0
    if not duplicates:
        st.success("✅ No duplicate track IDs found in Playlist A!")
    else:
        for tid, count in duplicates.items():
            details = track_details[tid]
            extra_copies = count - 1
            total_duplicate_copies += extra_copies
            
            col_song, col_link = st.columns([5, 1])
            with col_song:
                st.markdown(f"**[{count}x copies]** {details['name']} — *{details['artist']}*")
            with col_link:
                if details['url']:
                    st.markdown(f"[Listen 🔗]({details['url']})")
                    
        st.warning(f"📊 **Summary:** There are **{total_duplicate_copies} extra placeholder copies** cluttering up Playlist A.")
    
    # --------------------------------------------------
    # 3. BACKGROUND SUBTRACTION LOGIC (A - B)
    # --------------------------------------------------
    playlist_b_ids = set()
    for item in playlist_b:
        if item and "track" in item and item["track"] and item["track"]["id"]:
            playlist_b_ids.add(item["track"]["id"])

    output_track_ids = []
    seen_in_a = set()

    for item in playlist_a:
        if not item or "track" not in item or not item["track"] or not item["track"]["id"]:
            continue
        track_id = item["track"]["id"]

        if track_id in seen_in_a:
            continue
        seen_in_a.add(track_id)

        if track_id in playlist_b_ids:
            continue

        output_track_ids.append(track_id)

    st.write("---")
    
    if len(output_track_ids) > 0:
        st.info(f"✂️ Found **{len(output_track_ids)} unique tracks** in Playlist A that were completely missing from Playlist B.")
        user_id = sp.current_user()["id"]
        random.shuffle(output_track_ids)
        update_playlist(sp, user_id, output_name, output_track_ids)
        st.success(f"🎉 Created fresh `{output_name}` playlist with those missing items!")
    else:
        st.success("ℹ️ No unlinked tracks found! The math matches: the entire gap was caused entirely by duplicate songs.")
