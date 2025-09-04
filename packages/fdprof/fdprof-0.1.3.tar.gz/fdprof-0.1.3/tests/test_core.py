"""Tests for core functionality and CLI argument parsing."""

import sys
from unittest.mock import patch

import pytest
from fdprof.core import parse_args, print_summary


class TestArgumentParsing:
    """Test command line argument parsing."""

    def test_parse_args_basic_command(self):
        """Test parsing basic command without options."""
        with patch.object(sys, "argv", ["fdprof", "echo", "hello"]):
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
            assert show_plot is False
            assert save_plot == ""
            assert interval == 0.1
            assert merge_threshold == 5.0
            assert min_length == 5
            assert tolerance == 2.0
            assert jump_threshold == 2.0
            assert command == ["echo", "hello"]

    def test_parse_args_with_plot_option(self):
        """Test parsing with --plot option."""
        with patch.object(sys, "argv", ["fdprof", "--plot", "python", "script.py"]):
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
            assert show_plot is True
            assert save_plot == ""
            assert interval == 0.1
            assert command == ["python", "script.py"]

    def test_parse_args_with_interval_option(self):
        """Test parsing with --interval option."""
        with patch.object(sys, "argv", ["fdprof", "--interval", "0.5", "sleep", "1"]):
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
            assert show_plot is False
            assert interval == 0.5
            assert command == ["sleep", "1"]

    def test_parse_args_with_both_options(self):
        """Test parsing with both --plot and --interval options."""
        with patch.object(
            sys, "argv", ["fdprof", "--plot", "--interval", "0.2", "ls", "-la"]
        ):
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
            assert show_plot is True
            assert interval == 0.2
            assert command == ["ls", "-la"]

    def test_parse_args_options_order_independence(self):
        """Test that option order doesn't matter."""
        with patch.object(
            sys, "argv", ["fdprof", "--interval", "0.3", "--plot", "pwd"]
        ):
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
            assert show_plot is True
            assert interval == 0.3
            assert command == ["pwd"]

    def test_parse_args_no_command_exit(self):
        """Test that missing command causes exit."""
        with patch.object(sys, "argv", ["fdprof"]):
            with pytest.raises(SystemExit):
                parse_args()

    def test_parse_args_only_options_no_command_exit(self):
        """Test that options without command causes exit."""
        with patch.object(sys, "argv", ["fdprof", "--plot", "--interval", "0.5"]):
            with pytest.raises(SystemExit):
                parse_args()

    def test_parse_args_invalid_interval_negative(self):
        """Test that negative interval causes exit."""
        with patch.object(
            sys, "argv", ["fdprof", "--interval", "-0.1", "echo", "test"]
        ):
            with pytest.raises(SystemExit):
                parse_args()

    def test_parse_args_invalid_interval_zero(self):
        """Test that zero interval causes exit."""
        with patch.object(sys, "argv", ["fdprof", "--interval", "0", "echo", "test"]):
            with pytest.raises(SystemExit):
                parse_args()

    def test_parse_args_invalid_interval_non_numeric(self):
        """Test that non-numeric interval causes exit."""
        with patch.object(sys, "argv", ["fdprof", "--interval", "abc", "echo", "test"]):
            with pytest.raises(SystemExit):
                parse_args()

    def test_parse_args_interval_missing_value(self):
        """Test that --interval without value causes exit."""
        with patch.object(sys, "argv", ["fdprof", "--interval"]):
            with pytest.raises(SystemExit):
                parse_args()

    def test_parse_args_unknown_option(self):
        """Test that unknown option causes exit."""
        with patch.object(sys, "argv", ["fdprof", "--unknown", "echo", "test"]):
            with pytest.raises(SystemExit):
                parse_args()

    def test_parse_args_command_with_arguments(self):
        """Test parsing command with multiple arguments."""
        with patch.object(
            sys, "argv", ["fdprof", "python", "-c", 'print("hello world")']
        ):
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
            assert command == ["python", "-c", 'print("hello world")']

    def test_parse_args_complex_command(self):
        """Test parsing complex command with options and arguments."""
        with patch.object(
            sys,
            "argv",
            [
                "fdprof",
                "--plot",
                "--interval",
                "0.05",
                "python",
                "-u",
                "test.py",
                "--verbose",
            ],
        ):
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
            assert show_plot is True
            assert interval == 0.05
            assert command == ["python", "-u", "test.py", "--verbose"]


class TestPrintSummary:
    """Test summary printing functionality."""

    def test_print_summary_no_events(self, capsys):
        """Test printing summary with no events."""
        events = []
        return_code = 0

        print_summary(events, return_code)

        captured = capsys.readouterr()
        assert "Command completed with exit code: 0" in captured.out
        assert "Found 0 events" in captured.out
        assert "Event Timeline:" not in captured.out

    def test_print_summary_with_events(self, capsys):
        """Test printing summary with events."""
        events = [
            {"elapsed": 0.5, "message": "First event"},
            {"elapsed": 1.2, "message": "Second event"},
            {"elapsed": 2.1, "message": "Third event"},
        ]
        return_code = 0

        print_summary(events, return_code)

        captured = capsys.readouterr()
        assert "Command completed with exit code: 0" in captured.out
        assert "Found 3 events" in captured.out
        assert "Event Timeline:" in captured.out
        assert "0.50s: First event" in captured.out
        assert "1.20s: Second event" in captured.out
        assert "2.10s: Third event" in captured.out

    def test_print_summary_non_zero_exit_code(self, capsys):
        """Test printing summary with non-zero exit code."""
        events = []
        return_code = 1

        print_summary(events, return_code)

        captured = capsys.readouterr()
        assert "Command completed with exit code: 1" in captured.out

    def test_print_summary_event_formatting(self, capsys):
        """Test that event times are properly formatted."""
        events = [
            {"elapsed": 0.123456, "message": "Precise timing"},
            {"elapsed": 10.0, "message": "Round number"},
            {"elapsed": 123.789, "message": "Large number"},
        ]
        return_code = 0

        print_summary(events, return_code)

        captured = capsys.readouterr()
        # Check that times are formatted to 2 decimal places
        assert "0.12s:" in captured.out
        assert "10.00s:" in captured.out
        assert "123.79s:" in captured.out
