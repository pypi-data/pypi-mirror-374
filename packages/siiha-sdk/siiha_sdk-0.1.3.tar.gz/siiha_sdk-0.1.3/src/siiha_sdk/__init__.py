"""
SIIHA SDK — minimal, local-first helpers for turning natural text into
Google Calendar events.

Public API:
- parse_natural_event(text) -> dict
- create_calendar_event(**event_kwargs) -> dict
- get_calendar_service() -> googleapiclient Calendar service
- to_rfc3339(dt), normalize_attendees([...])
"""

from .nlp import parse_natural_event
from .calendar import create_calendar_event
from .auth import get_calendar_service
from .utils import to_rfc3339, normalize_attendees

__all__ = [
    "parse_natural_event",
    "create_calendar_event",
    "get_calendar_service",
    "to_rfc3339",
    "normalize_attendees",
    "__version__",
]

__version__ = "0.1.3"
