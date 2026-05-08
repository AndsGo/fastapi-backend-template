from __future__ import annotations

from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo


def next_cron_run_after(expression: str, timezone: str, after: datetime) -> datetime:
    fields = expression.split()
    if len(fields) != 5:
        raise ValueError("cron expression must have five fields")

    minutes = _parse_field(fields[0], minimum=0, maximum=59)
    hours = _parse_field(fields[1], minimum=0, maximum=23)
    days = _parse_field(fields[2], minimum=1, maximum=31)
    months = _parse_field(fields[3], minimum=1, maximum=12)
    weekdays = _parse_field(fields[4], minimum=0, maximum=7)

    zone = ZoneInfo(timezone)
    aware_after = after if after.tzinfo is not None else after.replace(tzinfo=UTC)
    candidate = aware_after.astimezone(zone).replace(second=0, microsecond=0) + timedelta(
        minutes=1
    )

    for _ in range(366 * 24 * 60):
        cron_weekday = (candidate.weekday() + 1) % 7
        if (
            candidate.minute in minutes
            and candidate.hour in hours
            and candidate.day in days
            and candidate.month in months
            and (cron_weekday in weekdays or (cron_weekday == 0 and 7 in weekdays))
        ):
            return candidate.astimezone(UTC)
        candidate += timedelta(minutes=1)

    raise ValueError("cron expression did not produce a run time within one year")


def _parse_field(field: str, *, minimum: int, maximum: int) -> set[int]:
    if field == "*":
        return set(range(minimum, maximum + 1))

    if field.startswith("*/"):
        step = int(field[2:])
        if step <= 0:
            raise ValueError("cron step must be positive")
        return set(range(minimum, maximum + 1, step))

    value = int(field)
    if value < minimum or value > maximum:
        raise ValueError(f"cron value {value} outside range {minimum}-{maximum}")
    return {value}
