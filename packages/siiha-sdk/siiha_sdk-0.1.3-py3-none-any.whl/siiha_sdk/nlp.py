# src/siiha_sdk/nlp.py
from __future__ import annotations
import re
from typing import Optional, Tuple, List, Dict
from datetime import datetime, timedelta

import pytz

from siiha_sdk.utils import (
    TZ,                         # Asia/Taipei pytz timezone (from config)
    to_rfc3339,
    normalize_attendees,
    cleanse_text,
    EMAIL_RE,
    parse_anchor_date,          # ← 只負責「日期」的解析
)

# -----------------------------
# 時間樣式與時段偵測
# -----------------------------

_TIME_RANGE_RE = re.compile(
    r"""
    (?:(?P<p1>上午|下午|早上|晚上|凌晨)\s*)?                          # 可選：起始前綴
    (?P<h1>\d{1,2})(?::(?P<m1>\d{2}))?\s*(?P<ap1>am|pm|上午|下午|早上|晚上|凌晨|點)?   # start
    \s*[-–~到至]\s*
    (?:(?P<p2>上午|下午|早上|晚上|凌晨)\s*)?                          # 可選：結束前綴
    (?P<h2>\d{1,2})(?::(?P<m2>\d{2}))?\s*(?P<ap2>am|pm|上午|下午|早上|晚上|凌晨|點)?   # end
    """,
    re.IGNORECASE | re.VERBOSE,
)

_TIME_SINGLE_COLON_RE = re.compile(r"(?P<h>\d{1,2}):(?P<m>\d{2})")
_TIME_SINGLE_WORD_RE  = re.compile(r"(?P<h>\d{1,2})\s*(?P<ap>am|pm|上午|下午|早上|晚上|凌晨|點)", re.IGNORECASE)

_DURATION_RE = re.compile(
    r"(?P<n>\d+)\s*(?:minutes?|mins?|min|分鐘|分|hrs?|hours?|小時|hr)",
    re.IGNORECASE,
)

_PERIOD_PM_RE = re.compile(r"\bpm\b|下午|晚上", re.IGNORECASE)
_PERIOD_AM_RE = re.compile(r"\bam\b|上午|早上|凌晨", re.IGNORECASE)

def _normalize_ampm(ap: Optional[str]) -> Optional[str]:
    if not ap:
        return None
    ap = ap.lower()
    if ap in ["pm", "下午", "晚上"]:
        return "pm"
    if ap in ["am", "上午", "早上", "凌晨"]:
        return "am"
    return None  # '點' 之類視為中性

def _detect_period(text: str) -> Optional[str]:
    if _PERIOD_PM_RE.search(text):
        return "pm"
    if _PERIOD_AM_RE.search(text):
        return "am"
    return None

def _to_24h(hour: int, minute: int, ampm: Optional[str]) -> Tuple[int, int]:
    if ampm == "pm" and 1 <= hour <= 11:
        hour += 12
    if ampm == "am" and hour == 12:
        hour = 0
    return hour, minute

# -----------------------------
# 地點 / 參與者 / 標題
# -----------------------------

# 地點：明確標記（地點：/location：），或「 at XXX」「，@ Zoom」
_LOC_MARKED_RE = re.compile(r"(?:地點[:：]\s*|location[:：]\s*)(?P<loc>[^，,。.\n]+)")
_LOC_AT_RE     = re.compile(r"[，,]\s*@\s*(?P<loc>[^,，。@\n]+)")

def _extract_location(text: str) -> Optional[str]:
    m = _LOC_MARKED_RE.search(text)
    if m:
        return cleanse_text(m.group("loc"))
    m = _LOC_AT_RE.search(text)
    if m:
        return cleanse_text(m.group("loc"))
    return None

def _extract_attendees(text: str) -> List[str]:
    emails = EMAIL_RE.findall(text)
    return normalize_attendees(emails)

# 會造成 title 汙染的片段（標記、關鍵詞、日期/時段詞）
_TITLE_NOISE_PATTERNS = [
    r"地點[:：]\s*[^，,。.\n]+",
    r"location[:：]\s*[^，,。.\n]+",
    r"\b(?:invite|邀請)\b.*",

    # 日期詞（含前綴：上/本/這/下；支援 週/周/星期/禮拜 + 一二三四五六日/天）
    r"(?:上|本|這|下)?\s*(?:週|周|星期|禮拜)\s*[一二三四五六日天]",

    # 「本月/下月/今年/明年/今天/明天/後天」等
    r"(?:本月|這個月|這月|下個月|下月|明年|今年|今天|明天|後天)",

    # 阿拉伯數字 + 日/号/號
    r"\b([0-3]?\d)\s*[日号號]\b",

    # 時段詞
    r"(?:上午|下午|早上|晚上|凌晨|\bam\b|\bpm\b|點)",
]

def _infer_title(text: str, location: Optional[str], attendees: List[str]) -> str:
    s = text

    # 先刪 <...@...>（避免名稱殘留的 email 片段干擾）
    s = re.sub(r"<[^>]*@[^>]*>", "", s)

    # 先刪時間片段（順序很重要：區間 → 冒號單點 → 文字單點）
    for pat in (_TIME_RANGE_RE, _TIME_SINGLE_COLON_RE, _TIME_SINGLE_WORD_RE):
        s = pat.sub("", s)

    # 把「到/至 + 時段詞」殘渣（如「到凌晨」）也清掉
    s = re.sub(r"(?:到|至)\s*(?:凌晨|上午|下午|早上|晚上)", "", s)

    # 再來刪「邀請/地點/日期/時段詞」等雜訊
    for pat in _TITLE_NOISE_PATTERNS:
        s = re.sub(pat, "", s, flags=re.IGNORECASE)

    # 刪 email 本體
    for em in attendees:
        s = re.sub(re.escape(em), "", s, flags=re.IGNORECASE)

    # 若前面清掉「點」之後留下開頭的孤兒數字（例如「3 」），去除之
    s = re.sub(r"^[\s,，。]*\d{1,2}(?=\s|$)", "", s)

    # 刪殘渣與多餘符號
    s = re.sub(r"(?:\b(invite|邀請)\b|@| at )", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\s*,?\s*\.(?:com|net|org|edu|io|ai|tw|co)\b", "", s, flags=re.IGNORECASE)
    s = s.replace("—", " ").replace("-", " ")
    s = re.sub(r"(?:\s*[,，]\s*){2,}", ", ", s)  # 多逗號 → 一個
    s = re.sub(r"\s{2,}", " ", s)               # 多空白 → 一個

    s = cleanse_text(s) or ""
    s = s[:60].strip(" ，,。.;:—-")
    return s or "Untitled"

# -----------------------------
# 內部：抓時間範圍 / 時長
# -----------------------------

def _extract_time_range(text: str, base_date: datetime) -> Optional[Tuple[datetime, datetime]]:
    m = _TIME_RANGE_RE.search(text)
    if not m:
        return None

    global_period = _detect_period(text)

    h1 = int(m.group("h1")); m1 = int(m.group("m1") or 0)
    h2 = int(m.group("h2")); m2 = int(m.group("m2") or 0)

    # 先用後綴（ap1/ap2），沒有就用前綴（p1/p2），再沒有才用全句與起始繼承
    ap1 = _normalize_ampm(m.group("ap1")) or _normalize_ampm(m.group("p1")) or global_period
    ap2 = _normalize_ampm(m.group("ap2")) or _normalize_ampm(m.group("p2")) or ap1 or global_period

    sh, sm = _to_24h(h1, m1, ap1)
    eh, em = _to_24h(h2, m2, ap2)

    start = base_date.replace(hour=sh, minute=sm, second=0, microsecond=0)
    end   = base_date.replace(hour=eh, minute=em, second=0, microsecond=0)

    # 跨日：像「晚上11點到凌晨1點」
    if end <= start:
        end += timedelta(days=1)

    return start, end

def _extract_duration_minutes(text: str) -> Optional[int]:
    """找時長（分鐘）；支援 hr/小時/分鐘；找不到回 None。"""
    m = _DURATION_RE.search(text)
    if not m:
        # 特例：'開 45 分鐘'
        m = re.search(r"開\s*(\d+)\s*(?:分鐘|分)", text)
        if m:
            return int(m.group(1))
        return None
    n = int(m.group("n"))
    unit = m.group(0).lower()
    return n * 60 if ("hour" in unit or "hr" in unit or "小時" in unit) else n

# -----------------------------
# Public entry
# -----------------------------

def parse_natural_event(
    text: str,
    default_tz: str = "Asia/Taipei",
    default_duration_minutes: int = 60,
) -> Dict:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("parse_natural_event(text): text is empty")

    tz = pytz.timezone(default_tz)
    global_period = _detect_period(text)

    # 先偵測時間樣式
    rng_m = _TIME_RANGE_RE.search(text)
    single_colon_m = None if rng_m else _TIME_SINGLE_COLON_RE.search(text)
    single_word_m  = None if rng_m or single_colon_m else _TIME_SINGLE_WORD_RE.search(text)

    # 先預設這兩個，後面會填
    start_dt: Optional[datetime] = None
    end_dt:   Optional[datetime] = None
    hint_hour = 9
    hint_minute = 0

    if rng_m:
        # 用 p1/p2（前綴）+ ap1/ap2（後綴）估算起始小時作為 anchor hint
        ap1_hint = _normalize_ampm(rng_m.group("ap1")) or _normalize_ampm(rng_m.group("p1")) or global_period
        h1 = int(rng_m.group("h1")); m1 = int(rng_m.group("m1") or 0)
        sh, sm = _to_24h(h1, m1, ap1_hint)
        hint_hour, hint_minute = sh, sm

        # 先決定哪一天
        anchor = parse_anchor_date(text, hint_hour=hint_hour, hint_minute=hint_minute)
        base_day = datetime(anchor.year, anchor.month, anchor.day, 0, 0)

        # 真正做區間解析（含 p1/p2 與跨日）
        start_dt, end_dt = _extract_time_range(text, base_day)

    else:
        # 單點時間（冒號/文字）或完全沒時間
        if single_colon_m:
            h = int(single_colon_m.group("h")); m = int(single_colon_m.group("m"))
            ap = _detect_period(text)
            sh, sm = _to_24h(h, m, ap)
            hint_hour, hint_minute = sh, sm
        elif single_word_m:
            h = int(single_word_m.group("h"))
            ap = _normalize_ampm(single_word_m.group("ap")) or _detect_period(text)
            sh, sm = _to_24h(h, 0, ap)
            hint_hour, hint_minute = sh, sm
        else:
            sh, sm = 9, 0
            hint_hour, hint_minute = sh, sm

        # 用時間 hint 拿 anchor（避免把「3點」的 3 誤當日）
        anchor = parse_anchor_date(text, hint_hour=hint_hour, hint_minute=hint_minute)

        # 組 start/end（單點用時長補 end）
        start_dt = datetime(anchor.year, anchor.month, anchor.day, sh, sm)
        dur_min = _extract_duration_minutes(text) or default_duration_minutes
        end_dt = start_dt + timedelta(minutes=dur_min)

    # 其他欄位
    location = _extract_location(text)
    attendees = _extract_attendees(text)
    title = _infer_title(text, location, attendees)
    description = None

    return {
        "title": title,
        "start_iso": to_rfc3339(start_dt),
        "end_iso": to_rfc3339(end_dt),
        "location": location,
        "attendees": attendees,
        "description": description,
        "timezone": tz.zone,
    }
