"""Integration tests for metrics exporter."""
import pytest
import time
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.exporters.metrics_exporter import MetricsExporter


class TestMetricsExporter:
    """Integration tests for MetricsExporter."""

    def test_exporter_initialization(self):
        """Test that exporter initializes correctly."""
        exporter = MetricsExporter(port=9101)
        assert exporter.port == 9101
        assert exporter.registry is not None
        assert exporter.cpu_collector is not None
        assert exporter.memory_collector is not None
        assert exporter.disk_collector is not None
        assert exporter.network_collector is not None

    def test_update_metrics(self):
        """Test that update_metrics runs without errors."""
        exporter = MetricsExporter(port=9101)

        # Should not raise any exceptions
        try:
            exporter.update_metrics()
            success = True
        except Exception as e:
            success = False
            print(f"Error: {e}")

        assert success

    def test_metrics_registry(self):
        """Test that metrics are registered in the registry."""
        exporter = MetricsExporter(port=9101)
        exporter.update_metrics()

        # Get metrics from registry
        metrics_output = exporter.registry.collect()

        # Check that we have metrics
        metric_families = list(metrics_output)
        assert len(metric_families) > 0

        # Check for some expected metrics
        metric_names = [m.name for m in metric_families]
        assert 'node_cpu_usage_percent' in metric_names
        assert 'node_memory_usage_percent' in metric_names

    def test_all_collectors_work(self):
        """Test that all collectors can collect metrics."""
        exporter = MetricsExporter(port=9101)

        # Test each collector individually
        cpu_metrics = exporter.cpu_collector.collect()
        assert isinstance(cpu_metrics, dict)
        assert len(cpu_metrics) > 0

        mem_metrics = exporter.memory_collector.collect()
        assert isinstance(mem_metrics, dict)
        assert len(mem_metrics) > 0

        disk_metrics = exporter.disk_collector.collect()
        assert isinstance(disk_metrics, dict)
        assert len(disk_metrics) > 0

        net_metrics = exporter.network_collector.collect()
        assert isinstance(net_metrics, dict)
        assert len(net_metrics) > 0

    def test_multiple_updates(self):
        """Test that metrics can be updated multiple times."""
        exporter = MetricsExporter(port=9101)

        # Update metrics 3 times
        for i in range(3):
            exporter.update_metrics()
            time.sleep(0.1)

        # Should complete without errors
        assert True

    def test_custom_port(self):
        """Test that custom port is set correctly."""
        ports = [9100, 9101, 9102]

        for port in ports:
            exporter = MetricsExporter(port=port)
            assert exporter.port == port
