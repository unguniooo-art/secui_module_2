"""
Base collector interface for system metrics.
All metric collectors should inherit from this class.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseCollector(ABC):
    """Abstract base class for metric collectors."""

    @abstractmethod
    def collect(self) -> Dict[str, Any]:
        """
        Collect metrics and return as dictionary.

        Returns:
            Dict mapping metric names to values.
            Example: {'cpu_usage_percent': 45.2, 'cpu_count': 8}
        """
        pass

    def get_name(self) -> str:
        """Return the collector name."""
        return self.__class__.__name__
