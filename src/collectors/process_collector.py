"""
Process metrics collector using psutil.
Collects process count, top processes, and zombie processes.
"""
import psutil
from typing import Dict, Any, List
from .base_collector import BaseCollector


class ProcessCollector(BaseCollector):
    """Collects process-related metrics."""

    def collect(self) -> Dict[str, Any]:
        """
        Collect process metrics.

        Returns:
            Dictionary with process metrics:
            - process_count: Total number of running processes
            - process_zombie_count: Number of zombie processes
            - top_processes_cpu: Top N processes by CPU usage
            - top_processes_memory: Top N processes by memory usage
        """
        metrics = {}

        try:
            # Get all processes
            all_processes = list(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']))

            # Total process count
            metrics['process_count'] = len(all_processes)

            # Count zombie processes
            zombie_count = 0
            for proc in all_processes:
                try:
                    if proc.info['status'] == psutil.STATUS_ZOMBIE:
                        zombie_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied, KeyError):
                    continue

            metrics['process_zombie_count'] = zombie_count

            # Get processes with CPU and memory info
            process_list = []
            for proc in all_processes:
                try:
                    info = proc.info
                    if info['cpu_percent'] is not None and info['memory_percent'] is not None:
                        process_list.append({
                            'pid': info['pid'],
                            'name': info['name'],
                            'cpu_percent': info['cpu_percent'],
                            'memory_percent': info['memory_percent']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied, KeyError):
                    continue

            # Top 10 processes by CPU
            top_cpu = sorted(process_list, key=lambda x: x['cpu_percent'], reverse=True)[:10]
            metrics['top_processes_cpu'] = top_cpu

            # Top 10 processes by Memory
            top_memory = sorted(process_list, key=lambda x: x['memory_percent'], reverse=True)[:10]
            metrics['top_processes_memory'] = top_memory

            # Thread count (total)
            try:
                total_threads = sum(p.num_threads() for p in psutil.process_iter() if p.is_running())
                metrics['thread_count_total'] = total_threads
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        except Exception as e:
            # If we can't collect process metrics, return minimal info
            metrics['process_count'] = 0
            metrics['process_zombie_count'] = 0
            metrics['top_processes_cpu'] = []
            metrics['top_processes_memory'] = []

        return metrics
