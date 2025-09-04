"""
Plotting functionality for fdprof.
"""

import json
from typing import Any, Dict, List

from .analysis import detect_plateaus


def create_plot(
    log_file: str,
    events: List[Dict[str, Any]],
    merge_threshold: float = 5.0,
    min_length: int = 5,
    tolerance: float = 2.0,
    jump_threshold: float = 2.0,
    save_filename: str = "",
) -> None:
    """Create and display plot of FD usage with event markers and jump labels."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Install matplotlib and numpy for plotting: pip install matplotlib numpy")
        return

    # Load FD data
    fd_data = []
    try:
        with open(log_file) as f:
            for line_num, line in enumerate(f, 1):
                if line.strip():
                    try:
                        fd_data.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        print(f"Warning: Invalid JSON on line {line_num}: {e}")
                        continue
    except FileNotFoundError:
        print(f"Log file {log_file} not found")
        return
    except OSError as e:
        print(f"Error reading log file {log_file}: {e}")
        return

    if not fd_data:
        print("No FD data to plot")
        return

    # Create plot
    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot FD usage
    times = [dp["elapsed"] for dp in fd_data]
    fd_counts = [dp["open_fds"] for dp in fd_data if dp["open_fds"] >= 0]
    valid_times = times[: len(fd_counts)]

    if fd_counts:
        ax.plot(
            valid_times, fd_counts, "o-", linewidth=1.5, label="Open FDs", markersize=3
        )
        y_max = max(fd_counts)

        # Detect plateaus using user-specified parameters
        plateaus = detect_plateaus(
            valid_times,
            fd_counts,
            min_length=min_length,
            tolerance=tolerance,
            merge_close_levels=True,
            merge_threshold=merge_threshold,
        )

        # Draw horizontal lines for each plateau
        for plateau in plateaus:
            ax.axhline(
                y=plateau["level"],
                xmin=(plateau["start_time"] - min(valid_times))
                / (max(valid_times) - min(valid_times)),
                xmax=(plateau["end_time"] - min(valid_times))
                / (max(valid_times) - min(valid_times)),
                color="lightgray",
                linestyle="-",
                alpha=0.7,
                linewidth=2,
            )

        # Calculate and label jumps between consecutive plateaus
        jumps = []
        for i in range(len(plateaus) - 1):
            current = plateaus[i]
            next_plateau = plateaus[i + 1]

            jump_size = int(next_plateau["level"] - current["level"])

            # Only show significant jumps using configurable threshold
            if abs(jump_size) >= jump_threshold:
                # Find the transition point between plateaus
                transition_time = (current["end_time"] + next_plateau["start_time"]) / 2
                transition_y = (current["level"] + next_plateau["level"]) / 2

                # Draw vertical arrow/line between plateaus
                ax.annotate(
                    "",
                    xy=(transition_time, next_plateau["level"]),
                    xytext=(transition_time, current["level"]),
                    arrowprops={
                        "arrowstyle": "<->",
                        "color": "red" if jump_size > 0 else "blue",
                        "lw": 1.5,
                        "alpha": 0.6,
                    },
                )

                # Add jump size label
                sign = "+" if jump_size > 0 else ""
                label_text = f"{sign}{jump_size}"
                ax.text(
                    transition_time + 0.02,
                    transition_y,
                    label_text,
                    fontsize=10,
                    fontweight="bold",
                    color="darkred" if jump_size > 0 else "darkblue",
                    verticalalignment="center",
                    horizontalalignment="left",
                    bbox={
                        "boxstyle": "round,pad=0.3",
                        "facecolor": "white",
                        "alpha": 0.9,
                        "edgecolor": "gray",
                    },
                )

                jumps.append(
                    {
                        "time": transition_time,
                        "size": jump_size,
                        "from_level": current["level"],
                        "to_level": next_plateau["level"],
                    }
                )

        # Print summary
        if plateaus:
            print(f"\nDetected {len(plateaus)} stable plateaus:")
            for i, plateau in enumerate(plateaus):
                print(
                    f"  Plateau {i+1}: {plateau['level']:.0f} FDs from {plateau['start_time']:.2f}s to {plateau['end_time']:.2f}s"
                )

        if jumps:
            print(f"\nDetected {len(jumps)} jumps between plateaus:")
            for jump in jumps:
                sign = "+" if jump["size"] > 0 else ""
                print(
                    f"  {jump['time']:6.2f}s: {sign}{jump['size']} FDs ({jump['from_level']:.0f} → {jump['to_level']:.0f})"
                )

    else:
        y_max = 100

    # Add event markers
    colors = ["red", "orange", "purple", "green", "brown"]
    for i, event in enumerate(events):
        color = colors[i % len(colors)]
        ax.axvline(
            x=event["elapsed"], color=color, linestyle="--", alpha=0.7, linewidth=1
        )

        # Stagger text heights to avoid overlap
        y_pos = y_max * (0.8 + (i % 3) * 0.1)
        ax.text(
            event["elapsed"],
            y_pos,
            event["message"],
            rotation=45,
            fontsize=8,
            alpha=0.8,
            color=color,
            bbox={"boxstyle": "round,pad=0.3", "facecolor": "white", "alpha": 0.7},
        )

    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Open File Descriptors")
    ax.set_title("File Descriptor Usage with Events")
    ax.grid(True, alpha=0.3)

    # Adjust x-axis to leave room for jump labels on the right
    if fd_counts:
        ax.set_xlim(left=min(valid_times) - 0.1, right=max(valid_times) * 1.05)
        ax.legend()

    plt.tight_layout()

    if save_filename:
        # Validate file extension
        supported_formats = {".png", ".pdf", ".svg", ".jpg", ".jpeg", ".eps", ".ps"}
        file_ext = (
            "." + save_filename.split(".")[-1].lower() if "." in save_filename else ""
        )

        if file_ext not in supported_formats:
            print(
                f"Warning: Unsupported file format '{file_ext}'. Supported: {', '.join(sorted(supported_formats))}"
            )
            print("Saving as PNG instead.")
            save_filename = save_filename.rsplit(".", 1)[0] + ".png"

        try:
            plt.savefig(save_filename, dpi=300, bbox_inches="tight")
            print(f"Plot saved to: {save_filename}")
        except OSError as e:
            print(f"Error saving plot to {save_filename}: {e}")
    else:
        plt.show()
