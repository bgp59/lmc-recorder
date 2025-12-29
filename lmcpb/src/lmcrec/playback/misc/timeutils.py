"""Date time parser and formatter controlled by $LMCREC_TZ"""

import os
import re
import time
from datetime import datetime, timezone
from functools import lru_cache
from typing import Optional
from zoneinfo import ZoneInfo

from tzlocal import get_localzone


@lru_cache
def get_tzinfo(tz: Optional[str] = None) -> ZoneInfo:
    if tz is None:
        time.tzset()
        return get_localzone()
    return ZoneInfo(tz)


def get_lmcrec_tz():
    return get_tzinfo(os.environ.get("LMCREC_TZ") or os.environ.get("TZ"))


def format_ts(ts: Optional[float] = None) -> str:
    """Format timestamp  as per ISO 8601"""

    if ts is None:
        ts = time.time()
    return datetime.fromtimestamp(ts, get_lmcrec_tz()).isoformat()


def parse_ts(spec: str) -> float:
    """Parse ISO 8601 spec"""

    if spec.endswith("Z"):
        dt = datetime.fromisoformat(spec[:-1]).replace(tzinfo=timezone.utc)
    else:
        dt = datetime.fromisoformat(spec)
        if not re.search(r"[+-]\d{2}:\d{2}$", spec):
            dt = dt.replace(tzinfo=get_lmcrec_tz())
    return dt.timestamp()
