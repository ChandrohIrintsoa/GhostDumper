"""Tests for deobfuscator."""
import pytest
from ghostdumper.parsers.deobfuscator import DeobfuscationPipeline, ObfuscationType


class TestDeobfuscator:
    def test_entropy_calculation(self):
        # Random data should have high entropy
        random_data = bytes(range(256)) * 10
        entropy = DeobfuscationPipeline._calculate_entropy(random_data)
        assert entropy > 7.5

        # Uniform data should have low entropy
        uniform_data = b"\x00" * 2560
        entropy = DeobfuscationPipeline._calculate_entropy(uniform_data)
        assert entropy < 0.1

    def test_xor_brute_force(self):
        original = b"Hello, World!"
        key = 0x42
        encrypted = bytes([b ^ key for b in original])

        pipeline = DeobfuscationPipeline(None)
        keys = pipeline.brute_force_xor(encrypted, original[:5])

        assert key in keys
