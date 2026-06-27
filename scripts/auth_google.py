"""
One-time Google OAuth authentication.
Run this once to generate credentials/token.json — the bot uses that file going forward.

Usage:
    uv run python scripts/auth_google.py
"""
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
]

CREDENTIALS_PATH = Path("credentials/credentials.json")
TOKEN_PATH = Path("credentials/token.json")


def main():
    if not CREDENTIALS_PATH.exists():
        raise FileNotFoundError(
            f"OAuth credentials file not found at {CREDENTIALS_PATH}.\n"
            "Download it from Google Cloud Console → APIs & Services → Credentials → your OAuth client → Download JSON.\n"
            "Rename it to credentials.json and place it in the credentials/ folder."
        )

    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
    creds = flow.run_local_server(port=0)

    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_PATH.write_text(creds.to_json())
    print(f"Token saved to {TOKEN_PATH}. The bot is now authorized.")


if __name__ == "__main__":
    main()
