# Pyfault

A Python package that provides automatic exception handling and crash reporting
to the Memfault platform.

## Overview

This package installs a custom exception handler that captures unhandled Python
exceptions and sends them to `memfaultd`, the Memfault Linux observability agent
for IOT devices, for crash analysis and debugging.

## Features

- **Automatic Exception Handling**: Captures all unhandled exceptions in your
  Python application
- **Rich Traceback Data**: Collects detailed traceback information including
  local variables (filtered to safe types)
- **Non-blocking**: Exception reporting doesn't interfere with normal exception
  handling

## Installation

```bash
pip install pyfault
```

## Usage

```python
import pyfault

# Initialize with default memfaultd settings (connects to 127.0.0.1:8787)
pyfault.init()

# Or specify a custom memfaultd host
pyfault.init(host="your-memfaultd-host:port")
```

Once initialized, any unhandled exception in your application will automatically
be reported to Memfault while still allowing the normal exception handling to
proceed.

## How it Works

The package works by:

1. Installing a custom `sys.excepthook` that intercepts unhandled exceptions
2. Extracting traceback information using `tblib` with safe local variable
   capture
3. Packaging the exception data with metadata (Python version, program name,
   etc.)
4. Sending the data to the Memfault daemon via HTTP POST to `/v1/trace/save`
5. Calling the original exception handler to maintain normal Python behavior

## Data Collected

The following information is sent to Memfault:

- **Traceback**: Complete stack trace with filtered local variables
- **Python Version**: Runtime Python version
- **Exception Type**: The type of exception that occurred
- **Program Name**: Name of the file where the exception originated

## Safety

Local variables are filtered to only include safe primitive types (str, int,
float, bool, None) to avoid serialization issues and potential sensitive data
exposure.
