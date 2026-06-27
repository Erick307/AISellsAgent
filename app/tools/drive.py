from functools import lru_cache

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from langchain_core.tools import tool

from app.config import settings

_SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
]


@lru_cache(maxsize=1)
def _credentials():
    creds = None
    token_path = settings.google_token_path

    if __import__("os").path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, _SCOPES)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(token_path, "w") as f:
            f.write(creds.to_json())

    if not creds or not creds.valid:
        raise RuntimeError(
            f"Google credentials not found or invalid. "
            f"Run `uv run python scripts/auth_google.py` to authenticate."
        )

    return creds


def _drive():
    return build("drive", "v3", credentials=_credentials(), cache_discovery=False)


def _sheets():
    return build("sheets", "v4", credentials=_credentials(), cache_discovery=False)


@tool
def search_drive_files(query: str) -> str:
    """Search Google Drive for spreadsheets whose name contains the query string.
    Returns a list of matching file names and their IDs."""
    try:
        escaped = query.replace("'", "\\'")
        results = (
            _drive()
            .files()
            .list(
                q=(
                    f"name contains '{escaped}' "
                    "and mimeType='application/vnd.google-apps.spreadsheet' "
                    "and trashed=false"
                ),
                fields="files(id, name)",
                pageSize=10,
            )
            .execute()
        )
        files = results.get("files", [])
        if not files:
            return f"No spreadsheets found matching '{query}'."
        return "\n".join(f"- {f['name']}  (id: {f['id']})" for f in files)
    except HttpError as e:
        return f"Drive API error: {e}"


@tool
def list_spreadsheet_sheets(file_id: str) -> str:
    """List all sheet (tab) names inside a Google Spreadsheet.
    Use this before read_sheet_data when you don't know the sheet name."""
    try:
        meta = (
            _sheets()
            .spreadsheets()
            .get(spreadsheetId=file_id, fields="sheets.properties.title")
            .execute()
        )
        names = [s["properties"]["title"] for s in meta.get("sheets", [])]
        if not names:
            return "No sheets found in this spreadsheet."
        return "Sheets: " + ", ".join(names)
    except HttpError as e:
        return f"Sheets API error: {e}"


@tool
def read_sheet_data(file_id: str, sheet_name: str) -> str:
    """Read all rows from a sheet in a Google Spreadsheet.
    file_id comes from search_drive_files; sheet_name from list_spreadsheet_sheets.
    Returns the data as tab-separated rows."""
    try:
        result = (
            _sheets()
            .spreadsheets()
            .values()
            .get(spreadsheetId=file_id, range=sheet_name)
            .execute()
        )
        rows = result.get("values", [])
        if not rows:
            return f"Sheet '{sheet_name}' is empty."
        return "\n".join("\t".join(cell for cell in row) for row in rows)
    except HttpError as e:
        return f"Sheets API error: {e}"


def get_drive_tools() -> list:
    return [search_drive_files, list_spreadsheet_sheets, read_sheet_data]
