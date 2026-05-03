"""
miHoYo Plugin for GhostDumper v2.2

Handles miHoYo-specific encryption and obfuscation patterns
found in games like Genshin Impact, Honkai Star Rail, etc.
"""

import struct
from typing import Dict, Any
from ..plugin_manager import DecryptorPlugin


class MiHoYoPlugin(DecryptorPlugin):
    """miHoYo custom encryption handler."""

    name = "mihoyo"
    version = "1.0"
    author = "GhostDumper Community"
    description = "Handles miHoYo XOR+ROT encryption patterns"

    XOR_KEYS = [0xA3, 0x5C, 0x7F, 0xE1]

    def detect(self, data: bytes) -> float:
        """Detect miHoYo encryption with confidence score."""
        confidence = 0.0

        if b"miHoYo" in data[:1024] or b"mihoyo" in data[:1024]:
            confidence += 0.3

        if len(data) > 0x100:
            header = data[:0x20]
            non_printable = sum(1 for b in header if b < 0x20 or b > 0x7E)
            if non_printable > 10:
                confidence += 0.4

        from ...parsers.deobfuscator import DeobfuscationPipeline
        entropy = DeobfuscationPipeline._calculate_entropy(data[:4096])
        if entropy > 7.8:
            confidence += 0.3

        return min(confidence, 1.0)

    def decrypt(self, data: bytes, params: Dict[str, Any]) -> bytes:
        """Decrypt miHoYo-encrypted data."""
        for key in self.XOR_KEYS:
            candidate = bytes([b ^ key for b in data[:4]])
            if self._is_valid_header(candidate):
                return bytes([b ^ key for b in data])
        return self._decrypt_rotating_xor(data)

    def _is_valid_header(self, header: bytes) -> bool:
        if len(header) < 4:
            return False
        magic = struct.unpack("<I", header[:4])[0]
        known_magics = [0xFAB11BAF, 0x5] + list(range(0x16, 0x20))
        return magic in known_magics

    def _decrypt_rotating_xor(self, data: bytes) -> bytes:
        key = [0xA3, 0x5C, 0x7F, 0xE1, 0x92, 0x38, 0xD4, 0x6B]
        return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

    def execute(self, result) -> Dict[str, Any]:
        return {"detected": False, "confidence": 0.0, "decrypted": False}
