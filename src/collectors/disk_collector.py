"""
Disk metrics collector using psutil.
Collects disk usage and I/O statistics.
"""
import psutil
from typing import Dict, Any, List
from .base_collector import BaseCollector


class DiskCollector(BaseCollector):
    """Collects disk-related metrics."""

    # Pseudo filesystems to filter out in production
    PSEUDO_FS_TYPES = {'tmpfs', 'devtmpfs', 'squashfs', 'overlay'}

    def collect(self) -> Dict[str, Any]:
        """
        Collect disk metrics.

        Returns:
            Dictionary with disk metrics:
            - disk_partitions: List of partition info
            - disk_usage: Usage info per partition
            - disk_io: I/O statistics per disk
        """
        metrics = {}

        # Disk partitions and usage
        partitions = psutil.disk_partitions(all=False)
        partition_metrics = []

        for partition in partitions:
            # Skip pseudo filesystems in production
            if partition.fstype.lower() in self.PSEUDO_FS_TYPES:
                continue

            try:
                usage = psutil.disk_usage(partition.mountpoint)
                partition_info = {
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent
                }
                partition_metrics.append(partition_info)
            except (PermissionError, OSError):
                # Skip partitions we can't access
                continue

        metrics['disk_partitions'] = partition_metrics

        # Disk I/O counters
        try:
            disk_io = psutil.disk_io_counters(perdisk=True)
            if disk_io:
                io_metrics = {}
                for disk_name, counters in disk_io.items():
                    io_metrics[disk_name] = {
                        'read_count': counters.read_count,
                        'write_count': counters.write_count,
                        'read_bytes': counters.read_bytes,
                        'write_bytes': counters.write_bytes,
                        'read_time': counters.read_time,
                        'write_time': counters.write_time
                    }
                metrics['disk_io'] = io_metrics
        except (AttributeError, RuntimeError):
            # Some systems don't support per-disk I/O
            pass

        # Total disk I/O
        try:
            total_io = psutil.disk_io_counters()
            if total_io:
                metrics['disk_io_total'] = {
                    'read_count': total_io.read_count,
                    'write_count': total_io.write_count,
                    'read_bytes': total_io.read_bytes,
                    'write_bytes': total_io.write_bytes,
                    'read_time': total_io.read_time,
                    'write_time': total_io.write_time
                }
        except (AttributeError, RuntimeError):
            pass

        return metrics
