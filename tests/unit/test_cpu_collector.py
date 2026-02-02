"""Unit tests for CPU collector."""
import pytest
from src.collectors.cpu_collector import CPUCollector


class TestCPUCollector:
    """Test cases for CPUCollector."""

    def test_collect_returns_dict(self):
        """Test that collect() returns a dictionary."""
        collector = CPUCollector()
        metrics = collector.collect()
        assert isinstance(metrics, dict)

    def test_collect_contains_required_metrics(self):
        """Test that collect() returns required CPU metrics."""
        collector = CPUCollector()
        metrics = collector.collect()

        # Check for required metrics
        assert 'cpu_usage_percent' in metrics
        assert 'cpu_count' in metrics
        assert 'cpu_per_core' in metrics

        # Validate types
        assert isinstance(metrics['cpu_usage_percent'], (int, float))
        assert isinstance(metrics['cpu_count'], int)
        assert isinstance(metrics['cpu_per_core'], list)

    def test_cpu_usage_in_valid_range(self):
        """Test that CPU usage is between 0 and 100."""
        collector = CPUCollector()
        metrics = collector.collect()

        assert 0 <= metrics['cpu_usage_percent'] <= 100

    def test_cpu_count_positive(self):
        """Test that CPU count is positive."""
        collector = CPUCollector()
        metrics = collector.collect()

        assert metrics['cpu_count'] > 0
        assert metrics['cpu_count_physical'] > 0

    def test_per_core_count_matches_cpu_count(self):
        """Test that per-core metrics match CPU count."""
        collector = CPUCollector()
        metrics = collector.collect()

        assert len(metrics['cpu_per_core']) == metrics['cpu_count']
