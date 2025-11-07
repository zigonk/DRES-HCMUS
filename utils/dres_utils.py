"""
Utility functions for DRES CSV to JSON conversion.
"""

import uuid


def make_uuid():
    """Generate a new UUID string."""
    return str(uuid.uuid4())


def split_hints(hints_raw, delimiter='\n'):
    """
    Split hints string on specified delimiter and strip whitespace.

    Args:
        hints_raw: Raw hints string with delimiter separators
        delimiter: Delimiter to use for splitting (default is newline)

    Returns:
        List of stripped hint strings
    """
    if not hints_raw:
        return []
    # Split on delimiter and strip
    parts = [p.strip() for p in hints_raw.split(delimiter) if p.strip()]
    return parts

def frames_to_ms(frame_val, fps=30):
    """
    Convert frame number to milliseconds based on fps.

    Args:
        frame_val: Frame number (int or string)
        fps: Frames per second (default 30)

    Returns:
        Milliseconds as integer, or None if conversion fails
    """
    try:
        f = int(str(frame_val).strip())
        return int((f / fps) * 1000)
    except Exception:
        return None


def seconds_to_ms(second_val):
    """
    Convert seconds to milliseconds.

    Args:
        second_val: Time in seconds (float or string)

    Returns:
        Milliseconds as integer, or None if conversion fails
    """
    try:
        return int(float(second_val) * 1000)
    except (ValueError, TypeError):
        return None
