# src/siiha_sdk/calendar.py
from __future__ import annotations
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import re
import pytz
from dateutil.parser import isoparse

from siiha_sdk.auth import get_calendar_service
from siiha_sdk.utils import cleanse_text, normalize_attendees
from siiha_sdk.config import DEFAULT_TIMEZONE, DEFAULT_CALENDAR_ID, GOOGLE_SEND_UPDATES

TZ = pytz.timezone(DEFAULT_TIMEZONE)

# ---------- helpers for robust dedupe ----------

def _norm_title(s: Optional[str]) -> str:
    """標題正規化：trim / 合併空白 / 統一逗號 / 英文大小寫無關"""
    if not s:
        return ""
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    s = s.replace("，", ",")
    s = re.sub(r"\s*,\s*", ", ", s)
    return s.casefold()

def _same_instant(a_iso: str, b_iso: str) -> bool:
    """兩個 RFC3339 是否指向同一瞬間（跨時區也成立）"""
    try:
        return isoparse(a_iso) == isoparse(b_iso)
    except Exception:
        return False

def _day_window(start_iso: str) -> tuple[str, str]:
    """在 Asia/Taipei 展開該天的整日窗口（避免 Z 導致 UTC 偏移）。"""
    dt = isoparse(start_iso)                 # aware datetime
    dt_local = dt.astimezone(TZ)             # 轉成本地時區再切日界
    start_of_day = dt_local.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)
    return start_of_day.isoformat(), end_of_day.isoformat()

def find_existing_event(service, title: str, start_iso: str) -> Optional[Dict]:
    """同一天窗內：『同一瞬間』且『標題正規化後相等』→ 視為重複。"""
    tmin, tmax = _day_window(start_iso)
    want_title = _norm_title(title)

    res = service.events().list(
        calendarId=DEFAULT_CALENDAR_ID,
        q=want_title,                 # 只作為篩選提示；實際仍做嚴格比對
        timeMin=tmin,
        timeMax=tmax,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    for e in res.get("items", []):
        e_start_iso = e.get("start", {}).get("dateTime")
        if not e_start_iso:
            # 跳過全日事件（若未來要支援，再另開邏輯）
            continue
        same = _same_instant(e_start_iso, start_iso)
        same_title = _norm_title(e.get("summary")) == want_title
        if same and same_title:
            return e
    return None

# ---------- public API ----------

def create_calendar_event(
    title: str,
    start_iso: str,
    end_iso: str,
    location: Optional[str] = None,
    attendees: Optional[List[str]] = None,
    description: Optional[str] = None,
    timezone: str = DEFAULT_TIMEZONE,
    dedupe: bool = True,
) -> Dict:
    """
    Create a Google Calendar event (local OAuth).
    Assumes start_iso/end_iso are RFC3339 strings WITH timezone.
    """
    try:
        service = get_calendar_service()

        title = cleanse_text(title) or ""
        location = cleanse_text(location)
        description = cleanse_text(description)
        attendees = normalize_attendees(attendees)

        if dedupe:
            existing = find_existing_event(service, title, start_iso)
            if existing:
                return {
                    "ok": True,
                    "eventId": existing["id"],
                    "htmlLink": existing.get("htmlLink"),
                    "start": existing["start"].get("dateTime"),
                    "end": existing["end"].get("dateTime"),
                    "attendees": [a["email"] for a in existing.get("attendees", [])],
                    "timezone": timezone,
                    "deduped": True,
                }

        body = {
            "summary": title,
            "location": location,
            "description": description,
            "start": {"dateTime": start_iso, "timeZone": timezone},
            "end": {"dateTime": end_iso, "timeZone": timezone},
        }
        if attendees:
            body["attendees"] = [{"email": e} for e in attendees]

        event = service.events().insert(
            calendarId=DEFAULT_CALENDAR_ID,
            body=body,
            sendUpdates=GOOGLE_SEND_UPDATES,
        ).execute()

        return {
            "ok": True,
            "eventId": event["id"],
            "htmlLink": event.get("htmlLink"),
            "start": event["start"].get("dateTime"),
            "end": event["end"].get("dateTime"),
            "attendees": [a["email"] for a in event.get("attendees", [])],
            "timezone": timezone,
            "deduped": False,
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}
