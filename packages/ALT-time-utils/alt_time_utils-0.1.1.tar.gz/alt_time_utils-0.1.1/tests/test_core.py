"""
Tests for alt_time_utils.core module.
"""

from datetime import datetime, timedelta, timezone
from typing import Any
from unittest.mock import patch

from alt_time_utils.core import (
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


class TestGetUTCTimestamp:
    """Tests for get_utc_timestamp function."""

    def test_returns_utc_timezone(self) -> None:
        """Test that returned datetime has UTC timezone."""
        result = get_utc_timestamp()
        assert result.tzinfo == timezone.utc

    def test_returns_current_time(self) -> None:
        """Test that returned time is close to current time."""
        before = datetime.now(timezone.utc)
        result = get_utc_timestamp()
        after = datetime.now(timezone.utc)
        assert before <= result <= after


class TestGetUTCTimestampString:
    """Tests for get_utc_timestamp_string function."""

    def test_returns_string_with_z_suffix(self) -> None:
        """Test that returned string ends with 'Z'."""
        result = get_utc_timestamp_string()
        assert result.endswith("Z")
        assert "+00:00" not in result

    def test_valid_iso_format(self) -> None:
        """Test that returned string is valid ISO format."""
        result = get_utc_timestamp_string()
        # Should be able to parse it back with 'Z' replaced
        parsed = datetime.fromisoformat(result.replace("Z", "+00:00"))
        assert parsed.tzinfo is not None

    @patch("alt_time_utils.core.get_utc_timestamp")
    def test_formats_correctly(self, mock_get_utc: Any) -> None:
        """Test correct formatting of timestamp."""
        mock_time = datetime(2025, 1, 15, 12, 30, 45, 123456, tzinfo=timezone.utc)
        mock_get_utc.return_value = mock_time
        result = get_utc_timestamp_string()
        assert result == "2025-01-15T12:30:45.123456Z"


class TestGetLocalTimestamp:
    """Tests for get_local_timestamp function."""

    def test_returns_timezone_aware(self) -> None:
        """Test that returned datetime is timezone-aware."""
        result = get_local_timestamp()
        assert result.tzinfo is not None

    def test_returns_current_time(self) -> None:
        """Test that returned time is close to current time."""
        before = datetime.now()
        result = get_local_timestamp()
        after = datetime.now()
        # Convert to naive for comparison
        result_naive = result.replace(tzinfo=None)
        assert before <= result_naive <= after


class TestLocalToUTC:
    """Tests for local_to_utc function."""

    def test_naive_datetime_conversion(self, naive_datetime: datetime) -> None:
        """Test conversion of naive datetime to UTC."""
        result = local_to_utc(naive_datetime)
        assert result.tzinfo == timezone.utc

    def test_aware_datetime_conversion(self, local_datetime: datetime) -> None:
        """Test conversion of timezone-aware datetime to UTC."""
        result = local_to_utc(local_datetime)
        assert result.tzinfo == timezone.utc

    def test_already_utc_datetime(self, utc_datetime: datetime) -> None:
        """Test that UTC datetime remains unchanged."""
        result = local_to_utc(utc_datetime)
        assert result == utc_datetime
        assert result.tzinfo == timezone.utc

    def test_custom_timezone_conversion(self, datetime_with_custom_tz: datetime) -> None:
        """Test conversion from custom timezone to UTC."""
        result = local_to_utc(datetime_with_custom_tz)
        assert result.tzinfo == timezone.utc
        # Should be 5.5 hours earlier in UTC (IST is UTC+5:30)
        expected = datetime_with_custom_tz - timedelta(hours=5, minutes=30)
        expected = expected.replace(tzinfo=timezone.utc)
        assert result == expected


class TestUTCToLocal:
    """Tests for utc_to_local function."""

    def test_naive_datetime_conversion(self, naive_datetime: datetime) -> None:
        """Test conversion of naive datetime (assumed UTC) to local."""
        result = utc_to_local(naive_datetime)
        assert result.tzinfo is not None
        # Should represent the same instant in time
        utc_version = naive_datetime.replace(tzinfo=timezone.utc)
        assert result.timestamp() == utc_version.timestamp()

    def test_aware_utc_datetime(self, utc_datetime: datetime) -> None:
        """Test conversion of UTC datetime to local."""
        result = utc_to_local(utc_datetime)
        assert result.tzinfo is not None
        # Time values should represent the same instant
        assert result.timestamp() == utc_datetime.timestamp()

    def test_custom_timezone_conversion(self, datetime_with_custom_tz: datetime) -> None:
        """Test conversion from custom timezone to local."""
        result = utc_to_local(datetime_with_custom_tz)
        assert result.tzinfo is not None
        # Time values should represent the same instant
        assert result.timestamp() == datetime_with_custom_tz.timestamp()


class TestGetLocalTimezoneName:
    """Tests for get_local_timezone_name function."""

    def test_returns_string(self) -> None:
        """Test that function returns a non-empty string."""
        result = get_local_timezone_name()
        assert isinstance(result, str)
        assert len(result) > 0

    @patch("time.daylight", 1)
    @patch("time.localtime")
    @patch("time.tzname", ("EST", "EDT"))
    def test_dst_active(self, mock_localtime: Any) -> None:
        """Test timezone name when DST is active."""
        mock_localtime.return_value.tm_isdst = 1
        result = get_local_timezone_name()
        assert result == "EDT"

    @patch("time.daylight", 1)
    @patch("time.localtime")
    @patch("time.tzname", ("EST", "EDT"))
    def test_dst_not_active(self, mock_localtime: Any) -> None:
        """Test timezone name when DST is not active."""
        mock_localtime.return_value.tm_isdst = 0
        result = get_local_timezone_name()
        assert result == "EST"


class TestFormatUTCTimestamp:
    """Tests for format_utc_timestamp function."""

    def test_naive_datetime(self, naive_datetime: datetime) -> None:
        """Test formatting of naive datetime (assumed UTC)."""
        result = format_utc_timestamp(naive_datetime)
        assert result == "2025-01-15T12:30:45.123456Z"
        assert result.endswith("Z")

    def test_utc_datetime(self, utc_datetime: datetime) -> None:
        """Test formatting of UTC datetime."""
        result = format_utc_timestamp(utc_datetime)
        assert result == "2025-01-15T12:30:45.123456Z"

    def test_non_utc_datetime(self, datetime_with_custom_tz: datetime) -> None:
        """Test formatting of non-UTC datetime (should convert to UTC)."""
        result = format_utc_timestamp(datetime_with_custom_tz)
        # IST is UTC+5:30, so UTC time should be 5.5 hours earlier
        assert result == "2025-01-15T07:00:45.123456Z"


class TestGetLocalUTCOffset:
    """Tests for get_local_utc_offset function."""

    def test_returns_formatted_offset(self) -> None:
        """Test that function returns properly formatted offset."""
        result = get_local_utc_offset()
        assert len(result) == 6  # ±HH:MM
        assert result[0] in ["+", "-"]
        assert result[3] == ":"
        assert result[1:3].isdigit()
        assert result[4:6].isdigit()

    def test_consistent_with_local_time(self) -> None:
        """Test that offset matches local time offset."""
        local_time = datetime.now().astimezone()
        offset_seconds = local_time.utcoffset().total_seconds() if local_time.utcoffset() else 0
        hours = int(offset_seconds // 3600)
        minutes = int((abs(offset_seconds) % 3600) // 60)
        expected = f"{hours:+03d}:{minutes:02d}"
        result = get_local_utc_offset()
        assert result == expected


class TestGetFileTimestamp:
    """Tests for get_file_timestamp function."""

    def test_format(self) -> None:
        """Test that timestamp has correct format."""
        result = get_file_timestamp()
        assert len(result) == 15  # YYYYMMDD_HHMMSS
        assert result[8] == "_"
        assert result[:8].isdigit()  # Date part
        assert result[9:].isdigit()  # Time part

    @patch("alt_time_utils.core.get_utc_timestamp")
    def test_uses_utc(self, mock_get_utc: Any) -> None:
        """Test that function uses UTC time."""
        mock_time = datetime(2025, 1, 15, 12, 30, 45, tzinfo=timezone.utc)
        mock_get_utc.return_value = mock_time
        result = get_file_timestamp()
        assert result == "20250115_123045"


class TestGetDateString:
    """Tests for get_date_string function."""

    def test_format(self) -> None:
        """Test that date string has correct format."""
        result = get_date_string()
        assert len(result) == 8  # YYYYMMDD
        assert result.isdigit()

    @patch("alt_time_utils.core.get_utc_timestamp")
    def test_uses_utc(self, mock_get_utc: Any) -> None:
        """Test that function uses UTC date."""
        mock_time = datetime(2025, 1, 15, 12, 30, 45, tzinfo=timezone.utc)
        mock_get_utc.return_value = mock_time
        result = get_date_string()
        assert result == "20250115"


class TestGetTimeString:
    """Tests for get_time_string function."""

    def test_format(self) -> None:
        """Test that time string has correct format."""
        result = get_time_string()
        assert len(result) == 6  # HHMMSS
        assert result.isdigit()

    @patch("alt_time_utils.core.get_utc_timestamp")
    def test_uses_utc(self, mock_get_utc: Any) -> None:
        """Test that function uses UTC time."""
        mock_time = datetime(2025, 1, 15, 12, 30, 45, tzinfo=timezone.utc)
        mock_get_utc.return_value = mock_time
        result = get_time_string()
        assert result == "123045"


class TestFormatDuration:
    """Tests for format_duration function."""

    def test_negative_duration(self) -> None:
        """Test handling of negative durations."""
        assert format_duration(-5) == "0s"
        assert format_duration(-100) == "0s"

    def test_milliseconds(self) -> None:
        """Test formatting of sub-second durations."""
        assert format_duration(0) == "0ms"
        assert format_duration(0.123) == "123ms"
        assert format_duration(0.999) == "999ms"

    def test_seconds(self) -> None:
        """Test formatting of second durations."""
        assert format_duration(1) == "1s"
        assert format_duration(45) == "45s"
        assert format_duration(45.6) == "45.60s"
        assert format_duration(59.9) == "59.90s"

    def test_minutes(self) -> None:
        """Test formatting of minute durations."""
        assert format_duration(60) == "1m"
        assert format_duration(90) == "1m 30s"
        assert format_duration(119) == "1m 59s"
        assert format_duration(120) == "2m"

    def test_hours(self) -> None:
        """Test formatting of hour durations."""
        assert format_duration(3600) == "1h"
        assert format_duration(3660) == "1h 1m"
        assert format_duration(3665) == "1h 1m 5s"
        assert format_duration(3665.5) == "1h 1m 5.50s"
        assert format_duration(3665.08) == "1h 1m 5.08s"
        assert format_duration(7200) == "2h"
        assert format_duration(7325) == "2h 2m 5s"

    def test_large_durations(self) -> None:
        """Test formatting of large durations."""
        assert format_duration(86400) == "24h"  # 1 day
        assert format_duration(90061) == "25h 1m 1s"  # > 1 day

    def test_edge_cases(self) -> None:
        """Test edge cases."""
        assert format_duration(0.0001) == "0ms"  # Very small
        assert format_duration(59.9) == "59.90s"  # Just under a minute
        assert format_duration(3599.9) == "59m 59.90s"  # Just under an hour
