
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


def get_sheet():

    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )

    client = gspread.authorize(credentials)

    spreadsheet = client.open_by_key(
        st.secrets["SHEET_ID"]
    )

    return spreadsheet.sheet1


def get_artists():

    worksheet = get_sheet()

    rows = worksheet.get_all_records()

    return rows


def add_artist(name, artist_id, image):

    worksheet = get_sheet()

    artists = get_artists()

    for artist in artists:

        if artist["id"] == artist_id:
            return False

    worksheet.append_row([
        name,
        artist_id,
        image
    ])

    return True


def remove_artist(artist_id):

    worksheet = get_sheet()

    ids = worksheet.col_values(2)

    for i, value in enumerate(ids):

        if value == artist_id:

            worksheet.delete_rows(
                i + 1
            )

            break


def update_artist_image(
    artist_id,
    image_url
):

    worksheet = get_sheet()

    ids = worksheet.col_values(2)

    for i, value in enumerate(ids):

        if value == artist_id:

            worksheet.update_cell(
                i + 1,
                3,
                image_url
            )

            break
