# utils/durations.py
# utils/durations.py

def hms_to_seconds(value: str) -> int:
    """
    Parse 'HH:MM:SS', 'M:SS', or raw seconds into an int number of seconds.
    """
    value = value.strip().strip('"')
    if not value:
        return 0

    if ":" in value:
        parts = value.split(":")
        try:
            parts = [int(p) for p in parts]
        except ValueError:
            return 0

        if len(parts) == 3:
            h, m, s = parts
        elif len(parts) == 2:
            h = 0
            m, s = parts
        else:
            return 0

        return h * 3600 + m * 60 + s

    try:
        return int(value)
    except ValueError:
        return 0


def seconds_to_hms(secs: int) -> str:
    h = secs // 3600
    m = (secs % 3600) // 60
    s = secs % 60
    return f"{h:02d}:{m:02d}:{s:02d}"
