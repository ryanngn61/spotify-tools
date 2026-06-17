import streamlit as st
import gspread
from google.oauth2.service_account import Credentials


def test_connection():

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

    st.success("✅ Connected successfully!")

    worksheet = sheet.sheet1

    rows = worksheet.get_all_values()

    st.write(rows[:5])
