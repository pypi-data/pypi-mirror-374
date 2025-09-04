"""
Plateau detection and analysis functionality.
"""

from typing import Any, Dict, List

import numpy as np

# Analysis constants
SLIDING_WINDOW_SIZE = 5
MAX_TRANSITION_LENGTH = 20


def detect_plateaus(
    times: List[float],
    values: List[int],
    min_length: int = 5,
    tolerance: float = 5.0,
    merge_close_levels: bool = True,
    merge_threshold: float = 15.0,
) -> List[Dict[str, Any]]:
    """Detect stable plateaus in FD usage, merging gradual transitions.

    Args:
        times: Time points
        values: FD count values
        min_length: Minimum number of points to consider a plateau
        tolerance: Maximum variance to consider values as stable
        merge_close_levels: Whether to merge plateaus with similar levels
        merge_threshold: Level difference below which plateaus are merged

    Returns:
        List of plateau dictionaries with level, start/end times
    """
    if len(values) < min_length:
        return []

    # First pass: identify stable regions
    stable_regions = []
    i = 0

    while i < len(values):
        # Look for a stable region
        j = i + 1
        region_vals = [values[i]]
        region_times = [times[i]]

        # Extend region while values are similar to recent mean
        recent_mean = values[i]  # Initialize with first value
        while j < len(values):
            # Use a sliding window mean for comparison (more efficient)
            window_size = min(SLIDING_WINDOW_SIZE, len(region_vals))
            if len(region_vals) >= window_size:
                recent_mean = np.mean(region_vals[-window_size:])

            if abs(values[j] - recent_mean) <= tolerance:
                region_vals.append(values[j])
                region_times.append(times[j])
                j += 1
            else:
                break

        # If we found a stable region
        if len(region_vals) >= min_length:
            stable_regions.append(
                {
                    "level": np.median(region_vals),
                    "start_time": region_times[0],
                    "end_time": region_times[-1],
                    "start_idx": i,
                    "end_idx": j - 1,
                    "variance": np.var(region_vals),
                    "values": region_vals,
                }
            )
            i = j
        else:
            i += 1

    # Second pass: merge transition zones
    # If there's a gap between stable regions, check if it's a transition
    plateaus = []
    i = 0

    while i < len(stable_regions):
        current = stable_regions[i]

        # Check if next region exists and there's a gap
        if i + 1 < len(stable_regions):
            next_region = stable_regions[i + 1]
            gap_start = current["end_idx"] + 1
            gap_end = next_region["start_idx"] - 1

            # If there's a transition zone between plateaus
            if (
                gap_end >= gap_start and gap_end - gap_start < MAX_TRANSITION_LENGTH
            ):  # Transition shouldn't be too long
                # This is likely a transition, not a plateau
                # Just add the current plateau
                plateaus.append(current)
            else:
                # Large gap might be another plateau
                plateaus.append(current)
        else:
            plateaus.append(current)

        i += 1

    # Final pass: merge very close plateaus if requested
    if merge_close_levels and len(plateaus) > 1:
        merged_plateaus = []
        i = 0

        while i < len(plateaus):
            current = plateaus[i]
            merged_with_next = False

            # Look ahead to find all plateaus that should be merged
            j = i + 1
            while j < len(plateaus):
                next_plateau = plateaus[j]
                level_diff = abs(current["level"] - next_plateau["level"])

                # Check if they should be merged
                if level_diff < merge_threshold:
                    # Merge plateaus
                    if "values" in current and "values" in next_plateau:
                        all_vals = current["values"] + next_plateau["values"]
                    else:
                        all_vals = []

                    current = {
                        "level": np.median(all_vals)
                        if all_vals
                        else (current["level"] + next_plateau["level"]) / 2,
                        "start_time": current["start_time"],
                        "end_time": next_plateau["end_time"],
                        "start_idx": current["start_idx"],
                        "end_idx": next_plateau["end_idx"],
                        "variance": np.var(all_vals) if all_vals else 0,
                        "values": all_vals,
                    }
                    merged_with_next = True
                    j += 1
                else:
                    break

            merged_plateaus.append(current)
            i = j if merged_with_next else i + 1

        return merged_plateaus
    else:
        return plateaus
