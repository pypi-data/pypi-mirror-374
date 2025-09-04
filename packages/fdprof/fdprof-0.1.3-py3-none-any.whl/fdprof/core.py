#!/usr/bin/env python3
"""
File descriptor profiler that monitors FD usage and captures timestamped events.

Usage: fdprof [OPTIONS] <command> [args...]

Options:
    --plot                      Show plot after command completes
    --save FILENAME             Save plot to file instead of showing (supports PNG, PDF, SVG)
    --interval SECONDS          Sampling interval in seconds (default: 0.1)
    --merge-threshold FLOAT     Merge plateaus within this FD difference (default: 5.0)
    --min-length INT           Minimum points for plateau detection (default: 5)
    --tolerance FLOAT          Stability tolerance for plateaus (default: 2.0)
    --jump-threshold FLOAT     Minimum jump size to display on plot (default: 2.0)

Examples:
    # Basic monitoring
    fdprof python script.py

    # With plot using demo-sensitive parameters (default)
    fdprof --plot fdprof-demo

    # Save plot to file for documentation
    fdprof --save fdprof_demo.png fdprof-demo

    # High sensitivity for small changes
    fdprof --plot --merge-threshold 2.0 --tolerance 1.0 --jump-threshold 1.0 fdprof-demo

    # Low sensitivity for large applications
    fdprof --plot --merge-threshold 50.0 --min-length 20 --jump-threshold 10.0 myapp

In your code, use a log_event function like:
    def log_event(message: str):
        print(f"EVENT: {time.time():.9f} {message}")
"""

import os
import subprocess
import sys
import time
from typing import Any, Dict, List

import psutil

from .events import parse_events
from .monitoring import capture_output_and_monitor_fds
from .plotting import create_plot

# Default configuration constants
DEFAULT_INTERVAL = 0.1
DEFAULT_MERGE_THRESHOLD = 5.0
DEFAULT_MIN_LENGTH = 5
DEFAULT_TOLERANCE = 2.0
DEFAULT_JUMP_THRESHOLD = 2.0


def parse_args() -> tuple[bool, str, float, float, int, float, float, List[str]]:
    """Parse command line arguments."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    show_plot = False
    save_plot = ""  # Empty string means don't save, otherwise filename
    interval = DEFAULT_INTERVAL
    merge_threshold = DEFAULT_MERGE_THRESHOLD
    min_length = DEFAULT_MIN_LENGTH
    tolerance = DEFAULT_TOLERANCE
    jump_threshold = DEFAULT_JUMP_THRESHOLD
    i = 1

    # Parse options
    while i < len(sys.argv) and sys.argv[i].startswith("--"):
        if sys.argv[i] == "--plot":
            show_plot = True
            i += 1
        elif sys.argv[i] == "--save":
            if i + 1 >= len(sys.argv):
                print("Error: --save requires a filename")
                sys.exit(1)
            save_plot = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--interval":
            if i + 1 >= len(sys.argv):
                print("Error: --interval requires a value")
                sys.exit(1)
            try:
                interval = float(sys.argv[i + 1])
                if interval <= 0:
                    print("Error: interval must be positive")
                    sys.exit(1)
            except ValueError:
                print("Error: interval must be a number")
                sys.exit(1)
            i += 2
        elif sys.argv[i] == "--merge-threshold":
            if i + 1 >= len(sys.argv):
                print("Error: --merge-threshold requires a value")
                sys.exit(1)
            try:
                merge_threshold = float(sys.argv[i + 1])
                if merge_threshold < 0:
                    print("Error: merge-threshold must be non-negative")
                    sys.exit(1)
            except ValueError:
                print("Error: merge-threshold must be a number")
                sys.exit(1)
            i += 2
        elif sys.argv[i] == "--min-length":
            if i + 1 >= len(sys.argv):
                print("Error: --min-length requires a value")
                sys.exit(1)
            try:
                min_length = int(sys.argv[i + 1])
                if min_length <= 0:
                    print("Error: min-length must be positive")
                    sys.exit(1)
            except ValueError:
                print("Error: min-length must be an integer")
                sys.exit(1)
            i += 2
        elif sys.argv[i] == "--tolerance":
            if i + 1 >= len(sys.argv):
                print("Error: --tolerance requires a value")
                sys.exit(1)
            try:
                tolerance = float(sys.argv[i + 1])
                if tolerance < 0:
                    print("Error: tolerance must be non-negative")
                    sys.exit(1)
            except ValueError:
                print("Error: tolerance must be a number")
                sys.exit(1)
            i += 2
        elif sys.argv[i] == "--jump-threshold":
            if i + 1 >= len(sys.argv):
                print("Error: --jump-threshold requires a value")
                sys.exit(1)
            try:
                jump_threshold = float(sys.argv[i + 1])
                if jump_threshold < 0:
                    print("Error: jump-threshold must be non-negative")
                    sys.exit(1)
            except ValueError:
                print("Error: jump-threshold must be a number")
                sys.exit(1)
            i += 2
        elif sys.argv[i] in ("--help", "-h"):
            print(__doc__)
            sys.exit(0)
        else:
            print(f"Error: unknown option {sys.argv[i]}")
            sys.exit(1)

    command = sys.argv[i:]
    if not command:
        print("Error: No command specified")
        sys.exit(1)

    return (
        show_plot,
        save_plot,
        interval,
        merge_threshold,
        min_length,
        tolerance,
        jump_threshold,
        command,
    )


def print_summary(events: List[Dict[str, Any]], return_code: int) -> None:
    """Print execution summary."""
    print("-" * 40)
    print(f"Command completed with exit code: {return_code}")
    print(f"Found {len(events)} events")

    if events:
        print("\nEvent Timeline:")
        for event in events:
            print(f"  {event['elapsed']:6.2f}s: {event['message']}")


def main() -> None:
    """Main execution function."""
    (
        show_plot,
        save_plot,
        interval,
        merge_threshold,
        min_length,
        tolerance,
        jump_threshold,
        command,
    ) = parse_args()
    log_file = "fdprof.jsonl"

    print(f"Command: {' '.join(command)}")
    print(f"Logging to: {log_file}")
    print(f"Sampling interval: {interval}s")
    print("-" * 40)

    # Start the process with unbuffered output
    env = os.environ.copy()
    # Force unbuffered output for Python processes
    env["PYTHONUNBUFFERED"] = "1"

    proc = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env
    )

    # Get psutil process handle
    try:
        psutil_proc = psutil.Process(proc.pid)
    except (psutil.NoSuchProcess, psutil.AccessDenied, OSError):
        print("Warning: Could not access process for monitoring")
        psutil_proc = None

    start_time = time.time()

    # Capture output and monitor FDs simultaneously
    output_lines = capture_output_and_monitor_fds(
        proc, psutil_proc, log_file, start_time, interval
    )

    # Wait for process completion
    return_code = proc.wait()

    # Parse events from captured output
    events = parse_events(output_lines, start_time)

    # Print summary
    print_summary(events, return_code)

    # Create plot if requested
    if show_plot or save_plot:
        create_plot(
            log_file,
            events,
            merge_threshold,
            min_length,
            tolerance,
            jump_threshold,
            save_plot,
        )


if __name__ == "__main__":
    main()
