"""Pytest configuration and fixtures for fdprof tests."""

import json
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_log_file():
    """Create a temporary log file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        log_file = f.name

    yield log_file

    # Clean up
    Path(log_file).unlink(missing_ok=True)


@pytest.fixture
def sample_fd_data():
    """Provide sample FD monitoring data."""
    return [
        {"timestamp": 1000.0, "elapsed": 0.0, "open_fds": 10},
        {"timestamp": 1000.1, "elapsed": 0.1, "open_fds": 10},
        {"timestamp": 1000.2, "elapsed": 0.2, "open_fds": 15},
        {"timestamp": 1000.3, "elapsed": 0.3, "open_fds": 15},
        {"timestamp": 1000.4, "elapsed": 0.4, "open_fds": 15},
        {"timestamp": 1000.5, "elapsed": 0.5, "open_fds": 20},
        {"timestamp": 1000.6, "elapsed": 0.6, "open_fds": 20},
        {"timestamp": 1000.7, "elapsed": 0.7, "open_fds": 20},
        {"timestamp": 1000.8, "elapsed": 0.8, "open_fds": 10},
        {"timestamp": 1000.9, "elapsed": 0.9, "open_fds": 10},
    ]


@pytest.fixture
def sample_events():
    """Provide sample event data."""
    return [
        {
            "type": "event",
            "elapsed": 0.1,
            "message": "Application started",
            "timestamp": 1000.1,
        },
        {
            "type": "event",
            "elapsed": 0.5,
            "message": "Database connected",
            "timestamp": 1000.5,
        },
        {
            "type": "event",
            "elapsed": 0.8,
            "message": "Processing complete",
            "timestamp": 1000.8,
        },
    ]


@pytest.fixture
def populated_log_file(temp_log_file, sample_fd_data):
    """Create a log file populated with sample FD data."""
    with open(temp_log_file, "w") as f:
        for data_point in sample_fd_data:
            f.write(json.dumps(data_point) + "\n")

    return temp_log_file


@pytest.fixture
def test_script():
    """Create a temporary test script for integration tests."""
    script_content = """#!/usr/bin/env python3
import time
import sys
import tempfile
import os

def log_event(message: str):
    print(f"EVENT: {time.time():.9f} {message}")

print("Test script starting")
log_event("Script initialized")

# Create some file descriptors
files = []
temp_dir = tempfile.gettempdir()
for i in range(3):
    try:
        temp_path = os.path.join(temp_dir, f"fdprof_test_script_{i}.txt")
        f = open(temp_path, "w")
        files.append(f)
        f.write(f"Test data {i}")
        log_event(f"Created file {i}")
    except:
        pass

time.sleep(0.1)

# Close files
for i, f in enumerate(files):
    try:
        f.close()
        log_event(f"Closed file {i}")
    except:
        pass

log_event("Script completed")
print("Test script finished")
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(script_content)
        script_path = f.name

    yield script_path

    # Clean up
    Path(script_path).unlink(missing_ok=True)
    # Clean up any test files created by the script
    temp_dir = tempfile.gettempdir()
    for i in range(3):
        temp_path = Path(temp_dir) / f"fdprof_test_script_{i}.txt"
        temp_path.unlink(missing_ok=True)


@pytest.fixture
def plateau_test_data():
    """Provide test data for plateau detection."""
    return {
        "simple_plateau": {
            "times": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
            "values": [100, 100, 100, 100, 100, 100],
        },
        "two_plateaus": {
            "times": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
            "values": [10, 10, 10, 10, 50, 50, 50, 50, 50, 50],
        },
        "noisy_plateau": {
            "times": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
            "values": [98, 101, 99, 102, 100, 99, 101, 100, 98, 102],
        },
        "step_function": {
            "times": list(range(15)),
            "values": [10] * 5 + [100] * 5 + [20] * 5,
        },
    }


@pytest.fixture(autouse=True)
def clean_up_log_files():
    """Automatically clean up any fdprof.jsonl files created during tests."""
    yield

    # Clean up after each test
    log_file = Path("fdprof.jsonl")
    log_file.unlink(missing_ok=True)


@pytest.fixture
def mock_subprocess_output():
    """Provide mock subprocess output with events."""
    return [
        "Starting application...",
        "EVENT: 1000.123456 Application initialized",
        "Loading configuration...",
        "EVENT: 1000.234567 Configuration loaded",
        "Processing data...",
        "EVENT: 1000.345678 Data processing started",
        "EVENT: 1000.456789 Data processing complete",
        "Application finished.",
    ]
