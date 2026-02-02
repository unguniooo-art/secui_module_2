"""Unit tests for Network collector."""
import pytest
from src.collectors.network_collector import NetworkCollector


class TestNetworkCollector:
    """Test cases for NetworkCollector."""

    def test_collect_returns_dict(self):
        """Test that collect() returns a dictionary."""
        collector = NetworkCollector()
        metrics = collector.collect()
        assert isinstance(metrics, dict)

    def test_network_io_metrics(self):
        """Test that network I/O metrics are collected."""
        collector = NetworkCollector()
        metrics = collector.collect()

        # Check for either per-interface or total metrics
        assert 'network_io' in metrics or 'network_io_total' in metrics

    def test_network_io_structure(self):
        """Test that network I/O has correct structure."""
        collector = NetworkCollector()
        metrics = collector.collect()

        if 'network_io' in metrics:
            assert isinstance(metrics['network_io'], dict)

            # Check first interface
            if len(metrics['network_io']) > 0:
                interface_name = list(metrics['network_io'].keys())[0]
                interface_stats = metrics['network_io'][interface_name]

                required_fields = [
                    'bytes_sent', 'bytes_recv',
                    'packets_sent', 'packets_recv',
                    'errin', 'errout', 'dropin', 'dropout'
                ]

                for field in required_fields:
                    assert field in interface_stats

    def test_network_io_values_positive(self):
        """Test that network I/O values are non-negative."""
        collector = NetworkCollector()
        metrics = collector.collect()

        if 'network_io_total' in metrics:
            io = metrics['network_io_total']
            assert io['bytes_sent'] >= 0
            assert io['bytes_recv'] >= 0
            assert io['packets_sent'] >= 0
            assert io['packets_recv'] >= 0

    def test_network_connections_metrics(self):
        """Test network connection statistics."""
        collector = NetworkCollector()
        metrics = collector.collect()

        # Connections might require elevated privileges
        if 'network_connections' in metrics:
            assert isinstance(metrics['network_connections'], dict)
            assert 'network_connections_total' in metrics
            assert metrics['network_connections_total'] >= 0
