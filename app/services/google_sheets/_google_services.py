# auth.py

from __future__ import print_function

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# not working for now, tokens should be generated manually
credentials = Credentials.from_authorized_user_file("token.json", scopes=SCOPES)

sheet = build("sheets", "v4", credentials=credentials)
drive = build("drive", "v3", credentials=credentials)
