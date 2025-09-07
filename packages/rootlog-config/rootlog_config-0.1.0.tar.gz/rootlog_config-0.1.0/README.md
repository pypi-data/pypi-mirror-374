# Python Logger Utility

A simple, powerful Python logging utility that configures the root logger properly. No more complex setup - just call `setup_logger()` once and use standard `logging.info()` everywhere.

## Why This Logger?

Python's built-in logging is powerful but complex to set up correctly. This utility provides:

- **One function call** to configure both console and file logging
- **Root logger approach** - works seamlessly across all modules
- **Thread-safe** with optional queue-based logging for high performance
- **Automatic file organization** - logs organized by script/app name
- **Color-coded console output** for better debugging
- **Flexible rotation** - time-based or size-based with human-readable units
- **Graceful error handling** - falls back to console if file logging fails
- **Zero migration** - use standard `logging.info()` calls everywhere

## Quick Start

```python
from logger import setup_logger
import logging

# Configure once at application entry point
setup_logger(app="myapp")

# Use standard logging everywhere
logging.info("This works perfectly!")
logging.error("Errors are automatically colored red")
logging.debug("Debug messages go to file by default")
```

## Installation

```bash
pip install rootlog-config
```

## Features

### Basic Usage

```python
from logger import setup_logger
import logging

# Minimal setup - uses sensible defaults
setup_logger()

# Logs to both console (colored) and file (rotated)
logging.info("Hello, world!")
```

### Script-based Logging

```python
# Automatically uses script name for log directory
setup_logger(script=__file__)

# Creates logs in ~/python-log/my_script/YYYYMMDD-HH.log
```

### Custom Configuration

```python
setup_logger(
    app="myapp",
    level_c=logging.WARNING,  # Console level
    level_f=logging.DEBUG,    # File level
    format_c="%(levelname)s: %(message)s",  # Console format
    log_c=True,   # Enable console logging
    log_f=True,   # Enable file logging
)
```

### Thread-Safe High Performance

```python
# For applications with many threads logging frequently
setup_logger(app="highperf", use_queue=True)

# All logging calls are now queued and handled by background thread
logging.info("Thread-safe logging!")
```

### Flexible Rotation

```python
# Size-based rotation
setup_logger(app="big", rotation="100 MB")
setup_logger(app="huge", rotation="1 GB")

# Time-based rotation
setup_logger(app="daily", rotation="1 day")
setup_logger(app="hourly", rotation="1 hour")
setup_logger(app="weekly", rotation="1 week")
setup_logger(app="midnight", rotation="00:00")
```

### Error Resilience

```python
# If file logging fails (permissions, disk full, etc.)
# automatically falls back to console logging with warning
setup_logger(app="robust")
logging.info("This works even on read-only filesystems!")
```

## How It Works

This utility follows Python logging best practices:

1. **Configure root logger once** at application startup
2. **Use standard logging calls** (`logging.info()`, etc.) everywhere
3. **No logger instances** to pass around or manage
4. **Automatic cleanup** prevents duplicate log messages
5. **Thread-safe by design** with optional queue support

### Multi-Module Usage

```python
# main.py
from logger import setup_logger
import logging
from mymodule import do_something

setup_logger(app="myapp")
logging.info("Application started")
do_something()

# mymodule.py
import logging

def do_something():
    logging.info("This automatically uses the configured logger!")
    logging.error("Errors are properly formatted and colored")
```

### Threading Example

```python
import threading
import time
from logger import setup_logger
import logging

setup_logger(app="threaded", use_queue=True)

def worker(name):
    for i in range(5):
        logging.info(f"Worker {name}: Processing item {i}")
        time.sleep(0.1)

# Start multiple threads - all logging is thread-safe
threads = []
for i in range(3):
    t = threading.Thread(target=worker, args=[f"Thread-{i}"])
    threads.append(t)
    t.start()

for t in threads:
    t.join()
```

## Configuration Options

### Parameters

- **script** (str): Path to script file, uses filename for log directory
- **app** (str): Application name for log directory
- **logger_name** (str): Specific logger name (None = root logger)
- **level_c** (int): Console logging level (default: INFO)
- **level_f** (int): File logging level (default: DEBUG)
- **format_c** (str): Console log format
- **format_f** (str): File log format
- **log_c** (bool): Enable console logging (default: True)
- **log_f** (bool): Enable file logging (default: True)
- **rotation** (str|int): Rotation config ("1 day", "100 MB", etc.)
- **use_queue** (bool): Enable queue-based thread-safe logging

### Log File Organization

Logs are automatically organized:
```
~/python-log/               # Default location (set PY_LOG_PATH to override)
├── myapp/                  # App-specific directory
│   ├── 20240315-14.log     # Hourly rotation (default)
│   ├── 20240315-15.log
│   └── ...
└── myscript/               # Script-based directory
    ├── 20240315-09.log
    └── ...
```

### Environment Variables

- **PY_LOG_PATH**: Override default log directory (default: `~/python-log`)
- **TESTING**: Set to "true" to append "-testing" to log filenames

## Comparison with Popular Libraries

| Feature | This Logger | Loguru | Structlog | Colorlog |
|---------|-------------|--------|-----------|----------|
| Setup Complexity | Low | Lowest | High | Medium |
| Root Logger Config | ✅ | ❌ | ✅ | ✅ |
| File Rotation | ✅ | ✅ | ❌ | ❌ |
| Thread Safety | ✅ | ✅ | ✅ | ✅ |
| Migration Cost | None | Medium | High | Low |
| File Organization | ✅ | ❌ | ❌ | ❌ |

## Requirements

- Python 3.8+
- colorlog >= 6.9.0

## Development

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest

# Type checking
poetry run mypy .

# Code formatting
pre-commit run --all-files
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please read our development guidelines in CLAUDE.md.

## Why Not Just Use Loguru?

Loguru is excellent, but:
- Creates its own logger instance (not root logger compatible)
- Requires migration of existing `logging.info()` calls
- Abstracts away Python logging concepts
- Less educational for learning proper logging patterns

This utility teaches and uses Python logging correctly while providing modern conveniences.

## Philosophy

> Configure once, log everywhere. Keep it simple, keep it standard.

This utility embraces Python's logging design rather than replacing it. Perfect for developers who want proper logging without complexity or vendor lock-in.
