"""Integration tests for fdprof CLI functionality."""

import json
import subprocess
import tempfile
from pathlib import Path


class TestCLIIntegration:
    """Test CLI integration and end-to-end functionality."""

    def test_cli_basic_command(self):
        """Test basic CLI command execution."""
        result = subprocess.run(
            ["uv", "run", "fdprof", "python", "-c", "print('hello world')"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0
        assert "hello world" in result.stdout
        assert "Command completed with exit code: 0" in result.stdout

    def test_cli_with_events(self):
        """Test CLI with a script that generates events."""
        # Create a temporary script that generates events
        script_content = """
import time
import sys

def log_event(message):
    print(f"EVENT: {time.time():.9f} {message}")

print("Script starting")
log_event("Script initialized")
time.sleep(0.1)
log_event("Processing complete")
print("Script finished")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(script_content)
            script_path = f.name

        try:
            result = subprocess.run(
                ["uv", "run", "fdprof", "python", script_path],
                capture_output=True,
                text=True,
                timeout=10,
            )

            assert result.returncode == 0
            assert "Script starting" in result.stdout
            assert "Script finished" in result.stdout
            assert "Found 2 events" in result.stdout
            assert "Event Timeline:" in result.stdout
            assert "Script initialized" in result.stdout
            assert "Processing complete" in result.stdout

        finally:
            Path(script_path).unlink(missing_ok=True)

    def test_cli_interval_option(self):
        """Test CLI with custom interval option."""
        result = subprocess.run(
            [
                "uv",
                "run",
                "fdprof",
                "--interval",
                "0.2",
                "python",
                "-c",
                "print('test')",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0
        assert "Sampling interval: 0.2s" in result.stdout

    def test_cli_creates_log_file(self):
        """Test that CLI creates the expected log file."""
        # Clean up any existing log file
        log_file = Path("fdprof.jsonl")
        log_file.unlink(missing_ok=True)

        result = subprocess.run(
            ["uv", "run", "fdprof", "python", "-c", "import time; time.sleep(0.2)"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0
        assert log_file.exists()

        # Verify log file contains JSON data
        with open(log_file) as f:
            lines = f.readlines()
            assert len(lines) > 0

            # Each line should be valid JSON
            for line in lines:
                if line.strip():
                    data = json.loads(line)
                    assert "timestamp" in data
                    assert "elapsed" in data
                    assert "open_fds" in data

        # Clean up
        log_file.unlink(missing_ok=True)

    def test_cli_invalid_command(self):
        """Test CLI behavior with invalid command."""
        result = subprocess.run(
            ["uv", "run", "fdprof", "nonexistent_command_xyz"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        # Should fail but fdprof itself should handle it gracefully
        assert result.returncode != 0

    def test_cli_command_with_arguments(self):
        """Test CLI with command that has multiple arguments."""
        result = subprocess.run(
            ["uv", "run", "fdprof", "python", "-c", "print('hello'); print('world')"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0
        assert "hello" in result.stdout
        assert "world" in result.stdout

    def test_cli_help_output(self):
        """Test CLI help/usage output."""
        result = subprocess.run(
            ["uv", "run", "fdprof"], capture_output=True, text=True, timeout=10
        )

        # Should exit with error (no command) and show usage
        assert result.returncode == 1
        assert "Usage:" in result.stdout or "usage:" in result.stdout.lower()

    def test_cli_invalid_interval(self):
        """Test CLI with invalid interval values."""
        # Negative interval
        result = subprocess.run(
            [
                "uv",
                "run",
                "fdprof",
                "--interval",
                "-0.1",
                "python",
                "-c",
                "print('test')",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 1

        # Non-numeric interval
        result = subprocess.run(
            [
                "uv",
                "run",
                "fdprof",
                "--interval",
                "abc",
                "python",
                "-c",
                "print('test')",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 1

    def test_cli_with_failing_command(self):
        """Test CLI with a command that fails."""
        result = subprocess.run(
            ["uv", "run", "fdprof", "python", "-c", "import sys; sys.exit(42)"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        # fdprof should complete successfully even if monitored command fails
        assert result.returncode == 0
        assert "Command completed with exit code: 42" in result.stdout

    def test_cli_fd_monitoring(self):
        """Test that CLI actually monitors file descriptors."""
        # Create a script that opens and closes files
        script_content = """
import time
import tempfile
import os

# Open some files to increase FD count
files = []
temp_dir = tempfile.gettempdir()
for i in range(3):
    temp_path = os.path.join(temp_dir, f"fdprof_test_{i}.txt")
    f = open(temp_path, "w")
    files.append(f)
    f.write(f"test content {i}")

time.sleep(0.2)  # Give time for monitoring

# Close files
for f in files:
    f.close()

print("FD test completed")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(script_content)
            script_path = f.name

        try:
            # Clean up any existing log file
            log_file = Path("fdprof.jsonl")
            log_file.unlink(missing_ok=True)

            result = subprocess.run(
                ["uv", "run", "fdprof", "python", script_path],
                capture_output=True,
                text=True,
                timeout=10,
            )

            assert result.returncode == 0
            assert "FD test completed" in result.stdout

            # Verify that FD data was collected
            assert log_file.exists()
            with open(log_file) as f:
                lines = f.readlines()
                assert len(lines) > 0

                # Should have multiple data points
                data_points = [json.loads(line) for line in lines if line.strip()]
                assert len(data_points) > 1

                # Should have valid FD counts (>= 0)
                fd_counts = [
                    dp["open_fds"] for dp in data_points if dp["open_fds"] >= 0
                ]
                assert len(fd_counts) > 0

            # Clean up log file
            log_file.unlink(missing_ok=True)

        finally:
            Path(script_path).unlink(missing_ok=True)
            # Clean up test files
            temp_dir = tempfile.gettempdir()
            for i in range(3):
                temp_path = Path(temp_dir) / f"fdprof_test_{i}.txt"
                temp_path.unlink(missing_ok=True)
