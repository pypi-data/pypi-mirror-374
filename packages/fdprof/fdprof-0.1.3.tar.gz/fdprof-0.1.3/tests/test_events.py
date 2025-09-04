"""Tests for event parsing functionality."""

from fdprof.events import _is_timestamp, parse_events


class TestEventParsing:
    """Test event parsing functionality."""

    def test_parse_events_empty_output(self):
        """Test parsing empty output lines."""
        events = parse_events([], 1000.0)
        assert events == []

    def test_parse_events_no_events(self):
        """Test parsing output with no EVENT lines."""
        output_lines = [
            "Starting application",
            "Processing data",
            "Application finished",
        ]
        events = parse_events(output_lines, 1000.0)
        assert events == []

    def test_parse_events_single_event(self):
        """Test parsing a single valid event."""
        start_time = 1000.0
        output_lines = ["EVENT: 1001.5 Database connected"]
        events = parse_events(output_lines, start_time)

        assert len(events) == 1
        event = events[0]
        assert event["type"] == "event"
        assert event["message"] == "Database connected"
        assert event["timestamp"] == 1001.5
        assert event["elapsed"] == 1.5

    def test_parse_events_multiple_events(self):
        """Test parsing multiple events."""
        start_time = 1000.0
        output_lines = [
            "Starting application",
            "EVENT: 1001.0 Application started",
            "Processing data",
            "EVENT: 1002.5 Data loaded",
            "EVENT: 1003.0 Processing complete",
            "Application finished",
        ]
        events = parse_events(output_lines, start_time)

        assert len(events) == 3

        assert events[0]["message"] == "Application started"
        assert events[0]["elapsed"] == 1.0

        assert events[1]["message"] == "Data loaded"
        assert events[1]["elapsed"] == 2.5

        assert events[2]["message"] == "Processing complete"
        assert events[2]["elapsed"] == 3.0

    def test_parse_events_with_high_precision_timestamps(self):
        """Test parsing events with high-precision timestamps."""
        start_time = 1000.0
        output_lines = ["EVENT: 1001.123456789 High precision event"]
        events = parse_events(output_lines, start_time)

        assert len(events) == 1
        assert events[0]["timestamp"] == 1001.123456789
        # Use approximate comparison for floating point precision
        assert abs(events[0]["elapsed"] - 1.123456789) < 1e-6

    def test_parse_events_invalid_timestamp(self):
        """Test parsing events with invalid timestamps."""
        start_time = 1000.0
        output_lines = [
            "EVENT: invalid_timestamp Some event",
            "EVENT: 1001.5 Valid event",
        ]
        events = parse_events(output_lines, start_time)

        # Should only parse the valid event
        assert len(events) == 1
        assert events[0]["message"] == "Valid event"

    def test_parse_events_missing_message(self):
        """Test parsing events with missing message."""
        start_time = 1000.0
        output_lines = ["EVENT: 1001.5"]
        events = parse_events(output_lines, start_time)

        # Should not parse events without messages
        assert len(events) == 0

    def test_parse_events_multiword_message(self):
        """Test parsing events with multi-word messages."""
        start_time = 1000.0
        output_lines = ["EVENT: 1001.5 This is a multi-word event message"]
        events = parse_events(output_lines, start_time)

        assert len(events) == 1
        assert events[0]["message"] == "This is a multi-word event message"


class TestTimestampValidation:
    """Test timestamp validation functionality."""

    def test_is_timestamp_valid_integer(self):
        """Test valid integer timestamp."""
        assert _is_timestamp("1234567890")

    def test_is_timestamp_valid_float(self):
        """Test valid float timestamp."""
        assert _is_timestamp("1234567890.123456")

    def test_is_timestamp_invalid_multiple_dots(self):
        """Test invalid timestamp with multiple dots."""
        assert not _is_timestamp("123.456.789")

    def test_is_timestamp_invalid_letters(self):
        """Test invalid timestamp with letters."""
        assert not _is_timestamp("123abc456")

    def test_is_timestamp_empty_string(self):
        """Test invalid empty timestamp."""
        assert not _is_timestamp("")

    def test_is_timestamp_only_dot(self):
        """Test invalid timestamp with only dot."""
        assert not _is_timestamp(".")

    def test_is_timestamp_dot_at_end(self):
        """Test valid timestamp with dot at end."""
        assert _is_timestamp("123456.")

    def test_is_timestamp_dot_at_start(self):
        """Test valid timestamp with dot at start."""
        assert _is_timestamp(".123456")
