"""
Demo script for testing fdprof functionality.

This script creates a realistic file descriptor usage pattern that's perfect
for demonstrating fdprof's monitoring and analysis capabilities.
"""

import sys
import tempfile
import time
from pathlib import Path


def log_event(message: str):
    """Log a timestamped event that fdprof will capture."""
    print(f"EVENT: {time.time():.9f} {message}")


def demo_script():
    """Run a demo that creates interesting FD usage patterns."""
    print("🔧 fdprof Demo Script - File Descriptor Usage Patterns")
    print("=" * 60)
    print("This demo will:")
    print("1. Open files in stages to create FD plateaus")
    print("2. Log events at each stage for visualization")
    print("3. Create jumps in FD usage for analysis")
    print("4. Clean up all files when done")
    print("=" * 60)

    log_event("Demo started")

    # Stage 1: Initial file opening
    print("\n📁 Stage 1: Opening initial batch of files...")
    stage1_files = []
    for i in range(5):
        f = tempfile.NamedTemporaryFile(
            mode="w", delete=False, prefix=f"fdprof_demo_s1_{i}_"
        )
        f.write(f"Stage 1 - File {i} content\nCreated for fdprof demo\n")
        f.flush()  # Ensure data is written
        stage1_files.append(f)

    print(f"✅ Opened {len(stage1_files)} files in stage 1")
    log_event("Stage 1 complete")

    # Wait to create a stable plateau
    print("⏳ Waiting 1.5 seconds (creating stable plateau)...")
    time.sleep(1.5)

    # Stage 2: Open more files (creating a jump)
    print("\n📁 Stage 2: Opening more files (creating FD jump)...")
    stage2_files = []
    for i in range(8):
        f = tempfile.NamedTemporaryFile(
            mode="w", delete=False, prefix=f"fdprof_demo_s2_{i}_"
        )
        f.write(f"Stage 2 - File {i} content\nMore files for higher FD count\n")
        f.flush()
        stage2_files.append(f)

    print(f"✅ Opened {len(stage2_files)} more files in stage 2")
    log_event("Stage 2 complete")

    # Wait to create another stable plateau
    print("⏳ Waiting 1.2 seconds (higher plateau)...")
    time.sleep(1.2)

    # Stage 3: Open even more files (another jump)
    print("\n📁 Stage 3: Opening final batch (maximum FDs)...")
    stage3_files = []
    for i in range(6):
        f = tempfile.NamedTemporaryFile(
            mode="w", delete=False, prefix=f"fdprof_demo_s3_{i}_"
        )
        f.write(f"Stage 3 - File {i} content\nPeak FD usage demonstration\n")
        f.flush()
        stage3_files.append(f)

    print(f"✅ Opened {len(stage3_files)} more files in stage 3")
    log_event("Peak reached")

    # Wait at peak usage
    print("⏳ Waiting 1 second (peak plateau)...")
    time.sleep(1.0)

    # Stage 4: Start closing files in stages
    print("\n🗂️ Stage 4: Closing stage 1 files (first FD drop)...")
    for _, f in enumerate(stage1_files):
        f.close()
        Path(f.name).unlink(missing_ok=True)

    print(f"✅ Closed all {len(stage1_files)} stage 1 files")
    log_event("First drop")

    # Wait to show the drop
    print("⏳ Waiting 0.8 seconds (showing FD drop)...")
    time.sleep(0.8)

    # Stage 5: Close more files
    print("\n🗂️ Stage 5: Closing stage 2 files (second FD drop)...")
    for _, f in enumerate(stage2_files):
        f.close()
        Path(f.name).unlink(missing_ok=True)

    print(f"✅ Closed all {len(stage2_files)} stage 2 files")
    log_event("Second drop")

    # Wait to show the drop
    print("⏳ Waiting 0.6 seconds (showing second drop)...")
    time.sleep(0.6)

    # Stage 6: Close remaining files
    print("\n🗂️ Stage 6: Closing remaining files (final cleanup)...")
    for _, f in enumerate(stage3_files):
        f.close()
        Path(f.name).unlink(missing_ok=True)

    print(f"✅ Closed all {len(stage3_files)} stage 3 files")
    log_event("Demo complete")

    print("\n🎉 Demo completed successfully!")
    print("Expected pattern:")
    print("  📈 Stage 1: Baseline → +5 FDs")
    print("  📈 Stage 2: Jump → +8 FDs (total +13)")
    print("  📈 Stage 3: Jump → +6 FDs (total +19)")
    print("  📉 Stage 4: Drop → -5 FDs (total +14)")
    print("  📉 Stage 5: Drop → -8 FDs (total +6)")
    print("  📉 Stage 6: Drop → -6 FDs (back to baseline)")
    print("\n💡 Use --plot to see the visualization!")


def main():
    """Main entry point for fdprof.demo command."""
    try:
        demo_script()
    except KeyboardInterrupt:
        print("\n\n⚠️ Demo interrupted by user")
        log_event("Interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Demo failed with error: {e}")
        log_event(f"Demo failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
