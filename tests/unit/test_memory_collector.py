"""Unit tests for Memory collector."""
import pytest
from src.collectors.memory_collector import MemoryCollector


class TestMemoryCollector:
    """Test cases for MemoryCollector."""

    def test_collect_returns_dict(self):
        """Test that collect() returns a dictionary."""
        collector = MemoryCollector()
        metrics = collector.collect()
        assert isinstance(metrics, dict)

    def test_collect_contains_required_metrics(self):
        """Test that collect() returns required memory metrics."""
        collector = MemoryCollector()
        metrics = collector.collect()

        # Check for required metrics
        required = [
            'memory_total',
            'memory_used',
            'memory_available',
            'memory_percent',
            'swap_total',
            'swap_used',
            'swap_percent'
        ]

        for metric in required:
            assert metric in metrics

    def test_memory_values_positive(self):
        """Test that memory values are positive or zero."""
        collector = MemoryCollector()
        metrics = collector.collect()

        assert metrics['memory_total'] >= 0
        assert metrics['memory_used'] >= 0
        assert metrics['memory_available'] >= 0

    def test_memory_percent_in_valid_range(self):
        """Test that memory percentage is between 0 and 100."""
        collector = MemoryCollector()
        metrics = collector.collect()

        assert 0 <= metrics['memory_percent'] <= 100
        assert 0 <= metrics['swap_percent'] <= 100

    def test_used_memory_less_than_total(self):
        """Test that used memory is less than or equal to total."""
        collector = MemoryCollector()
        metrics = collector.collect()

        assert metrics['memory_used'] <= metrics['memory_total']
        assert metrics['swap_used'] <= metrics['swap_total']
