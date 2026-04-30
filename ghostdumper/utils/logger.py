"""
Logging utilities for GhostDumper v2.2
"""

import sys
from typing import Optional
from rich.console import Console
from rich.logging import RichHandler
import logging


class GhostLogger:
    """Structured logger for GhostDumper."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.console = Console(stderr=True)

        # Setup logging
        self.logger = logging.getLogger("ghostdumper")
        self.logger.setLevel(logging.DEBUG if verbose else logging.INFO)

        if not self.logger.handlers:
            handler = RichHandler(console=self.console, show_time=False)
            handler.setFormatter(logging.Formatter("%(message)s"))
            self.logger.addHandler(handler)

    def debug(self, msg: str):
        if self.verbose:
            self.logger.debug(msg)

    def info(self, msg: str):
        self.logger.info(msg)

    def warning(self, msg: str):
        self.logger.warning(msg)

    def error(self, msg: str):
        self.logger.error(msg)

    def critical(self, msg: str):
        self.logger.critical(msg)
