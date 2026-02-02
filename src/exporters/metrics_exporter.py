"""
Prometheus metrics exporter.
Exposes system metrics at :9100/metrics endpoint.
"""
import time
import argparse
from prometheus_client import Gauge, Counter, CollectorRegistry, generate_latest
from prometheus_client import start_http_server
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.collectors import CPUCollector, MemoryCollector, DiskCollector, NetworkCollector


class MetricsExporter:
    """
    Prometheus metrics exporter using Registry pattern.
    Collects system metrics and exposes them in Prometheus format.
    """

    def __init__(self, port=9100):
        self.port = port
        self.registry = CollectorRegistry()

        # Initialize collectors
        self.cpu_collector = CPUCollector()
        self.memory_collector = MemoryCollector()
        self.disk_collector = DiskCollector()
        self.network_collector = NetworkCollector()

        # Create Prometheus metrics
        self._create_metrics()

    def _create_metrics(self):
        """Create Prometheus Gauge and Counter metrics."""

        # CPU metrics
        self.cpu_usage = Gauge(
            'node_cpu_usage_percent',
            'CPU usage percentage',
            registry=self.registry
        )
        self.cpu_count = Gauge(
            'node_cpu_count',
            'Number of CPU cores',
            registry=self.registry
        )
        self.load_average = Gauge(
            'node_load_average',
            'Load average',
            ['period'],
            registry=self.registry
        )

        # Memory metrics
        self.memory_total = Gauge(
            'node_memory_total_bytes',
            'Total memory in bytes',
            registry=self.registry
        )
        self.memory_used = Gauge(
            'node_memory_used_bytes',
            'Used memory in bytes',
            registry=self.registry
        )
        self.memory_available = Gauge(
            'node_memory_available_bytes',
            'Available memory in bytes',
            registry=self.registry
        )
        self.memory_percent = Gauge(
            'node_memory_usage_percent',
            'Memory usage percentage',
            registry=self.registry
        )
        self.swap_total = Gauge(
            'node_swap_total_bytes',
            'Total swap in bytes',
            registry=self.registry
        )
        self.swap_used = Gauge(
            'node_swap_used_bytes',
            'Used swap in bytes',
            registry=self.registry
        )
        self.swap_percent = Gauge(
            'node_swap_usage_percent',
            'Swap usage percentage',
            registry=self.registry
        )

        # Disk metrics
        self.disk_usage = Gauge(
            'node_disk_usage_bytes',
            'Disk usage in bytes',
            ['device', 'mountpoint'],
            registry=self.registry
        )
        self.disk_total = Gauge(
            'node_disk_total_bytes',
            'Total disk space in bytes',
            ['device', 'mountpoint'],
            registry=self.registry
        )
        self.disk_usage_percent = Gauge(
            'node_disk_usage_percent',
            'Disk usage percentage',
            ['device', 'mountpoint'],
            registry=self.registry
        )
        self.disk_io_read_bytes = Counter(
            'node_disk_io_read_bytes_total',
            'Total bytes read from disk',
            ['device'],
            registry=self.registry
        )
        self.disk_io_write_bytes = Counter(
            'node_disk_io_write_bytes_total',
            'Total bytes written to disk',
            ['device'],
            registry=self.registry
        )

        # Network metrics
        self.network_receive_bytes = Counter(
            'node_network_receive_bytes_total',
            'Total bytes received',
            ['interface'],
            registry=self.registry
        )
        self.network_transmit_bytes = Counter(
            'node_network_transmit_bytes_total',
            'Total bytes transmitted',
            ['interface'],
            registry=self.registry
        )
        self.network_receive_packets = Counter(
            'node_network_receive_packets_total',
            'Total packets received',
            ['interface'],
            registry=self.registry
        )
        self.network_transmit_packets = Counter(
            'node_network_transmit_packets_total',
            'Total packets transmitted',
            ['interface'],
            registry=self.registry
        )
        self.network_connections_total = Gauge(
            'node_network_connections_total',
            'Total network connections',
            registry=self.registry
        )

    def update_metrics(self):
        """Collect and update all metrics."""

        # CPU metrics
        cpu_metrics = self.cpu_collector.collect()
        self.cpu_usage.set(cpu_metrics.get('cpu_usage_percent', 0))
        self.cpu_count.set(cpu_metrics.get('cpu_count', 0))

        if 'load_average_1m' in cpu_metrics:
            self.load_average.labels(period='1m').set(cpu_metrics['load_average_1m'])
            self.load_average.labels(period='5m').set(cpu_metrics['load_average_5m'])
            self.load_average.labels(period='15m').set(cpu_metrics['load_average_15m'])

        # Memory metrics
        mem_metrics = self.memory_collector.collect()
        self.memory_total.set(mem_metrics.get('memory_total', 0))
        self.memory_used.set(mem_metrics.get('memory_used', 0))
        self.memory_available.set(mem_metrics.get('memory_available', 0))
        self.memory_percent.set(mem_metrics.get('memory_percent', 0))
        self.swap_total.set(mem_metrics.get('swap_total', 0))
        self.swap_used.set(mem_metrics.get('swap_used', 0))
        self.swap_percent.set(mem_metrics.get('swap_percent', 0))

        # Disk metrics
        disk_metrics = self.disk_collector.collect()
        for partition in disk_metrics.get('disk_partitions', []):
            device = partition['device']
            mountpoint = partition['mountpoint']
            self.disk_total.labels(device=device, mountpoint=mountpoint).set(partition['total'])
            self.disk_usage.labels(device=device, mountpoint=mountpoint).set(partition['used'])
            self.disk_usage_percent.labels(device=device, mountpoint=mountpoint).set(partition['percent'])

        # Disk I/O
        disk_io = disk_metrics.get('disk_io', {})
        for device, counters in disk_io.items():
            # Note: Counter values should only increase, so we use _total suffix
            self.disk_io_read_bytes.labels(device=device)._value.set(counters['read_bytes'])
            self.disk_io_write_bytes.labels(device=device)._value.set(counters['write_bytes'])

        # Network metrics
        net_metrics = self.network_collector.collect()
        net_io = net_metrics.get('network_io', {})
        for interface, counters in net_io.items():
            self.network_receive_bytes.labels(interface=interface)._value.set(counters['bytes_recv'])
            self.network_transmit_bytes.labels(interface=interface)._value.set(counters['bytes_sent'])
            self.network_receive_packets.labels(interface=interface)._value.set(counters['packets_recv'])
            self.network_transmit_packets.labels(interface=interface)._value.set(counters['packets_sent'])

        if 'network_connections_total' in net_metrics:
            self.network_connections_total.set(net_metrics['network_connections_total'])

    def run(self):
        """Start the HTTP server and continuously update metrics."""
        # Start Prometheus HTTP server
        start_http_server(self.port, registry=self.registry)
        print(f"Metrics exporter running on http://localhost:{self.port}/metrics")
        print("Press Ctrl+C to stop")

        try:
            while True:
                self.update_metrics()
                time.sleep(15)  # Update every 15 seconds
        except KeyboardInterrupt:
            print("\nShutting down...")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='System Resource Monitoring Exporter')
    parser.add_argument('--port', type=int, default=9100, help='Port to expose metrics (default: 9100)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')

    args = parser.parse_args()

    exporter = MetricsExporter(port=args.port)
    exporter.run()


if __name__ == '__main__':
    main()
