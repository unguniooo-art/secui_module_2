"""
Memory metrics collector using psutil.
Collects RAM and swap memory metrics.
"""
import psutil
from typing import Dict, Any
from .base_collector import BaseCollector


class MemoryCollector(BaseCollector):
    """Collects memory-related metrics."""

    def collect(self) -> Dict[str, Any]:
        """
        Collect memory metrics.

        Returns:
            Dictionary with memory metrics:
            - memory_total: Total physical memory in bytes
            - memory_available: Available memory in bytes
            - memory_used: Used memory in bytes
            - memory_percent: Memory usage percentage
            - swap_total: Total swap memory in bytes
            - swap_used: Used swap memory in bytes
            - swap_percent: Swap usage percentage
        """
        metrics = {}

        # Virtual memory (RAM)
        vm = psutil.virtual_memory()
        metrics['memory_total'] = vm.total
        metrics['memory_available'] = vm.available
        metrics['memory_used'] = vm.used
        metrics['memory_free'] = vm.free
        metrics['memory_percent'] = vm.percent

        # Additional memory fields (platform-specific)
        if hasattr(vm, 'active'):
            metrics['memory_active'] = vm.active
        if hasattr(vm, 'inactive'):
            metrics['memory_inactive'] = vm.inactive
        if hasattr(vm, 'buffers'):
            metrics['memory_buffers'] = vm.buffers
        if hasattr(vm, 'cached'):
            metrics['memory_cached'] = vm.cached

        # Swap memory
        swap = psutil.swap_memory()
        metrics['swap_total'] = swap.total
        metrics['swap_used'] = swap.used
        metrics['swap_free'] = swap.free
        metrics['swap_percent'] = swap.percent

        # Swap I/O (if available)
        if hasattr(swap, 'sin'):
            metrics['swap_sin'] = swap.sin
        if hasattr(swap, 'sout'):
            metrics['swap_sout'] = swap.sout

        return metrics
