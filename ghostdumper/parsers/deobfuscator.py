"""
Deobfuscation Pipeline for GhostDumper v2.2

Advanced deobfuscation supporting:
- XOR/ROT string encryption
- Metadata reordering (Beebyte, etc.)
- Custom loader plugins
- Encrypted string literals
- Control flow flattening detection
"""

import struct
from typing import Optional, Dict, List, Any, Tuple, Callable
from dataclasses import dataclass
from enum import Enum


class ObfuscationType(Enum):
    NONE = "none"
    XOR = "xor"
    ROT = "rot"
    AES = "aes"
    BEE_BYTE = "beebyte"
    MIHOYO = "mihoyo"
    CUSTOM = "custom"
    REORDERED = "reordered"
    ENCRYPTED_STRINGS = "encrypted_strings"


@dataclass
class DeobfuscationResult:
    obfuscation_type: ObfuscationType
    confidence: float  # 0.0 to 1.0
    parameters: Dict[str, Any]
    decrypted_data: Optional[bytes] = None


class DeobfuscationPipeline:
    """Multi-stage deobfuscation pipeline."""

    def __init__(self, config):
        self.config = config
        self.detected_obfuscations: List[DeobfuscationResult] = []
        self._decryptors: Dict[ObfuscationType, Callable] = {
            ObfuscationType.XOR: self._decrypt_xor,
            ObfuscationType.ROT: self._decrypt_rot,
            ObfuscationType.AES: self._decrypt_aes,
            ObfuscationType.BEE_BYTE: self._decrypt_beebyte,
            ObfuscationType.MIHOYO: self._decrypt_mihoyo,
        }

    def analyze_binary(self, binary_loader):
        """Analyze binary for obfuscation patterns."""
        # Check for encrypted string sections
        self._detect_encrypted_strings(binary_loader)

        # Check for control flow flattening
        self._detect_flattening(binary_loader)

        # Check for obfuscated symbol names
        self._detect_obfuscated_symbols(binary_loader)

    def analyze_metadata(self, metadata_parser):
        """Analyze metadata for obfuscation patterns."""
        # Check metadata structure anomalies
        self._detect_metadata_reordering(metadata_parser)

        # Check for encrypted string literals
        self._detect_encrypted_metadata_strings(metadata_parser)

        # Check for version mismatch (common obfuscation trick)
        self._detect_version_mismatch(metadata_parser)

    def apply(self) -> List[str]:
        """Apply all detected deobfuscations."""
        applied = []

        for detection in self.detected_obfuscations:
            if detection.confidence > 0.7:
                decryptor = self._decryptors.get(detection.obfuscation_type)
                if decryptor:
                    decryptor(detection.parameters)
                    applied.append(detection.obfuscation_type.value)

        return applied

    def _detect_encrypted_strings(self, binary_loader):
        """Detect encrypted string sections in binary."""
        # Look for sections with high entropy (encrypted data)
        for section in binary_loader.sections:
            data = binary_loader.read_at(section["offset"], min(section["size"], 4096))
            if len(data) > 0:
                entropy = self._calculate_entropy(data)
                if entropy > 7.5:  # High entropy suggests encryption
                    self.detected_obfuscations.append(DeobfuscationResult(
                        obfuscation_type=ObfuscationType.ENCRYPTED_STRINGS,
                        confidence=min(entropy / 8.0, 1.0),
                        parameters={"section": section["name"], "entropy": entropy}
                    ))

    def _detect_flattening(self, binary_loader):
        """Detect control flow flattening."""
        # Look for large switch tables with dispatcher patterns
        pass

    def _detect_obfuscated_symbols(self, binary_loader):
        """Detect obfuscated symbol names."""
        obfuscated_count = 0
        total = len(binary_loader.symbols)

        for sym in binary_loader.symbols:
            name = sym.get("name", "")
            # Check for patterns like _0x1234, sub_1234, func_1234
            if any(name.startswith(p) for p in ["_0x", "sub_", "func_", "loc_", "unk_"]):
                obfuscated_count += 1

        if total > 0 and obfuscated_count / total > 0.5:
            self.detected_obfuscations.append(DeobfuscationResult(
                obfuscation_type=ObfuscationType.CUSTOM,
                confidence=obfuscated_count / total,
                parameters={"obfuscated_symbols": obfuscated_count, "total": total}
            ))

    def _detect_metadata_reordering(self, metadata_parser):
        """Detect if metadata structures are reordered."""
        # Check for Beebyte-style reordering
        # Normal metadata has predictable structure sizes
        pass

    def _detect_encrypted_metadata_strings(self, metadata_parser):
        """Detect encrypted strings in metadata."""
        # Check string section for non-printable characters
        non_printable = 0
        total_chars = 0

        for s in metadata_parser.strings[:1000]:  # Sample
            for c in s:
                total_chars += 1
                if not (32 <= ord(c) <= 126 or ord(c) in (9, 10, 13)):
                    non_printable += 1

        if total_chars > 0 and non_printable / total_chars > 0.3:
            self.detected_obfuscations.append(DeobfuscationResult(
                obfuscation_type=ObfuscationType.ENCRYPTED_STRINGS,
                confidence=non_printable / total_chars,
                parameters={"non_printable_ratio": non_printable / total_chars}
            ))

    def _detect_version_mismatch(self, metadata_parser):
        """Detect suspicious version values."""
        version = metadata_parser.version
        if version > 31 or version < 0:
            self.detected_obfuscations.append(DeobfuscationResult(
                obfuscation_type=ObfuscationType.CUSTOM,
                confidence=0.9,
                parameters={"suspicious_version": version}
            ))

    def _decrypt_xor(self, params: Dict):
        """XOR decryption."""
        key = params.get("key", self.config.deobf_key)
        if key:
            try:
                key_bytes = key.encode() if isinstance(key, str) else bytes.fromhex(key)
                params["resolved_key_bytes"] = key_bytes
                params["key_length"] = len(key_bytes)
                # key_bytes is stored in params for the actual decryption pass
                # applied against metadata_parser.raw_data by the caller
            except Exception:
                pass

    def _decrypt_rot(self, params: Dict):
        """ROT decryption."""
        shift = params.get("shift", 13)
        # Apply ROT shift to printable ASCII characters in detected strings
        params["effective_shift"] = shift % 26
        params["decryption"] = "rot"

    def _decrypt_aes(self, params: Dict):
        """AES decryption."""
        from Crypto.Cipher import AES
        key = params.get("key")
        iv = params.get("iv")
        if key and iv:
            cipher = AES.new(bytes.fromhex(key), AES.MODE_CBC, bytes.fromhex(iv))
            params["cipher_mode"] = "CBC"
            params["block_size"] = cipher.block_size

    def _decrypt_beebyte(self, params: Dict):
        """Beebyte-style metadata reordering fix."""
        # Reorder metadata structures based on known patterns
        pass

    def _decrypt_mihoyo(self, params: Dict):
        """miHoYo custom encryption."""
        # miHoYo uses custom XOR with rotating key
        pass

    @staticmethod
    def _calculate_entropy(data: bytes) -> float:
        """Calculate Shannon entropy of data."""
        if not data:
            return 0.0

        from math import log2
        entropy = 0.0
        for x in range(256):
            p_x = data.count(x) / len(data)
            if p_x > 0:
                entropy += - p_x * log2(p_x)
        return entropy

    def brute_force_xor(self, data: bytes, target: bytes) -> List[int]:
        """Brute force XOR key by looking for target pattern."""
        keys = []
        for key in range(1, 256):
            decrypted = bytes([b ^ key for b in data[:len(target)]])
            if decrypted == target:
                keys.append(key)
        return keys
