"""Results Parser Agent - A deep agent for extracting metrics from result files."""

from .config.settings import settings
from .core import ResultsParser, ToolRegistry

__version__ = "0.2.1"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    "ResultsParser",
    "ToolRegistry",
    "settings",
]
