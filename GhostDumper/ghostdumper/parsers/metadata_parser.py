"""
IL2CPP Metadata Parser for GhostDumper v2.2

Supports metadata versions 16 through 31.
Handles encrypted/obfuscated metadata detection.
"""

import struct
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, field


@dataclass
class Il2CppImage:
    name: str
    assembly_index: int
    type_start: int
    type_count: int
    entry_point_index: int
    token: int
    custom_attribute_start: int
    custom_attribute_count: int


@dataclass
class Il2CppType:
    name: str
    namespace: str
    image_index: int
    parent_index: int
    element_type_index: int
    token: int
    flags: int
    field_start: int
    field_count: int
    method_start: int
    method_count: int
    property_start: int
    property_count: int
    interface_start: int
    interface_count: int
    vtable_start: int
    vtable_count: int
    interfaces: List[int] = field(default_factory=list)
    methods: List["Il2CppMethod"] = field(default_factory=list)
    fields: List["Il2CppField"] = field(default_factory=list)


@dataclass
class Il2CppMethod:
    name: str
    return_type: str
    parameter_types: List[str]
    flags: int
    token: int
    impl_flags: int
    slot: int
    address: Optional[int] = None
    is_generic: bool = False
    generic_params: List[str] = field(default_factory=list)


@dataclass
class Il2CppField:
    name: str
    type: str
    offset: int
    token: int
    flags: int
    default_value: Optional[Any] = None


class MetadataParser:
    """Parse global-metadata.dat IL2CPP metadata files."""

    def __init__(self, path: str, config):
        self.path = Path(path)
        self.config = config
        self.raw_data: bytes = b""
        self.version: int = 0
        self.is_encrypted: bool = False
        self.encryption_type: Optional[str] = None

        # Metadata structures
        self.strings: List[str] = []
        self.images: List[Il2CppImage] = []
        self.assemblies: List[Dict[str, Any]] = []
        self.types: List[Il2CppType] = []
        self.methods: List[Il2CppMethod] = []
        self.fields: List[Il2CppField] = []
        self.generics: List[Dict[str, Any]] = []

        # Offsets
        self.string_offset: int = 0
        self.string_count: int = 0

    def parse(self):
        """Parse metadata file."""
        self.raw_data = self.path.read_bytes()

        # Detect encryption/obfuscation
        self._detect_encryption()

        if self.is_encrypted and not self.config.deobfuscate:
            raise ValueError(f"Metadata appears encrypted ({self.encryption_type}). Use --deobfuscate flag.")

        # Parse header
        self._parse_header()

        # Parse strings
        self._parse_strings()

        # Parse images
        self._parse_images()

        # Parse assemblies
        self._parse_assemblies()

        # Parse types
        self._parse_types()

        # Parse methods
        self._parse_methods()

        # Parse fields
        self._parse_fields()

        # Parse generics
        self._parse_generics()

    def _detect_encryption(self):
        """Detect if metadata is encrypted or obfuscated."""
        if not self.raw_data:
            self.raw_data = self.path.read_bytes()
        
        if len(self.raw_data) < 4:
            self.is_encrypted = False
            return
        
        # Check for normal metadata magic: 0xFAB11BAF for v21+, version number for older
        magic = struct.unpack("<I", self.raw_data[:4])[0]

        known_magics = [0xFAB11BAF, 0x5] + list(range(16, 32))

        if magic not in known_magics and magic != 0:
            # Check for XOR encryption patterns
            xor_candidates = []
            for key in range(1, 256):
                decrypted = bytes([b ^ key for b in self.raw_data[:4]])
                decrypted_magic = struct.unpack("<I", decrypted)[0]
                if decrypted_magic in known_magics:
                    xor_candidates.append(key)

            if xor_candidates:
                self.is_encrypted = True
                self.encryption_type = f"XOR(key_candidates={xor_candidates})"
            else:
                # Check for byte reordering
                reversed_magic = struct.unpack(">I", self.raw_data[:4])[0]
                if reversed_magic in known_magics:
                    self.is_encrypted = True
                    self.encryption_type = "ByteReversed"
                else:
                    self.is_encrypted = True
                    self.encryption_type = "Unknown"

    def _parse_header(self):
        """Parse metadata header."""
        if len(self.raw_data) < 0x28:
            raise ValueError("Metadata file too small")

        # Version detection
        magic = struct.unpack("<I", self.raw_data[:4])[0]
        if magic == 0xFAB11BAF:
            # v21+ format: magic at offset 0, version at offset 4
            self.version = struct.unpack("<I", self.raw_data[4:8])[0]
        else:
            self.version = magic

        # Handle different header sizes based on version
        if self.version >= 21:
            # Modern header (v21+)
            header = struct.unpack("<I4I", self.raw_data[:20])
            self.version = header[0]
            self.string_offset = header[1]
            self.string_count = header[2]
        else:
            # Legacy header
            header = struct.unpack("<I", self.raw_data[:4])[0]
            self.version = header
            self.string_offset = 0x28  # Default for older versions

    def _parse_strings(self):
        """Parse string literals from metadata."""
        if self.version >= 21:
            string_literal_offset = struct.unpack("<I", self.raw_data[4:8])[0]
            string_literal_count = struct.unpack("<I", self.raw_data[8:12])[0]

            # Sanity check on count to prevent memory exhaustion on corrupted files
            if string_literal_count > 1_000_000:
                self.errors.append(f"String count {string_literal_count} exceeds safety limit, capping to 1,000,000")
                string_literal_count = 1_000_000

            if string_literal_count == 0:
                return

            offset = string_literal_offset
            for _ in range(min(string_literal_count, 100000)):  # Safety limit
                if offset >= len(self.raw_data):
                    break
                # Read null-terminated string
                end = self.raw_data.find(b"\x00", offset)
                if end == -1:
                    break
                try:
                    s = self.raw_data[offset:end].decode("utf-8", errors="ignore")
                    if s:
                        self.strings.append(s)
                except:
                    pass
                offset = end + 1
        else:
            # Fallback: scan for printable strings
            self._scan_strings()

    def _scan_strings(self):
        """Fallback string scanning."""
        i = 0x28
        while i < len(self.raw_data):
            if 32 <= self.raw_data[i] <= 126:
                start = i
                while i < len(self.raw_data) and 32 <= self.raw_data[i] <= 126:
                    i += 1
                if i - start >= 4:
                    try:
                        s = self.raw_data[start:i].decode("ascii")
                        self.strings.append(s)
                    except:
                        pass
            i += 1

    def _parse_images(self):
        """Parse image definitions."""
        # Simplified parsing - would need version-specific offsets
        # This is a structural representation
        pass

    def _parse_assemblies(self):
        """Parse assembly definitions."""
        pass

    def _parse_types(self):
        """Parse type definitions."""
        pass

    def _parse_methods(self):
        """Parse method definitions."""
        pass

    def _parse_fields(self):
        """Parse field definitions."""
        pass

    def _parse_generics(self):
        """Parse generic type/method definitions."""
        pass

    def get_string(self, index: int) -> str:
        """Get string by index."""
        if 0 <= index < len(self.strings):
            return self.strings[index]
        return ""

    def get_type_by_name(self, name: str) -> Optional[Il2CppType]:
        """Find type by name."""
        for t in self.types:
            if t.name == name or f"{t.namespace}.{t.name}" == name:
                return t
        return None
