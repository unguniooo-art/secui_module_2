"""
Network metrics collector using psutil.
Collects network I/O and connection statistics.
"""
import psutil
from typing import Dict, Any
from .base_collector import BaseCollector


class NetworkCollector(BaseCollector):
    """Collects network-related metrics."""

    def collect(self) -> Dict[str, Any]:
        """
        Collect network metrics.

        Returns:
            Dictionary with network metrics:
            - network_io: I/O statistics per interface
            - network_connections: Connection statistics by state
        """
        metrics = {}

        # Network I/O per interface
        try:
            net_io = psutil.net_io_counters(pernic=True)
            if net_io:
                io_metrics = {}
                for interface, counters in net_io.items():
                    io_metrics[interface] = {
                        'bytes_sent': counters.bytes_sent,
                        'bytes_recv': counters.bytes_recv,
                        'packets_sent': counters.packets_sent,
                        'packets_recv': counters.packets_recv,
                        'errin': counters.errin,
                        'errout': counters.errout,
                        'dropin': counters.dropin,
                        'dropout': counters.dropout
                    }
                metrics['network_io'] = io_metrics
        except (AttributeError, RuntimeError):
            pass

        # Total network I/O
        try:
            total_io = psutil.net_io_counters()
            if total_io:
                metrics['network_io_total'] = {
                    'bytes_sent': total_io.bytes_sent,
                    'bytes_recv': total_io.bytes_recv,
                    'packets_sent': total_io.packets_sent,
                    'packets_recv': total_io.packets_recv,
                    'errin': total_io.errin,
                    'errout': total_io.errout,
                    'dropin': total_io.dropin,
                    'dropout': total_io.dropout
                }
        except (AttributeError, RuntimeError):
            pass

        # Network connections by state
        try:
            connections = psutil.net_connections(kind='inet')
            connection_stats = {
                'ESTABLISHED': 0,
                'SYN_SENT': 0,
                'SYN_RECV': 0,
                'FIN_WAIT1': 0,
                'FIN_WAIT2': 0,
                'TIME_WAIT': 0,
                'CLOSE': 0,
                'CLOSE_WAIT': 0,
                'LAST_ACK': 0,
                'LISTEN': 0,
                'CLOSING': 0,
                'NONE': 0
            }

            for conn in connections:
                status = conn.status
                if status in connection_stats:
                    connection_stats[status] += 1

            metrics['network_connections'] = connection_stats
            metrics['network_connections_total'] = len(connections)

        except (PermissionError, psutil.AccessDenied):
            # Requires elevated privileges on some systems
            pass

        return metrics
