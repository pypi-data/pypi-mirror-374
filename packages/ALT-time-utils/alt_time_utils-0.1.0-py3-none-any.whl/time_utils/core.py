"""
Core time-related utility functions.
"""

import time
from datetime import datetime, timezone

from time_utils.constants import (
    DATE_STRING_FORMAT,
    DURATION_DECIMAL_PLACES,
    FILE_TIMESTAMP_FORMAT,
    ISO_FORMAT_WITH_Z,
    MILLISECONDS_PER_SECOND,
    MILLISECONDS_THRESHOLD,
    SECONDS_PER_HOUR,
    SECONDS_PER_MINUTE,
    TIME_STRING_FORMAT,
    UTC_OFFSET_FORMAT,
    UTC_OFFSET_SEPARATOR,
    UTC_OFFSET_ZERO,
)


def get_utc_timestamp() -> datetime:
    """
    Get the current UTC timestamp.

    This is the centralized function for getting timestamps throughout
    the application, ensuring all times are in UTC with timezone info.

    Returns:
        datetime: Current UTC time with timezone info

    Example:
        >>> utc_time = get_utc_timestamp()
        >>> utc_time.tzinfo
        datetime.timezone.utc
    """
    return datetime.now(timezone.utc)


def get_utc_timestamp_string() -> str:
    """
    Get the current UTC timestamp as an ISO format string with 'Z' suffix.

    This is the standard way to represent UTC timestamps in ISO 8601 format.

    Returns:
        str: Current UTC time in ISO format with 'Z' suffix

    Example:
        >>> timestamp = get_utc_timestamp_string()
        >>> timestamp.endswith('Z')
        True
        >>> # Example output: "2025-01-15T12:30:45.123456Z"
    """
    utc_time = get_utc_timestamp()
    # Replace the '+00:00' with 'Z' for cleaner UTC representation
    return utc_time.isoformat().replace(UTC_OFFSET_ZERO, ISO_FORMAT_WITH_Z)


def get_local_timestamp() -> datetime:
    """
    Get the current timestamp in the local timezone.

    Returns a timezone-aware datetime object in the system's local timezone.

    Returns:
        datetime: Current time in local timezone with timezone info

    Example:
        >>> local_time = get_local_timestamp()
        >>> local_time.tzinfo is not None
        True
    """
    # Get current time and make it timezone-aware with local timezone
    return datetime.now().astimezone()


def local_to_utc(local_dt: datetime) -> datetime:
    """
    Convert a local datetime to UTC.

    If the input datetime is naive (no timezone info), it assumes it's in
    the system's local timezone. If it's already timezone-aware, it converts
    from that timezone to UTC.

    Args:
        local_dt: Datetime to convert (naive or timezone-aware)

    Returns:
        datetime: Timezone-aware datetime in UTC

    Example:
        >>> local_time = datetime.now()  # Naive local time
        >>> utc_time = local_to_utc(local_time)
        >>> utc_time.tzinfo
        datetime.timezone.utc
    """
    if local_dt.tzinfo is None:
        # Naive datetime - assume it's in local timezone
        local_dt = local_dt.replace(tzinfo=None).astimezone()

    # Convert to UTC
    return local_dt.astimezone(timezone.utc)


def utc_to_local(utc_dt: datetime) -> datetime:
    """
    Convert a UTC datetime to local timezone.

    If the input datetime is naive (no timezone info), it assumes it's in UTC.
    If it's already timezone-aware, it converts from that timezone to local.

    Args:
        utc_dt: Datetime to convert (naive or timezone-aware)

    Returns:
        datetime: Timezone-aware datetime in local timezone

    Example:
        >>> utc_time = datetime.now(timezone.utc)
        >>> local_time = utc_to_local(utc_time)
        >>> local_time.tzinfo is not None
        True
    """
    if utc_dt.tzinfo is None:
        # Naive datetime - assume it's in UTC
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)

    # Convert to local timezone
    return utc_dt.astimezone()


def get_local_timezone_name() -> str:
    """
    Get the name of the local timezone.

    Returns:
        str: Local timezone name (e.g., 'EST', 'PDT', 'IST')

    Example:
        >>> tz_name = get_local_timezone_name()
        >>> isinstance(tz_name, str)
        True
        >>> len(tz_name) > 0
        True
    """
    # Get timezone name based on whether DST is active
    is_dst = time.daylight and time.localtime().tm_isdst > 0
    return time.tzname[1 if is_dst else 0]


def format_utc_timestamp(dt: datetime) -> str:
    """
    Format a datetime as UTC ISO string with 'Z' suffix.

    If the datetime is not already in UTC, it will be converted first.

    Args:
        dt: datetime object to format (can be naive or timezone-aware)

    Returns:
        str: ISO format string with 'Z' suffix

    Example:
        >>> dt = datetime.now()
        >>> formatted = format_utc_timestamp(dt)
        >>> formatted.endswith('Z')
        True
        >>> # Example output: "2025-01-15T12:30:45.123456Z"
    """
    # Convert to UTC if not already
    if dt.tzinfo is None:
        # Assume naive datetime is UTC
        utc_dt = dt.replace(tzinfo=timezone.utc)
    elif dt.tzinfo != timezone.utc:
        # Convert to UTC
        utc_dt = dt.astimezone(timezone.utc)
    else:
        # Already UTC
        utc_dt = dt

    # Format with 'Z' suffix
    return utc_dt.isoformat().replace(UTC_OFFSET_ZERO, ISO_FORMAT_WITH_Z)


def get_local_utc_offset() -> str:
    """
    Get the local timezone's UTC offset as a string.

    Returns:
        str: UTC offset in format like '-05:00' or '+02:00'

    Example:
        >>> offset = get_local_utc_offset()
        >>> offset[0] in ['+', '-']
        True
        >>> len(offset) == 6  # ±HH:MM
        True
    """
    local_time = datetime.now().astimezone()
    offset = local_time.strftime(UTC_OFFSET_FORMAT)
    # Format as ±HH:MM
    if offset:
        return f"{offset[:3]}{UTC_OFFSET_SEPARATOR}{offset[3:]}"
    return UTC_OFFSET_ZERO


def get_file_timestamp() -> str:
    """
    Get timestamp formatted for filenames (YYYYMMDD_HHMMSS).

    This format is commonly used for log files, results directories,
    and other filesystem artifacts where a sortable timestamp is needed.

    Returns:
        str: Current UTC time formatted as 'YYYYMMDD_HHMMSS'

    Example:
        >>> timestamp = get_file_timestamp()
        >>> len(timestamp) == 15  # YYYYMMDD_HHMMSS
        True
        >>> timestamp[8] == '_'
        True
    """
    return get_utc_timestamp().strftime(FILE_TIMESTAMP_FORMAT)


def get_date_string() -> str:
    """
    Get the current date as a string (YYYYMMDD).

    Useful for daily logs, reports, or date-based file organization.

    Returns:
        str: Current UTC date formatted as 'YYYYMMDD'

    Example:
        >>> date_str = get_date_string()
        >>> len(date_str) == 8  # YYYYMMDD
        True
        >>> date_str.isdigit()
        True
    """
    return get_utc_timestamp().strftime(DATE_STRING_FORMAT)


def get_time_string() -> str:
    """
    Get the current time as a string (HHMMSS).

    Useful when only the time component is needed.

    Returns:
        str: Current UTC time formatted as 'HHMMSS'

    Example:
        >>> time_str = get_time_string()
        >>> len(time_str) == 6  # HHMMSS
        True
        >>> time_str.isdigit()
        True
    """
    return get_utc_timestamp().strftime(TIME_STRING_FORMAT)


def format_duration(seconds: float) -> str:
    """
    Format a duration in seconds to a human-readable string.

    Args:
        seconds: Duration in seconds

    Returns:
        str: Formatted duration (e.g., '1h 23m 45s', '45.6s', '123ms')

    Example:
        >>> format_duration(3665.5)
        '1h 1m 5.5s'
        >>> format_duration(45.6)
        '45.6s'
        >>> format_duration(0.123)
        '123ms'
        >>> format_duration(-5)
        '0s'
    """
    if seconds < 0:
        return "0s"

    if seconds < MILLISECONDS_THRESHOLD:
        return f"{int(seconds * MILLISECONDS_PER_SECOND)}ms"

    hours = int(seconds // SECONDS_PER_HOUR)
    minutes = int((seconds % SECONDS_PER_HOUR) // SECONDS_PER_MINUTE)
    secs = seconds % SECONDS_PER_MINUTE

    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        if secs == int(secs):
            parts.append(f"{int(secs)}s")
        else:
            parts.append(f"{secs:.{DURATION_DECIMAL_PLACES}f}s")

    return " ".join(parts)
