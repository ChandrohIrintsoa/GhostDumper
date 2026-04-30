"""
GhostDumper v2.2 — IL2CPP Deep Analyzer & Runtime Toolkit

A next-generation reverse engineering framework for Unity IL2CPP binaries.
"""

__version__ = "2.2.0"
__author__ = "Chandroh Irintsoa"
__license__ = "MIT"

from .core.engine import GhostEngine
from .core.config import GhostConfig

__all__ = ["GhostEngine", "GhostConfig"]
