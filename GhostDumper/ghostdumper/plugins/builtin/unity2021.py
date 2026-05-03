"""
Unity 2021+ Plugin for GhostDumper v2.2

Handles Unity 2021.2+ specific IL2CPP changes.
"""

from typing import Dict, Any
from ..plugin_manager import LoaderPlugin


class Unity2021Plugin(LoaderPlugin):
    """Unity 2021+ specific loader."""

    name = "unity2021"
    version = "1.0"
    author = "GhostDumper Community"
    description = "Handles Unity 2021.2+ IL2CPP metadata format changes"

    SUPPORTED_VERSIONS = [29, 30, 31]

    def load_binary(self, path: str):
        return None

    def load_metadata(self, path: str):
        return None

    def is_compatible(self, result) -> bool:
        if hasattr(result, 'metadata_info') and result.metadata_info:
            version = result.metadata_info.get('version', 0)
            return version in self.SUPPORTED_VERSIONS
        return False

    def execute(self, result) -> Dict[str, Any]:
        return {
            "unity_version": "2021.2+",
            "metadata_version": result.metadata_info.get('version', 0) if hasattr(result, 'metadata_info') else 0,
            "generic_sharing": True,
            "method_pointer_tables": True,
        }
