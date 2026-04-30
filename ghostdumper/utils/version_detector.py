"""
Unity/IL2CPP Version Detector for GhostDumper v2.2

Detects Unity version and IL2CPP metadata version from binary.
"""

import struct
import re
from typing import Optional, Tuple
from pathlib import Path


class VersionDetector:
    """Detect Unity and IL2CPP versions."""

    UNITY_VERSION_PATTERN = re.compile(rb"(\d{1,2})\.(\d{1,3})\.(\d{1,3})([a-z]\d+)?")
    IL2CPP_VERSION_PATTERN = re.compile(rb"il2cpp_version|global-metadata")

    @classmethod
    def detect_from_binary(cls, data: bytes) -> Tuple[Optional[str], Optional[int]]:
        """Detect Unity version and IL2CPP metadata version from binary."""
        unity_version = cls._detect_unity_version(data)
        il2cpp_version = cls._detect_il2cpp_version(data)
        return unity_version, il2cpp_version

    @classmethod
    def _detect_unity_version(cls, data: bytes) -> Optional[str]:
        """Detect Unity version string from binary."""
        # Search for version strings like "2021.3.15f1"
        matches = cls.UNITY_VERSION_PATTERN.findall(data)
        if matches:
            # Return the most common match
            version_counts = {}
            for match in matches:
                version = b".".join(match[:3]).decode()
                version_counts[version] = version_counts.get(version, 0) + 1

            if version_counts:
                return max(version_counts, key=version_counts.get)

        return None

    @classmethod
    def _detect_il2cpp_version(cls, data: bytes) -> Optional[int]:
        """Detect IL2CPP metadata version from binary."""
        # Look for version-specific patterns
        # v24: specific string patterns
        # v27: different metadata header
        # v29+: newer structures

        # Check for known version signatures
        if b"il2cpp_codegen_metadata" in data:
            return 24
        if b"il2cpp::vm::MetadataCache" in data:
            return 27

        return None

    @classmethod
    def detect_from_metadata(cls, data: bytes) -> Optional[int]:
        """Detect metadata version from metadata file."""
        if len(data) < 4:
            return None

        magic = struct.unpack("<I", data[:4])[0]

        # Known magic values
        if magic == 0xFAB11BAF:
            # Modern metadata, version in header
            if len(data) >= 8:
                return struct.unpack("<I", data[4:8])[0]
        elif 16 <= magic <= 31:
            return magic

        return None

    @classmethod
    def get_metadata_offsets(cls, version: int) -> dict:
        """Get structure offsets for a specific metadata version."""
        # Version-specific offsets
        offsets = {
            24: {
                "string_literal_offset": 0x18,
                "string_literal_count": 0x1C,
                "string_literal_data_offset": 0x20,
            },
            27: {
                "string_literal_offset": 0x18,
                "string_literal_count": 0x1C,
                "string_literal_data_offset": 0x20,
            },
            29: {
                "string_literal_offset": 0x18,
                "string_literal_count": 0x1C,
                "string_literal_data_offset": 0x20,
            },
        }

        return offsets.get(version, offsets.get(24, {}))
