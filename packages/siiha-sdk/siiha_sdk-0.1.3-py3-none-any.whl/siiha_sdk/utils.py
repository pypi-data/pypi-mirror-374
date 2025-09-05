from __future__ import annotations

import re
from typing import List, Optional
from datetime import datetime, timedelta, date
from calendar import monthrange

from dateutil.relativedelta import relativedelta, MO
import pytz

from siiha_sdk.config import DEFAULT_TIMEZONE

# ---------------- Basic constants ----------------

TZ = pytz.timezone(DEFAULT_TIMEZONE)

EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)

# for weekday parsing (0=Mon ... 6=Sun)
WEEKDAY_EN = {
    "monday": 0, "mon": 0,
    "tuesday": 1, "tue": 1, "tues": 1,
    "wednesday": 2, "wed": 2,
    "thursday": 3, "thu": 3, "thur": 3, "thurs": 3,
    "friday": 4, "fri": 4,
    "saturday": 5, "sat": 5,
    "sunday": 6, "sun": 6,
}
WEEKDAY_ZH = {
    "週一": 0, "星期一": 0, "禮拜一": 0,
    "週二": 1, "星期二": 1, "禮拜二": 1,
    "週三": 2, "星期三": 2, "禮拜三": 2,
    "週四": 3, "星期四": 3, "禮拜四": 3,
    "週五": 4, "星期五": 4, "禮拜五": 4,
    "週六": 5, "星期六": 5, "禮拜六": 5,
    "週日": 6, "星期日": 6, "禮拜天": 6, "禮拜日": 6,
}
# 抓「下週X」裡的單一中文數字
WEEKDAY_ZH_CHAR_INDEX = {"一":0, "二":1, "三":2, "四":3, "五":4, "六":5, "日":6, "天":6}

# ---------------- Small pure helpers ----------------

def cleanse_text(s: Optional[str]) -> Optional[str]:
    if s is None:
        return None
    s = s.strip()
    return s or None

def normalize_attendees(raw: Optional[List[str]]) -> List[str]:
    """Return a deduped list of lowercase emails (accepts 'Name <mail>' etc.)."""
    if not raw:
        return []
    emails, seen = [], set()
    for x in raw:
        if not isinstance(x, str):
            continue
        # 抓字串中所有可能 email（允許在 <...> 內）
        found = EMAIL_RE.findall(x)
        for em in found:
            em = em.strip().lower()
            if em and em not in seen:
                emails.append(em)
                seen.add(em)
    return emails

def to_rfc3339(dt: Optional[datetime]) -> Optional[str]:
    """Ensure RFC3339 with timezone (default Asia/Taipei if naive)."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = TZ.localize(dt)
    else:
        dt = dt.astimezone(TZ)
    return dt.isoformat()

# ---------------- Date-only parser ----------------

def _clamp_day(y: int, m: int, d: int) -> int:
    return max(1, min(d, monthrange(y, m)[1]))

def parse_anchor_date(
    text: str,
    hint_hour: int = 9,
    hint_minute: int = 0,
    now: Optional[datetime] = None,
) -> date:
    """
    只解析「日期」（不含時間），規則：
      - 今天/明天/後天
      - 顯式日期：YYYY/MM/DD、YYYY-MM-DD、M/D、M月D日｜號
        * 若有 '明年/next year' 或 '今年/this year'，對 M/D 與 中文日期的年份套用覆蓋
      - 下個月（可含幾號；無則預設 1 號；會 clamp 到該月最後一天）
      - next week/下週/下周/下星期（可帶週幾；未帶則預設下週一）
      - 週幾（以今天往後找最近一次；若今天就是該週幾且 hint 時間已過→+7 天）
      - 都沒有就回傳今天
    """
    if not isinstance(text, str) or not text.strip():
        return (now or datetime.now(TZ)).date()

    now = now or datetime.now(TZ)
    lower = text.lower()

    # 相對日
    if re.search(r"\btoday\b|今天", lower):
        return now.date()
    if re.search(r"\btomorrow\b|明天", lower):
        return (now + timedelta(days=1)).date()
    if re.search(r"day after tomorrow|後天", lower):
        return (now + timedelta(days=2)).date()

    # 年份偏好詞
    wants_next_year = bool(re.search(r"\bnext year\b|明年", lower))
    wants_this_year = bool(re.search(r"\bthis year\b|今年", lower))

    # 顯式 YYYY/MM/DD 或 YYYY-MM-DD
    m = re.search(r"\b(19|20)\d{2}[/-](1?\d)[/-]([12]?\d|3[01])\b", text)
    if m:
        y, mo, d = map(int, re.split(r"[/-]", m.group(0)))
        d = _clamp_day(y, mo, d)
        return date(y, mo, d)

    # 顯式 M/D（只接受 / 或 -，避免把 10:00 當日期）
    m = re.search(r"(?<![:：])\b(1?\d)[/-]([12]?\d|3[01])\b(?!:\d{2})", text)
    if m:
        mo, d = int(m.group(1)), int(m.group(2))
        y = now.year + 1 if wants_next_year else now.year
        d = _clamp_day(y, mo, d)
        return date(y, mo, d)

    # 中文：X月Y日/號
    m = re.search(r"\b(1?\d)\s*月\s*(\d{1,2})\s*(?:日|号|號)\b", text)
    if m:
        mo, d = int(m.group(1)), int(m.group(2))
        y = now.year + 1 if wants_next_year else now.year
        d = _clamp_day(y, mo, d)
        return date(y, mo, d)

    # 下個月（可帶幾號）
    if ("下個月" in text) or ("下月" in text) or ("next month" in lower):
        dm = re.search(r"([12]?\d|3[01])\s*(?:日|号|號)", text) or re.search(r"\b([12]?\d|3[01])\b", text)
        day_hint = int(dm.group(1)) if dm else 1
        nm = now + relativedelta(months=+1)
        y, mo = nm.year + (1 if wants_next_year else 0), nm.month
        d = _clamp_day(y, mo, day_hint)
        return date(y, mo, d)

    # --- 下週X（穩定版：先取下週一，再加索引天數）---
    m_zh_next = re.search(r"(下週|下周|下星期|下禮拜)\s*(?:的)?\s*(?:週|周|星期|禮拜)?\s*([一二三四五六日天])?", text)
    if m_zh_next:
        next_monday = now + relativedelta(weekday=MO(+1))
        idx = WEEKDAY_ZH_CHAR_INDEX.get(m_zh_next.group(2), 0)
        target = next_monday + timedelta(days=idx)
        return date(target.year, target.month, target.day)

    m_en_next = re.search(
        r"\bnext week(?:\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tue|tues|wed|thu|thur|thurs|fri|sat|sun))?\b",
        lower
    )
    if m_en_next:
        next_monday = now + relativedelta(weekday=MO(+1))
        if m_en_next.group(1):
            wd = WEEKDAY_EN.get(m_en_next.group(1), 0)
        else:
            wd = 0
        target = next_monday + timedelta(days=wd)
        return date(target.year, target.month, target.day)

    # 單純寫週幾（以今天往後找最近一次）
    for k, wd in {**WEEKDAY_EN, **WEEKDAY_ZH}.items():
        if k in lower or k in text:
            today_wd = now.weekday()
            days_ahead = (wd - today_wd) % 7
            if days_ahead == 0:
                # 今天就是該週幾：若時間已過，用下週
                if (now.hour, now.minute) >= (hint_hour, hint_minute):
                    days_ahead = 7
            base = now + timedelta(days=days_ahead)
            return date(base.year, base.month, base.day)

    # 無任何日期訊號 → 今天
    return now.date()

# ---------------- Datetime parser (date + time) ----------------

# 句子級時段詞（補 am/pm 用）
_PERIOD_PM_RE = re.compile(r"\bpm\b|下午|晚上", re.IGNORECASE)
_PERIOD_AM_RE = re.compile(r"\bam\b|上午|早上", re.IGNORECASE)

def _normalize_ampm(ap: Optional[str]) -> Optional[str]:
    if not ap:
        return None
    ap = ap.lower()
    if ap in ["pm", "下午", "晚上"]:
        return "pm"
    if ap in ["am", "上午", "早上"]:
        return "am"
    return None  # '點' 等視為中性

# 單點時間（不處理區間；區間交給 nlp.parse_natural_event）
_TIME_SINGLE_RE = re.compile(
    r"(?P<h>\d{1,2})(?::(?P<m>\d{2}))?\s*(?P<ap>am|pm|上午|下午|早上|晚上|點)?",
    re.IGNORECASE,
)

def parse_natural_datetime(text: str) -> Optional[datetime]:
    """
    只負責把「一句話」解析成一個基準 datetime（Asia/Taipei）：
      - 日期靠 parse_anchor_date()（避免把 10:00 誤當日期、支援 2026/1/2、下個月、週幾、next week 等）
      - 時間抓單點（3pm、15:30、下午3點、3:00、3點）；若沒寫 → 預設 09:00
      - '下午/晚上' 在前也會正確補 pm
    """
    if not text or not isinstance(text, str):
        return None

    now = datetime.now(TZ)

    # 1) 先抓時間（單點）
    hour, minute = 9, 0  # default 09:00
    tm = _TIME_SINGLE_RE.search(text)
    if tm:
        h = int(tm.group("h"))
        m = int(tm.group("m") or 0)
        ap = _normalize_ampm(tm.group("ap"))
        if not ap:
            ap = "pm" if _PERIOD_PM_RE.search(text) else ("am" if _PERIOD_AM_RE.search(text) else None)
        # 24h 轉換
        if ap == "pm" and 1 <= h <= 11:
            h += 12
        if ap == "am" and h == 12:
            h = 0
        # 邊界保護
        h = max(0, min(h, 23))
        m = max(0, min(m, 59))
        hour, minute = h, m

    # 2) 用 hint 時間算出 anchor date（避免時間數字影響日期）
    anchor = parse_anchor_date(text, hint_hour=hour, hint_minute=minute, now=now)

    # 3) 組成時區感知的 datetime（pytz 正確作法：localize）
    naive = datetime(anchor.year, anchor.month, anchor.day, hour, minute)
    dt = TZ.localize(naive)
    return dt
