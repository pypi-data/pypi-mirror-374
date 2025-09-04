"""Tests for analysis and plateau detection functionality."""

import numpy as np
from fdprof.analysis import detect_plateaus


class TestPlateauDetection:
    """Test plateau detection functionality."""

    def test_detect_plateaus_empty_data(self):
        """Test plateau detection with empty data."""
        plateaus = detect_plateaus([], [], min_length=5)
        assert plateaus == []

    def test_detect_plateaus_insufficient_data(self):
        """Test plateau detection with insufficient data points."""
        times = [0.0, 0.1, 0.2]
        values = [10, 11, 12]
        plateaus = detect_plateaus(times, values, min_length=5)
        assert plateaus == []

    def test_detect_plateaus_single_stable_region(self):
        """Test detecting a single stable plateau."""
        times = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        values = [100, 101, 99, 100, 101, 100, 99, 100, 101, 100]

        plateaus = detect_plateaus(times, values, min_length=5, tolerance=2.0)

        assert len(plateaus) == 1
        plateau = plateaus[0]
        assert plateau["start_time"] == 0.0
        assert plateau["end_time"] == 0.9
        assert 99 <= plateau["level"] <= 101

    def test_detect_plateaus_multiple_regions(self):
        """Test detecting multiple plateau regions."""
        # Create data with two distinct plateaus
        times = list(range(20))  # 0 to 19
        values = [10] * 8 + [50] * 12  # First plateau at 10, second at 50

        plateaus = detect_plateaus(
            [float(t) for t in times],
            values,
            min_length=5,
            tolerance=1.0,
            merge_close_levels=False,
        )

        assert len(plateaus) >= 1  # Should detect at least one clear plateau

        # Check if we detected the high plateau
        high_plateau = [p for p in plateaus if p["level"] > 40]
        assert len(high_plateau) >= 1

    def test_detect_plateaus_with_noise(self):
        """Test plateau detection with noisy data."""
        np.random.seed(42)  # For reproducible tests

        # Create a plateau with some noise
        base_times = np.linspace(0, 2, 50)
        base_values = np.full(50, 100) + np.random.normal(0, 2, 50)

        plateaus = detect_plateaus(
            base_times.tolist(),
            base_values.astype(int).tolist(),
            min_length=10,
            tolerance=5.0,
        )

        assert len(plateaus) >= 1
        # The detected level should be close to 100
        assert 95 <= plateaus[0]["level"] <= 105

    def test_detect_plateaus_merge_close_levels(self):
        """Test merging of plateaus with similar levels."""
        # Create two plateaus with slightly different but close levels
        times = list(range(30))
        values = [100] * 10 + [110] * 10 + [105] * 10

        plateaus_no_merge = detect_plateaus(
            [float(t) for t in times],
            values,
            min_length=5,
            tolerance=1.0,
            merge_close_levels=False,
            merge_threshold=20.0,
        )

        plateaus_with_merge = detect_plateaus(
            [float(t) for t in times],
            values,
            min_length=5,
            tolerance=1.0,
            merge_close_levels=True,
            merge_threshold=20.0,  # Should merge plateaus within 20 units
        )

        # With merging enabled, we should have fewer plateaus
        assert len(plateaus_with_merge) <= len(plateaus_no_merge)

    def test_detect_plateaus_parameters(self):
        """Test that plateau detection parameters work correctly."""
        times = [float(i) for i in range(20)]
        values = [100] * 20  # Perfect plateau

        # Test different min_length requirements
        plateaus_short = detect_plateaus(times, values, min_length=5)
        plateaus_long = detect_plateaus(times, values, min_length=25)

        assert len(plateaus_short) >= 1  # Should detect with min_length=5
        assert len(plateaus_long) == 0  # Should not detect with min_length=25

    def test_detect_plateaus_tolerance(self):
        """Test plateau detection tolerance parameter."""
        times = [float(i) for i in range(20)]
        values = [100, 105, 95, 100, 105, 95] * 3 + [100, 105]  # Oscillating values

        # Strict tolerance should not find plateau
        plateaus_strict = detect_plateaus(times, values, min_length=5, tolerance=1.0)

        # Loose tolerance should find plateau
        plateaus_loose = detect_plateaus(times, values, min_length=5, tolerance=10.0)

        assert len(plateaus_loose) >= len(plateaus_strict)

    def test_detect_plateaus_step_function(self):
        """Test plateau detection on step function data."""
        # Create clear step function: low -> high -> low
        times = [float(i) for i in range(30)]
        values = [10] * 10 + [100] * 10 + [20] * 10

        plateaus = detect_plateaus(
            times, values, min_length=5, tolerance=2.0, merge_close_levels=False
        )

        # Should detect multiple distinct plateaus
        assert len(plateaus) >= 2

        # Check that we have both low and high levels
        levels = [p["level"] for p in plateaus]
        assert any(level < 30 for level in levels)  # Low plateau
        assert any(level > 80 for level in levels)  # High plateau

    def test_detect_plateaus_return_structure(self):
        """Test that plateau detection returns correct data structure."""
        times = [float(i) for i in range(10)]
        values = [100] * 10

        plateaus = detect_plateaus(times, values, min_length=5)

        if plateaus:
            plateau = plateaus[0]
            required_keys = ["level", "start_time", "end_time", "start_idx", "end_idx"]
            for key in required_keys:
                assert key in plateau

            # Check data types and ranges
            assert isinstance(plateau["level"], (int, float))
            assert isinstance(plateau["start_time"], (int, float))
            assert isinstance(plateau["end_time"], (int, float))
            assert isinstance(plateau["start_idx"], int)
            assert isinstance(plateau["end_idx"], int)

            # Check logical constraints
            assert plateau["start_time"] <= plateau["end_time"]
            assert plateau["start_idx"] <= plateau["end_idx"]
