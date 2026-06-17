import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(creds)

sheet = client.open("Spotify Artists Watchlist").sheet1

records = sheet.get_all_records()

st.write("Connection successful!")
st.write(records[:5])

