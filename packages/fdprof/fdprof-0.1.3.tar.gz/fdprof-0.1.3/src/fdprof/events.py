"""
Event parsing functionality for fdprof.
"""

from typing import Any, Dict, List


def parse_events(output_lines: List[str], start_time: float) -> List[Dict[str, Any]]:
    """Parse EVENT messages with timestamps from output."""
    events = []

    for line in output_lines:
        if not line.startswith("EVENT:"):
            continue

        # Parse format: "EVENT: 1234567890.123456 message"
        content = line[6:].strip()  # Remove "EVENT:" prefix
        parts = content.split(" ", 1)

        if len(parts) >= 2 and _is_timestamp(parts[0]):
            try:
                event_timestamp = float(parts[0])
                event_message = parts[1]
                event_elapsed = event_timestamp - start_time

                events.append(
                    {
                        "type": "event",
                        "elapsed": event_elapsed,
                        "message": event_message,
                        "timestamp": event_timestamp,
                    }
                )
            except ValueError:
                continue

    return events


def _is_timestamp(text: str) -> bool:
    """Check if text looks like a timestamp (digits and at most one dot)."""
    return text.replace(".", "").isdigit() and text.count(".") <= 1
