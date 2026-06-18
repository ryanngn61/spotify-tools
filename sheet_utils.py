import streamlit as st
import gspread
from google.oauth2.service_account import Credentials


def get_sheet():

    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope
    )

    client = gspread.authorize(creds)

    sheet = client.open("Spotify Artists Watchlist")

    return sheet.sheet1


def get_artists():

    worksheet = get_sheet()

    rows = worksheet.get_all_records()

    return rows

def add_artist(name, artist_id):

    worksheet = get_sheet()

    artists = get_artists()

    # Prevent duplicates
    for artist in artists:
        if artist["id"] == artist_id:
            return False

    worksheet.append_row([name, artist_id])

    return True

def add_artist(name, artist_id):

    worksheet = get_sheet()

    artists = get_artists()

    # Prevent duplicates
    for artist in artists:
        if artist["id"] == artist_id:
            return False

    worksheet.append_row([name, artist_id])

    return True
