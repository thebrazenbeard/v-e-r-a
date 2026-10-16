"""Temporal metadata contracts for Roots-style uncertain source history.

This module does not run Roots search or infer event dates from retrieval dates.
"""
from datetime import datetime, timedelta

PRECISIONS = {"INSTANT", "DAY", "MONTH", "INTERVAL", "UNKNOWN"}
BASES = {"MESSAGE_TIMESTAMP", "SOURCE_EVENT_DATE", "INFERRED_INTERVAL", "UNAVAILABLE"}


def timestamp(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(label + ": timezone-aware timestamp required")
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None or dt.utcoffset() is None:
            raise ValueError("no timezone")
    except ValueError as exc:
        raise ValueError(label + ": invalid timezone-aware ISO timestamp") from exc
    return dt


def validate_v2_time(t):
    """Require explicit unknown/uncertain event-time representation, no fake defaults."""
    if not isinstance(t, dict) or set(t) != {"precision", "earliest_at", "latest_at", "basis"}:
        raise ValueError("event_time needs precision/earliest_at/latest_at/basis")
    precision, basis = t["precision"], t["basis"]
    if precision not in PRECISIONS or basis not in BASES:
        raise ValueError("unrecognized event-time precision/basis")
    low, high = t["earliest_at"], t["latest_at"]
    if precision == "UNKNOWN":
        if low is not None or high is not None or basis != "UNAVAILABLE":
            raise ValueError("UNKNOWN event-time needs null bounds and UNAVAILABLE basis")
        return
    if basis == "UNAVAILABLE":
        raise ValueError("dated event-time must have an evidence basis")
    start, end = timestamp(low, "earliest_at"), timestamp(high, "latest_at")
    if end < start:
        raise ValueError("event-time interval reversed")
    if precision == "INSTANT" and start != end:
        raise ValueError("INSTANT time requires matching bounds")
    if precision != "INSTANT" and start == end:
        raise ValueError("bounded interval requires nonzero duration")
    if precision == "DAY" and end - start != timedelta(days=1):
        raise ValueError("DAY time requires a one-day interval")
    if precision == "MONTH" and not (
        start.day == 1 and end.day == 1 and
        end.year * 12 + end.month == start.year * 12 + start.month + 1
    ):
        raise ValueError("MONTH time requires a calendar-month interval")


def build_timeline(records):
    """Non-authoritative partial chronology: overlaps and unknowns stay visible."""
    placed, unplaced = [], []
    for rec in records:
        event = rec["event"]
        if event["schema"] == "redworm.event.v2":
            when = event["event_time"]
            if when["precision"] == "UNKNOWN":
                unplaced.append(rec)
                continue
            lower, upper = when["earliest_at"], when["latest_at"]
        else:
            lower = upper = event["occurred_at"]
        placed.append((timestamp(lower, "earliest"), timestamp(upper, "latest"), rec))
    placed.sort(key=lambda row: row[0])
    result = []
    for start, end, record in placed:
        overlaps = sorted([
            other["event"]["event_id"] for low, high, other in placed
            if other["event"]["event_id"] != record["event"]["event_id"]
            and start <= high and low <= end
        ])
        result.append({"event": record["event"], "admitted": record["admitted"],
                       "overlaps": overlaps, "sequence_proven": not bool(overlaps)})
    return {"non_authoritative": True, "ordered_candidates": result,
            "unplaced_unknown_time": unplaced,
            "note": "Overlapping intervals are not a proven total order; earliest accessible is not proven origin"}
