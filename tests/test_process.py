"""
Starter test file. Run with: pytest tests/
"""

from process import detect_anomalies, compute_stats


def test_detect_anomalies_empty():
    assert detect_anomalies([], threshold=10.0) == []


def test_compute_stats_single_point():
    stats = compute_stats([{"x": 0.0, "y": 0.0, "z": 0.0, "magnetic_intensity": 5.0}])
    assert stats["count"] == 1
    assert stats["mean"] == 5.0
