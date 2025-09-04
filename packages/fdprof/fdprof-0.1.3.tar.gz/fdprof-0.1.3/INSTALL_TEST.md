# Installation Testing Guide

This document provides step-by-step instructions for testing fdprof installation methods.

## Prerequisites

- Python 3.8+
- uv installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

## Installation Methods

### Method 1: uv tool install (from PyPI - once published)

```bash
# Install from PyPI
uv tool install fdprof

# Verify installation
fdprof --help
fdprof echo "Test PyPI installation"

# Uninstall for testing other methods
uv tool uninstall fdprof
```

### Method 2: uv tool install (from GitHub)

```bash
# Install from GitHub repository
uv tool install git+https://github.com/ianhi/fdprof

# Verify installation
fdprof --help
fdprof echo "Test GitHub installation"

# Test with plotting (requires GUI)
fdprof --plot echo "Test plotting"

# Uninstall
uv tool uninstall fdprof
```

### Method 3: uvx (temporary execution)

```bash
# Run directly without installation
uvx --from git+https://github.com/ianhi/fdprof fdprof echo "Test uvx"

# With options
uvx --from git+https://github.com/ianhi/fdprof fdprof --interval 0.2 echo "Test options"
```

### Method 4: pip install (traditional)

```bash
# Create virtual environment
python -m venv test-fdprof
source test-fdprof/bin/activate  # or test-fdprof\Scripts\activate on Windows

# Install from PyPI (once published)
pip install fdprof

# Or from GitHub
pip install git+https://github.com/ianhi/fdprof

# Verify
fdprof --help
fdprof echo "Test pip installation"

# Cleanup
deactivate
rm -rf test-fdprof
```

### Method 5: Development install

```bash
# Clone repository
git clone https://github.com/ianhi/fdprof
cd fdprof

# Install development dependencies
uv sync --extra dev

# Run in development mode
uv run fdprof --help
uv run fdprof echo "Test development"

# Run tests
uv run pytest

# Clean up
cd ..
rm -rf fdprof
```

## Comprehensive Test Script

Create a test script that validates all functionality:

```python
#!/usr/bin/env python3
"""Test script for fdprof installation."""

import subprocess
import time
import tempfile
import os

def log_event(message):
    print(f"EVENT: {time.time():.9f} {message}")

def test_fdprof():
    print("Testing fdprof functionality...")
    log_event("Test script started")

    # Open some file descriptors
    files = []
    for i in range(3):
        f = tempfile.NamedTemporaryFile(mode='w', delete=False)
        f.write(f"Test data {i}")
        f.flush()
        files.append(f)
        log_event(f"Opened file {i}: {f.name}")

    time.sleep(0.5)
    log_event("Processing data")

    # Close files
    for i, f in enumerate(files):
        f.close()
        os.unlink(f.name)
        log_event(f"Closed and deleted file {i}")

    log_event("Test script completed")
    print("Test script finished successfully!")

if __name__ == "__main__":
    test_fdprof()
```

Save as `test_fdprof.py` and run:

```bash
# Test basic functionality
fdprof python test_fdprof.py

# Test with plotting
fdprof --plot python test_fdprof.py

# Test with custom interval
fdprof --interval 0.05 --plot python test_fdprof.py
```

## Expected Output

### Console Output
```
Command: python test_fdprof.py
Logging to: fdprof.jsonl
Sampling interval: 0.1s
----------------------------------------
Testing fdprof functionality...
EVENT: 1234567890.123 Test script started
EVENT: 1234567890.234 Opened file 0: /tmp/tmp123456
EVENT: 1234567890.245 Opened file 1: /tmp/tmp789012
EVENT: 1234567890.256 Opened file 2: /tmp/tmp345678
EVENT: 1234567890.767 Processing data
EVENT: 1234567890.778 Closed and deleted file 0
EVENT: 1234567890.789 Closed and deleted file 1
EVENT: 1234567890.801 Closed and deleted file 2
EVENT: 1234567890.812 Test script completed
Test script finished successfully!
----------------------------------------
Command completed with exit code: 0
Found 8 events

Event Timeline:
    0.02s: Test script started
    0.13s: Opened file 0: /tmp/tmp123456
    ...
```

### Generated Files
- `fdprof.jsonl` - JSON logs with FD data
- Interactive plot (if `--plot` used)

## Troubleshooting

### Common Issues

1. **"fdprof: command not found"**
   - Ensure `~/.local/bin` is in your PATH
   - Run `uv tool update-shell` to update shell configuration

2. **"No module named 'psutil'"**
   - Dependencies not installed correctly
   - Try `uv tool install --force fdprof`

3. **Plot not showing**
   - GUI backend not available
   - Install: `pip install matplotlib[gui]`
   - Set backend: `export MPLBACKEND=TkAgg`

4. **Permission denied errors**
   - Some systems need elevated privileges for FD monitoring
   - Try: `sudo fdprof ...`

### Verification Checklist

- [ ] `fdprof --help` shows usage information
- [ ] `fdprof echo "test"` runs successfully
- [ ] Events are captured and displayed
- [ ] `fdprof.jsonl` file is created
- [ ] FD counts are monitored (> 0 values)
- [ ] Exit code is reported correctly
- [ ] `--plot` option shows interactive graph (if GUI available)
- [ ] Custom `--interval` values work
- [ ] Tool can be uninstalled cleanly

## Platform Notes

- **Linux**: Full support, all features work
- **macOS**: Full support, may need GUI setup for plotting
- **Windows**: Limited support (FD monitoring may not work)

## Performance Notes

- Default sampling interval: 0.1 seconds
- Minimum recommended interval: 0.01 seconds
- Memory usage: ~10MB + matplotlib (if plotting)
- CPU overhead: Minimal (<1% for typical usage)
