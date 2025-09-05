"""
Constants used throughout the alt_time_utils package.
"""

# Time format constants
ISO_FORMAT_WITH_Z = "Z"  # Suffix for UTC timestamps in ISO format
UTC_OFFSET_SEPARATOR = ":"  # Separator for UTC offset formatting

# File timestamp formats
FILE_TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"  # Format: YYYYMMDD_HHMMSS
DATE_STRING_FORMAT = "%Y%m%d"  # Format: YYYYMMDD
TIME_STRING_FORMAT = "%H%M%S"  # Format: HHMMSS

# Duration formatting thresholds
MILLISECONDS_THRESHOLD = 1.0  # Seconds below which to show milliseconds
SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = 3600
MILLISECONDS_PER_SECOND = 1000

# Timezone offset formatting
UTC_OFFSET_FORMAT = "%z"  # Format for timezone offset
UTC_OFFSET_ZERO = "+00:00"  # Default UTC offset string

# Duration formatting precision
DURATION_DECIMAL_PLACES = 2  # Decimal places for seconds in duration
