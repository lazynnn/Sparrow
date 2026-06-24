from __future__ import annotations

import datetime
from typing import Optional


def utc_isoformat(dt: Optional[datetime.datetime]) -> Optional[str]:
    if dt is None:
        return None
    if dt.tzinfo is not None:
        return dt.isoformat()
    return dt.isoformat() + "+00:00"
