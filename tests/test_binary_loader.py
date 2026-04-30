"""Tests for binary loader."""
import pytest
from ghostdumper.parsers.binary_loader import BinaryLoader
from ghostdumper.core.config import GhostConfig


class TestBinaryLoader:
    def test_elf_detection(self, tmp_path):
        # Create minimal ELF header
        elf_data = b"\x7fELF\x02\x01\x01\x00" + b"\x00" * 8
        elf_file = tmp_path / "test.so"
        elf_file.write_bytes(elf_data + b"\x00" * 100)

        config = GhostConfig()
        loader = BinaryLoader(str(elf_file), config)
        loader.load()

        assert loader.format == "ELF"
        assert loader.bitness == 64

    def test_pe_detection(self, tmp_path):
        pe_data = b"MZ" + b"\x00" * 58 + b"\x40\x00\x00\x00"
        pe_file = tmp_path / "test.dll"
        pe_file.write_bytes(pe_data + b"\x00" * 200)

        config = GhostConfig()
        loader = BinaryLoader(str(pe_file), config)
        loader.load()

        assert loader.format == "PE"
