"""Tests for metadata parser."""
import pytest
import struct
from ghostdumper.parsers.metadata_parser import MetadataParser
from ghostdumper.core.config import GhostConfig


class TestMetadataParser:
    def test_version_detection(self, tmp_path):
        # Create minimal metadata with v24 header
        meta_data = struct.pack("<I", 24) + b"\x00" * 100
        meta_file = tmp_path / "global-metadata.dat"
        meta_file.write_bytes(meta_data)

        config = GhostConfig()
        parser = MetadataParser(str(meta_file), config)
        parser.parse()

        assert parser.version == 24

    def test_encryption_detection(self, tmp_path):
        # Create encrypted-looking metadata
        meta_data = b"\xff\xfe\xfd\xfc" + b"\x00" * 100
        meta_file = tmp_path / "global-metadata.dat"
        meta_file.write_bytes(meta_data)

        config = GhostConfig()
        parser = MetadataParser(str(meta_file), config)

        # Should detect encryption
        parser._detect_encryption()
        assert parser.is_encrypted == True
