import os
from typing import Optional
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

CREDS_FILE = os.getenv("GOOGLE_CREDS_FILE", "credentials.json")
TOKEN_FILE = os.getenv("GOOGLE_TOKEN_FILE", "token.json")

SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/calendar.readonly",
]

def get_calendar_service():
    """
    Load local OAuth token and return Calendar service.
    This SDK does NOT run the first-time OAuth flow.
    If token is missing/invalid, raise with a clear message.
    """
    if not os.path.exists(TOKEN_FILE):
        raise ValueError(
            f"Missing token file: {TOKEN_FILE}. "
            "Please run your OAuth bootstrap to generate it."
        )

    creds: Optional[Credentials] = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # persist refreshed token
            with open(TOKEN_FILE, "w") as f:
                f.write(creds.to_json())
        else:
            raise ValueError(
                "Invalid or expired credentials. Please re-authenticate to refresh token."
            )

    try:
        return build("calendar", "v3", credentials=creds)
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Google Calendar service: {e}")
