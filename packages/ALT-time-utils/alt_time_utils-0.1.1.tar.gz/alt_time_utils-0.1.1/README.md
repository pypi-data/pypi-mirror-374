# ALT-time-utils

A collection of time-related utility functions for Python applications.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Features

- 🌍 **UTC-first design**: All timestamps are UTC by default with timezone awareness
- 🔄 **Timezone conversions**: Easy conversion between UTC and local time
- 📅 **Multiple formats**: ISO 8601, file-friendly timestamps, and human-readable durations
- 🏷️ **Type hints**: Full type annotations for better IDE support
- ✅ **Well tested**: 100% test coverage
- 🚀 **Zero dependencies**: Uses only Python standard library

## Installation

```bash
pip install ALT-time-utils
```

## Quick Start

```python
from alt_time_utils import (
    get_utc_timestamp,
    get_utc_timestamp_string,
    format_duration,
    local_to_utc,
    utc_to_local
)

# Get current UTC time
utc_now = get_utc_timestamp()
print(utc_now)  # 2025-01-15 12:30:45.123456+00:00

# Get UTC timestamp as string with 'Z' suffix
utc_string = get_utc_timestamp_string()
print(utc_string)  # 2025-01-15T12:30:45.123456Z

# Convert local time to UTC
from datetime import datetime
local_time = datetime.now()
utc_time = local_to_utc(local_time)

# Format duration in human-readable format
duration = format_duration(3665.5)
print(duration)  # 1h 1m 5.5s
```

## API Reference

### Timestamp Functions

#### `get_utc_timestamp() -> datetime`
Get the current UTC timestamp with timezone info.

```python
>>> utc_time = get_utc_timestamp()
>>> print(utc_time.tzinfo)
datetime.timezone.utc
```

#### `get_utc_timestamp_string() -> str`
Get the current UTC timestamp as an ISO format string with 'Z' suffix.

```python
>>> timestamp = get_utc_timestamp_string()
>>> print(timestamp)
'2025-01-15T12:30:45.123456Z'
```

#### `get_local_timestamp() -> datetime`
Get the current timestamp in the local timezone.

```python
>>> local_time = get_local_timestamp()
>>> print(local_time.tzinfo)
<DstTzInfo 'America/New_York' EST-1 day, 19:00:00 STD>
```

### Timezone Conversion

#### `local_to_utc(local_dt: datetime) -> datetime`
Convert a local datetime to UTC. Handles both naive and timezone-aware datetimes.

```python
>>> from datetime import datetime
>>> local = datetime.now()  # Naive datetime
>>> utc = local_to_utc(local)
>>> print(utc.tzinfo)
datetime.timezone.utc
```

#### `utc_to_local(utc_dt: datetime) -> datetime`
Convert a UTC datetime to local timezone.

```python
>>> from datetime import datetime, timezone
>>> utc = datetime.now(timezone.utc)
>>> local = utc_to_local(utc)
>>> print(local.tzinfo)
<DstTzInfo 'America/New_York' EST-1 day, 19:00:00 STD>
```

### Formatting Functions

#### `get_file_timestamp() -> str`
Get timestamp formatted for filenames (YYYYMMDD_HHMMSS).

```python
>>> timestamp = get_file_timestamp()
>>> print(timestamp)
'20250115_123045'
```

#### `get_date_string() -> str`
Get the current date as a string (YYYYMMDD).

```python
>>> date_str = get_date_string()
>>> print(date_str)
'20250115'
```

#### `get_time_string() -> str`
Get the current time as a string (HHMMSS).

```python
>>> time_str = get_time_string()
>>> print(time_str)
'123045'
```

#### `format_duration(seconds: float) -> str`
Format a duration in seconds to a human-readable string.

```python
>>> format_duration(0.123)
'123ms'
>>> format_duration(45.6)
'45.6s'
>>> format_duration(3665.5)
'1h 1m 5.5s'
>>> format_duration(-5)
'0s'
```

### Utility Functions

#### `get_local_timezone_name() -> str`
Get the name of the local timezone.

```python
>>> tz_name = get_local_timezone_name()
>>> print(tz_name)
'EST'
```

#### `get_local_utc_offset() -> str`
Get the local timezone's UTC offset as a string.

```python
>>> offset = get_local_utc_offset()
>>> print(offset)
'-05:00'
```

#### `format_utc_timestamp(dt: datetime) -> str`
Format any datetime as UTC ISO string with 'Z' suffix.

```python
>>> from datetime import datetime
>>> dt = datetime.now()
>>> formatted = format_utc_timestamp(dt)
>>> print(formatted)
'2025-01-15T12:30:45.123456Z'
```

## Examples

### Working with Log Files

```python
from alt_time_utils import get_file_timestamp, get_date_string
import os

# Create timestamped log file
timestamp = get_file_timestamp()
log_file = f"app_{timestamp}.log"

# Organize logs by date
date_dir = get_date_string()
os.makedirs(f"logs/{date_dir}", exist_ok=True)
```

### Duration Tracking

```python
from alt_time_utils import get_utc_timestamp, format_duration

start_time = get_utc_timestamp()

# ... do some work ...

end_time = get_utc_timestamp()
duration = (end_time - start_time).total_seconds()
print(f"Operation took: {format_duration(duration)}")
```

### Timezone-Aware Operations

```python
from alt_time_utils import local_to_utc, utc_to_local, get_local_utc_offset
from datetime import datetime

# Schedule something in local time, store in UTC
local_scheduled = datetime(2025, 1, 20, 9, 0, 0)  # 9 AM local
utc_scheduled = local_to_utc(local_scheduled)

# Display in user's timezone
user_local = utc_to_local(utc_scheduled)
offset = get_local_utc_offset()
print(f"Meeting at {user_local.strftime('%I:%M %p')} ({offset})")
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/Avilir/time_utils.git
cd time_utils

# Set up development environment
./scripts/setup_dev.sh

# Or using make
make setup
```

### Running Tests

```bash
# Using make
make test

# Using script
./scripts/run_tests.sh

# Or directly with pytest
python -m pytest
```

### Code Quality

```bash
# Run all checks
make all

# Individual checks
make lint        # Run linting
make type-check  # Run type checking
make format      # Format code
```

### Building

```bash
# Build distributions
make build

# Or using script
./scripts/build.sh
```

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Run `make all` to ensure quality
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Avi Layani** - [alayani@redhat.com](mailto:alayani@redhat.com)

## Acknowledgments

- Inspired by the need for consistent time handling across Python projects
