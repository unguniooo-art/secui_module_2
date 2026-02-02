"""Unit tests for Disk collector."""
import pytest
from src.collectors.disk_collector import DiskCollector


class TestDiskCollector:
    """Test cases for DiskCollector."""

    def test_collect_returns_dict(self):
        """Test that collect() returns a dictionary."""
        collector = DiskCollector()
        metrics = collector.collect()
        assert isinstance(metrics, dict)

    def test_collect_contains_disk_partitions(self):
        """Test that collect() returns disk partition metrics."""
        collector = DiskCollector()
        metrics = collector.collect()

        assert 'disk_partitions' in metrics
        assert isinstance(metrics['disk_partitions'], list)

    def test_partition_has_required_fields(self):
        """Test that each partition has required fields."""
        collector = DiskCollector()
        metrics = collector.collect()

        if len(metrics['disk_partitions']) > 0:
            partition = metrics['disk_partitions'][0]
            required_fields = ['device', 'mountpoint', 'fstype', 'total', 'used', 'free', 'percent']

            for field in required_fields:
                assert field in partition

    def test_disk_usage_values_valid(self):
        """Test that disk usage values are valid."""
        collector = DiskCollector()
        metrics = collector.collect()

        for partition in metrics['disk_partitions']:
            assert partition['total'] >= 0
            assert partition['used'] >= 0
            assert partition['free'] >= 0
            assert 0 <= partition['percent'] <= 100
            assert partition['used'] <= partition['total']

    def test_disk_io_metrics(self):
        """Test that disk I/O metrics are collected."""
        collector = DiskCollector()
        metrics = collector.collect()

        # I/O metrics might not be available on all systems
        if 'disk_io' in metrics or 'disk_io_total' in metrics:
            if 'disk_io' in metrics:
                assert isinstance(metrics['disk_io'], dict)

            if 'disk_io_total' in metrics:
                io_total = metrics['disk_io_total']
                assert 'read_bytes' in io_total
                assert 'write_bytes' in io_total
                assert io_total['read_bytes'] >= 0
                assert io_total['write_bytes'] >= 0
