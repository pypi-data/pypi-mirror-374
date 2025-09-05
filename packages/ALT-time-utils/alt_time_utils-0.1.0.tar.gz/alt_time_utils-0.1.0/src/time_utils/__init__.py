"""
time_utils - A collection of time-related utility functions for Python.

This package provides utilities for working with timestamps, timezones,
and time formatting in Python applications.
"""

from time_utils.core import (
    format_duration,
    format_utc_timestamp,
    get_date_string,
    get_file_timestamp,
    get_local_timestamp,
    get_local_timezone_name,
    get_local_utc_offset,
    get_time_string,
    get_utc_timestamp,
    get_utc_timestamp_string,
    local_to_utc,
    utc_to_local,
)

__version__ = "0.1.0"
__author__ = "Avi Layani"
__email__ = "alayani@redhat.com"

__all__ = [
    "get_utc_timestamp",
    "get_utc_timestamp_string",
    "get_local_timestamp",
    "local_to_utc",
    "utc_to_local",
    "get_local_timezone_name",
    "format_utc_timestamp",
    "get_local_utc_offset",
    "get_file_timestamp",
    "get_date_string",
    "get_time_string",
    "format_duration",
]
