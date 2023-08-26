from datetime import timedelta


def format_timedelta(td: timedelta) -> str:
    td_seconds = int(td.total_seconds())
    periods = [
        ("year", 60 * 60 * 24 * 365),
        ("month", 60 * 60 * 24 * 30),
        ("day", 60 * 60 * 24),
        ("hour", 60 * 60),
        ("minute", 60),
        ("second", 1),
    ]

    formatted_periods = []
    for period_name, period_seconds in periods:
        if td_seconds > period_seconds:
            period_value, td_seconds = divmod(td_seconds, period_seconds)
            maybe_plural = "s" if period_value > 1 else ""
            formatted_periods.append(f"{period_value} {period_name}{maybe_plural}")

    if not len(formatted_periods):
        # Less than a second
        return "0 seconds"

    return ", ".join(formatted_periods)
