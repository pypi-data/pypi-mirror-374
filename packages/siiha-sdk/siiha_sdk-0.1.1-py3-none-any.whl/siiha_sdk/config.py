from __future__ import annotations

import os
import logging
from dataclasses import dataclass

# ---------- Defaults (can be overridden via environment) ----------

# Time & parsing
DEFAULT_TIMEZONE: str = os.getenv("SIIHA_DEFAULT_TZ", "Asia/Taipei")
DEFAULT_DURATION_MINUTES: int = int(os.getenv("SIIHA_DEFAULT_DURATION_MINUTES", "60"))

# Google OAuth files (local, user-owned)
GOOGLE_CREDS_FILE: str = os.getenv("GOOGLE_CREDS_FILE", "credentials.json")
GOOGLE_TOKEN_FILE: str = os.getenv("GOOGLE_TOKEN_FILE", "token.json")

# Google Calendar API
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/calendar.readonly",
]
DEFAULT_CALENDAR_ID: str = os.getenv("SIIHA_GOOGLE_CALENDAR_ID", "primary")
GOOGLE_SEND_UPDATES: str = os.getenv("SIIHA_GOOGLE_SEND_UPDATES", "all")  # "all"|"externalOnly"|"none"

# Dedupe strategy (for reference / toggles)
# current PoC: same-day + same title + same start == duplicate
DEDUPE_STRATEGY: str = os.getenv("SIIHA_DEDUPE_STRATEGY", "title+start+same-day")

# Logging
LOG_LEVEL: str = os.getenv("SIIHA_LOG_LEVEL", "INFO").upper()

# ---------- Helpers ----------

def configure_logging(level: str | None = None) -> None:
    """
    Minimal logger setup; idempotent enough for SDK/demo usage.
    """
    lvl_name = (level or LOG_LEVEL).upper()
    lvl = getattr(logging, lvl_name, logging.INFO)
    logging.basicConfig(
        level=lvl,
        format="%(asctime)s %(levelname)s [siiha] %(message)s",
    )

@dataclass(frozen=True)
class Settings:
    timezone: str = DEFAULT_TIMEZONE
    default_duration_minutes: int = DEFAULT_DURATION_MINUTES
    creds_file: str = GOOGLE_CREDS_FILE
    token_file: str = GOOGLE_TOKEN_FILE
    calendar_id: str = DEFAULT_CALENDAR_ID
    send_updates: str = GOOGLE_SEND_UPDATES
    dedupe_strategy: str = DEDUPE_STRATEGY
    log_level: str = LOG_LEVEL

def settings() -> Settings:
    """
    Snapshot current env-driven settings as a dataclass.
    (Useful for debugging / printing effective config.)
    """
    return Settings()
