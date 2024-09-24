from datetime import datetime
import os
from typing import Any
import gspread
from gspread.worksheet import Worksheet
from google.oauth2.credentials import Credentials
from google.auth.transport import requests
from google_auth_oauthlib.flow import InstalledAppFlow

from implementation.route import Route

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/spreadsheets",
]
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"


def authenticate():
    """Authenticate the user with OAuth2."""
    creds = None
    # Check if token file exists
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # If no valid credentials, prompt the user to log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(requests.Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(TOKEN_FILE, "w", encoding="utf8") as token:
            token.write(creds.to_json())

    return creds


def get_worksheet():

    creds = authenticate()
    client = gspread.auth.authorize(creds)
    params = {"title": "Careta Logs", "folder_id": "1C3v18sCG4WHRTWfpxmoY4PxfQ3EOOHpQ"}
    try:
        sheet = client.open(**params)
    except (gspread.exceptions.SpreadsheetNotFound, gspread.exceptions.APIError):
        sheet = client.create(**params)
    worksheet = sheet.get_worksheet(0)
    return worksheet


def add_data(sheet: Worksheet, data: dict[Any, str | int | float]):
    keys = data.keys()
    headers = sheet.get_values("1:1")[0]
    missing_headers = [m for m in headers if m not in keys]
    ordered_values = []

    for cell_val in headers:
        if cell_val in keys:
            ordered_values.append(data[cell_val])
        else:
            ordered_values.append(None)
    if missing_headers:
        print("Adding missing headers")
    for miss in missing_headers:
        ordered_values.append(data[miss])
    sheet.update([headers + list(missing_headers)], "1:1")
    sheet.append_row(ordered_values)


def routes_to_dict(routes: list[Route]):
    time = datetime.now()
    d: dict[str, Any] = {
        "Date": time.strftime("%Y-%m-%d"),
        "Time": time.strftime("%H:%M:%S"),
    }
    for r in routes:
        d[r.name] = str(r.duration)
    return d
