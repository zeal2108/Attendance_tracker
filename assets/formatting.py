from datetime import datetime


def format_date_pretty(date_str):

    date = datetime.strptime(date_str, "%Y-%m-%d")
    day = date.day
    # Decide suffix based on the rules
    suffix = (
        "th" if 11 <= day <= 13 else
        {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    )
    # Format: 1st May 2025
    return date.strftime(f"{day}{suffix} {date.strftime('%B %Y')}")

def to_12_hour_format(time_str):
    from datetime import datetime
    if not time_str or ":" not in time_str:
        return time_str  # skip invalid or empty strings
    try:
        # Try parsing time with seconds
        t = datetime.strptime(time_str.strip(), "%H:%M:%S")
        return t.strftime("%I:%M %p").lstrip("0")
    except ValueError:
        try:
            # Try parsing time without seconds (e.g., "14:30")
            t = datetime.strptime(time_str.strip(), "%H:%M")
            return t.strftime("%I:%M %p").lstrip("0")
        except ValueError:
            return time_str