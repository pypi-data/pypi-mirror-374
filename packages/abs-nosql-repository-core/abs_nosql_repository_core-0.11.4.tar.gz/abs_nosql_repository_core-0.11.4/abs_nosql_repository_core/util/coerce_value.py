from datetime import datetime, time, date
from functools import lru_cache
from typing import Any, Union, Dict, List
from bson import ObjectId

@lru_cache(maxsize=128)
def parse_datetime_or_time(value: str) -> Union[datetime, time, str]:
    """Try to parse a string into datetime or time."""
    formats = [
        # datetime formats
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%m-%d-%Y",
        "%m/%d/%Y",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",

        # time formats
        "%H:%M:%S",
        "%H:%M:%S.%f",
        "%H:%M",
    ]

    for fmt in formats:
        try:
            parsed = datetime.strptime(value, fmt)
            if "H" in fmt and "M" in fmt:  # time-only formats
                return parsed.time()
            return parsed
        except Exception:
            continue
    return value


BOOLEAN_MAP = {"true": True, "false": False}


def coerce_value(value: Any) -> Any:
    if isinstance(value, dict):
        # Special handling for time_range dict
        if "start" in value and "end" in value:
            return {k: coerce_value(v) for k, v in value.items()}
        elif "time" in value:
            return {"time":parse_datetime_or_time(value.get("time"))}
        else:
            return {k: coerce_value(v) for k, v in value.items()}

    if isinstance(value, list):
        return [coerce_value(v) for v in value]

    if isinstance(value, str):
        # Boolean
        lowered = value.lower()
        if lowered in BOOLEAN_MAP:
            return BOOLEAN_MAP[lowered]
        # ObjectId
        try:
            if ObjectId.is_valid(value):
                return ObjectId(value)
        except Exception as e:
            pass
        # Date or time
        return parse_datetime_or_time(value)

    # Everything else (int, float, None)
    return value