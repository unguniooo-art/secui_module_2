"""
CPU metrics collector using psutil.
Collects CPU usage, load average, and per-core metrics.
"""
import platform
import psutil
from typing import Dict, Any
from .base_collector import BaseCollector


class CPUCollector(BaseCollector):
    """Collects CPU-related metrics."""

    def collect(self) -> Dict[str, Any]:
        """
        Collect CPU metrics.

        Returns:
            Dictionary with CPU metrics:
            - cpu_usage_percent: Overall CPU usage
            - cpu_count: Number of CPU cores
            - cpu_per_core: List of per-core usage percentages
            - load_average: Load averages (1, 5, 15 min) - Linux/macOS only
        """
        metrics = {}

        # Overall CPU usage
        metrics['cpu_usage_percent'] = psutil.cpu_percent(interval=1)

        # CPU count
        metrics['cpu_count'] = psutil.cpu_count(logical=True)
        metrics['cpu_count_physical'] = psutil.cpu_count(logical=False)

        # Per-core CPU usage
        per_cpu = psutil.cpu_percent(interval=0.1, percpu=True)
        metrics['cpu_per_core'] = per_cpu

        # CPU times breakdown
        cpu_times = psutil.cpu_times_percent(interval=0.1)
        metrics['cpu_time_user'] = cpu_times.user
        metrics['cpu_time_system'] = cpu_times.system
        metrics['cpu_time_idle'] = cpu_times.idle

        # Platform-specific metrics
        if hasattr(cpu_times, 'iowait'):
            metrics['cpu_time_iowait'] = cpu_times.iowait

        # Load average (Linux/macOS only)
        if platform.system() != 'Windows':
            try:
                load_avg = psutil.getloadavg()
                metrics['load_average_1m'] = load_avg[0]
                metrics['load_average_5m'] = load_avg[1]
                metrics['load_average_15m'] = load_avg[2]
            except (AttributeError, OSError):
                pass

        # CPU frequency (if available)
        try:
            freq = psutil.cpu_freq()
            if freq:
                metrics['cpu_freq_current'] = freq.current
                metrics['cpu_freq_min'] = freq.min
                metrics['cpu_freq_max'] = freq.max
        except (AttributeError, NotImplementedError):
            pass

        return metrics
