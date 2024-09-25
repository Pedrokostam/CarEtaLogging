from datetime import datetime
import os
from pathlib import Path
from typing import Any, Optional
from zoneinfo import ZoneInfo
import gsheet_pandas
import gspread
from gspread.worksheet import Worksheet
from google.oauth2.credentials import Credentials
from google.auth.transport import requests
from google_auth_oauthlib.flow import InstalledAppFlow
import pandas as pd
from gsheet_pandas import DriveConnection

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
    params = {"title": "Test", "folder_id": "1C3v18sCG4WHRTWfpxmoY4PxfQ3EOOHpQ"}
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
    d: dict[str, Any] = {}
    for r in routes:
        d[r.name] = str(r.duration)
    return d


GOOGLE_START_DATE = datetime(1899, 12, 30)


def add_row_with_current_time(frame: pd.DataFrame, values: dict[str, Any], datetime_added: Optional[datetime] = None):
    current_time = datetime_added or datetime.now()
    google_start = datetime(1899, 12, 30)
    diff = current_time - google_start
    days_since_float = diff.total_seconds() / (24 * 60 * 60)
    date_days = int(days_since_float)
    time_days = days_since_float - date_days
    time_dict = {"Time": time_days, "Date": date_days, "Datetime": days_since_float}
    values = time_dict | values
    non_scalar = {k: [v] for k, v in values.items()}
    frame_to_add = pd.DataFrame.from_dict(non_scalar)
    return pd.concat([frame, frame_to_add])


class Archiver:
    def __init__(self, credentials: str | Path, token: str | Path, spreadsheet_id: str) -> None:
        self.spreadsheet_id = spreadsheet_id
        credentials = Path(credentials).resolve()
        token = Path(token).resolve()
        self._drive = DriveConnection(credentials_dir=credentials, token_dir=token)

    def get_frame(self, sheet_name: str):
        try:
            return self._drive.download(self.spreadsheet_id, sheet_name)
        except Exception as e:
            if not e.args or e.args[0] != "Empty data":
                raise e
            return pd.DataFrame()

    def upload_frame(self, frame: pd.DataFrame, sheet_name: str):
        self._drive.upload(frame, self.spreadsheet_id, sheet_name)

    def ensure_sheets(self, *sheet_names: str):
        present_sheets = self._drive.get_sheets_names(self.spreadsheet_id)
        for name in sheet_names:
            if name not in present_sheets:
                self._drive.create_sheet(self.spreadsheet_id, name)
