"""
File descriptor monitoring functionality.
"""

import json
import platform
import queue
import select
import subprocess
import threading
import time
from typing import Callable, List, Optional

import psutil


def _get_fd_counter(psutil_proc: psutil.Process) -> Callable[[], int]:
    """Determine the best FD counting method for the current platform."""
    # Try methods in order of efficiency
    try:
        psutil_proc.num_fds()
        return lambda: psutil_proc.num_fds()
    except AttributeError:
        try:
            psutil_proc.num_handles()
            return lambda: psutil_proc.num_handles()
        except AttributeError:
            return lambda: len(psutil_proc.open_files())


def _read_output_thread(
    pipe, output_queue: queue.Queue, stop_event: threading.Event
) -> None:
    """Thread to read output from subprocess pipe."""
    try:
        while not stop_event.is_set():
            line = pipe.readline()
            if line:
                output_queue.put(line)
            else:
                # End of stream
                break
    except (OSError, ValueError):
        # IOError/OSError: pipe closed or read error
        # ValueError: I/O operation on closed file
        pass


def capture_output_and_monitor_fds(
    proc: subprocess.Popen,
    psutil_proc: Optional[psutil.Process],
    log_file: str,
    start_time: float,
    interval: float = 0.1,
) -> List[str]:
    """Capture process output and monitor FD usage simultaneously."""
    output_lines = []

    # Determine the FD counting method once at startup
    get_fd_count = None
    if psutil_proc:
        try:
            get_fd_count = _get_fd_counter(psutil_proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
            get_fd_count = None

    # Set up platform-specific output capture
    is_windows = platform.system() == "Windows"
    output_queue = None
    stop_event = None
    reader_thread = None

    if is_windows:
        # Windows: Use threading for output capture
        output_queue = queue.Queue()
        stop_event = threading.Event()
        reader_thread = threading.Thread(
            target=_read_output_thread,
            args=(proc.stdout, output_queue, stop_event),
        )
        reader_thread.daemon = True
        reader_thread.start()

    with open(log_file, "w") as f:
        while proc.poll() is None:
            # Monitor FD usage
            try:
                current_time = time.time()
                if get_fd_count:
                    try:
                        fd_count = get_fd_count()
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        fd_count = -1
                else:
                    fd_count = -1

                fd_data = {
                    "timestamp": current_time,
                    "elapsed": current_time - start_time,
                    "open_fds": fd_count,
                }

                f.write(json.dumps(fd_data) + "\n")
                f.flush()
            except (OSError, json.JSONEncodeError):
                # OSError: file write error
                # JSONEncodeError: shouldn't happen with our controlled data
                pass

            # Capture output
            if is_windows:
                # Windows: Read from queue
                try:
                    line = output_queue.get(timeout=interval)
                    if line:
                        line_stripped = line.strip()
                        output_lines.append(line_stripped)
                        print(line_stripped, flush=True)
                except queue.Empty:
                    pass
                except (OSError, UnicodeDecodeError):
                    # IOError/OSError: stdout write error
                    # UnicodeDecodeError: non-UTF8 output from subprocess
                    pass
            else:
                # Unix: Use select
                try:
                    ready, _, _ = select.select([proc.stdout], [], [], interval)
                    if ready:
                        line = proc.stdout.readline()
                        if line:
                            line_stripped = line.strip()
                            output_lines.append(line_stripped)
                            print(line_stripped, flush=True)
                except (OSError, ValueError, UnicodeDecodeError):
                    # IOError/OSError: pipe/stdout error
                    # ValueError: file descriptor out of range in select()
                    # select.error: interrupted system call or invalid file descriptor
                    # UnicodeDecodeError: non-UTF8 output from subprocess
                    pass

    # Clean up Windows thread
    if is_windows and reader_thread:
        stop_event.set()
        reader_thread.join(timeout=1)

    # Capture any remaining output
    remaining = proc.stdout.read()
    if remaining:
        for line in remaining.strip().split("\n"):
            if line:
                output_lines.append(line)
                print(line, flush=True)

    return output_lines
