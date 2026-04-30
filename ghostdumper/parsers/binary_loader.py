"""
Multi-format binary loader for GhostDumper v2.2

Supports: ELF (32/64), PE (32/64), Mach-O (32/64/Fat), NSO, WASM
"""

import struct
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass

from elftools.elf.elffile import ELFFile
from elftools.elf.sections import SymbolTableSection
from elftools.elf.descriptions import describe_sh_type


@dataclass
class BinarySection:
    name: str
    virtual_address: int
    offset: int
    size: int
    permissions: str


class BinaryLoader:
    """Universal binary loader with format auto-detection."""

    MAGIC_ELF = b"\x7fELF"
    MAGIC_PE = b"MZ"
    MAGIC_MACHO_32 = 0xfeedface
    MAGIC_MACHO_64 = 0xfeedfacf
    MAGIC_MACHO_FAT = 0xcafebabe
    MAGIC_NSO = 0x304f534e  # "NSO0"
    MAGIC_WASM = b"\x00asm"

    def __init__(self, path: str, config):
        self.path = Path(path)
        self.config = config
        self.raw_data: bytes = b""
        self.format: str = "Unknown"
        self.arch: str = "Unknown"
        self.bitness: int = 0
        self.entry_point: Optional[int] = None
        self.base_address: int = 0
        self.size: int = 0
        self.sections: List[Dict[str, Any]] = []
        self.symbols: List[Dict[str, Any]] = []
        self.exports: List[Dict[str, Any]] = []
        self.imports: List[Dict[str, Any]] = []

    def load(self):
        """Load and analyze binary file."""
        self.raw_data = self.path.read_bytes()
        self.size = len(self.raw_data)

        # Auto-detect format
        self._detect_format()

        # Parse based on format
        if self.format == "ELF":
            self._parse_elf()
        elif self.format == "PE":
            self._parse_pe()
        elif self.format == "Mach-O":
            self._parse_macho()
        elif self.format == "NSO":
            self._parse_nso()
        elif self.format == "WASM":
            self._parse_wasm()
        else:
            raise ValueError(f"Unsupported binary format: {self.format}")

    def _detect_format(self):
        """Detect binary format from magic bytes."""
        if self.raw_data[:4] == self.MAGIC_ELF:
            self.format = "ELF"
        elif self.raw_data[:2] == self.MAGIC_PE:
            self.format = "PE"
        elif struct.unpack("<I", self.raw_data[:4])[0] in (self.MAGIC_MACHO_32, self.MAGIC_MACHO_64):
            self.format = "Mach-O"
        elif struct.unpack(">I", self.raw_data[:4])[0] == self.MAGIC_MACHO_FAT:
            self.format = "Mach-O"
        elif struct.unpack("<I", self.raw_data[:4])[0] == self.MAGIC_NSO:
            self.format = "NSO"
        elif self.raw_data[:4] == self.MAGIC_WASM:
            self.format = "WASM"

    def _parse_elf(self):
        """Parse ELF file using pyelftools."""
        elf = ELFFile(open(self.path, "rb"))

        self.bitness = 64 if elf.elfclass == 64 else 32
        self.arch = self._describe_elf_arch(elf["e_machine"])
        self.entry_point = elf["e_entry"]

        # Find base address from first PT_LOAD segment
        for segment in elf.iter_segments():
            if segment["p_type"] == "PT_LOAD":
                self.base_address = segment["p_vaddr"] - segment["p_offset"]
                break

        # Parse sections
        for section in elf.iter_sections():
            self.sections.append({
                "name": section.name,
                "type": describe_sh_type(section["sh_type"]),
                "address": section["sh_addr"],
                "offset": section["sh_offset"],
                "size": section["sh_size"],
                "flags": section["sh_flags"],
            })

        # Parse symbols
        for section in elf.iter_sections():
            if isinstance(section, SymbolTableSection):
                for symbol in section.iter_symbols():
                    if symbol.name:
                        self.symbols.append({
                            "name": symbol.name,
                            "address": symbol["st_value"],
                            "size": symbol["st_size"],
                            "type": symbol["st_info"]["type"],
                            "bind": symbol["st_info"]["bind"],
                            "section": symbol["st_shndx"],
                        })

        elf.stream.close()

    def _parse_pe(self):
        """Parse PE file."""
        # PE parsing implementation
        dos_header = struct.unpack("<2s58xH", self.raw_data[:64])
        pe_offset = dos_header[1]

        pe_sig = self.raw_data[pe_offset:pe_offset+4]
        if pe_sig != b"PE\x00\x00":
            raise ValueError("Invalid PE signature")

        coff_header = struct.unpack("<2H3I2H", self.raw_data[pe_offset+4:pe_offset+24])
        machine = coff_header[0]
        num_sections = coff_header[1]

        self.bitness = 64 if machine == 0x8664 else 32
        self.arch = "x64" if self.bitness == 64 else "x86"

        optional_header_offset = pe_offset + 24
        magic = struct.unpack("<H", self.raw_data[optional_header_offset:optional_header_offset+2])[0]

        if magic == 0x10b:  # PE32
            self.entry_point = struct.unpack("<I", self.raw_data[optional_header_offset+16:optional_header_offset+20])[0]
            self.base_address = struct.unpack("<I", self.raw_data[optional_header_offset+28:optional_header_offset+32])[0]
        elif magic == 0x20b:  # PE32+
            self.entry_point = struct.unpack("<I", self.raw_data[optional_header_offset+16:optional_header_offset+20])[0]
            self.base_address = struct.unpack("<Q", self.raw_data[optional_header_offset+24:optional_header_offset+32])[0]

        # Parse sections
        section_table_offset = optional_header_offset + (224 if magic == 0x20b else 96)
        for i in range(num_sections):
            sec_offset = section_table_offset + i * 40
            name = self.raw_data[sec_offset:sec_offset+8].rstrip(b"\x00").decode("ascii", errors="ignore")
            vsize, vaddr, raw_size, raw_offset = struct.unpack("<4I", self.raw_data[sec_offset+8:sec_offset+24])
            chars = struct.unpack("<I", self.raw_data[sec_offset+36:sec_offset+40])[0]

            perms = ""
            if chars & 0x20000000: perms += "X"
            if chars & 0x40000000: perms += "W"
            if chars & 0x80000000: perms += "R"

            self.sections.append({
                "name": name,
                "address": vaddr,
                "offset": raw_offset,
                "size": raw_size,
                "flags": chars,
            })

    def _parse_macho(self):
        """Parse Mach-O file."""
        # Mach-O parsing stub
        magic = struct.unpack("<I", self.raw_data[:4])[0]
        if magic == self.MAGIC_MACHO_64:
            self.bitness = 64
            self.arch = "ARM64"  # Simplified
            header = struct.unpack("<I4I2I", self.raw_data[:32])
            self.entry_point = 0  # Would need to parse LC_MAIN
        elif magic == self.MAGIC_MACHO_32:
            self.bitness = 32
            self.arch = "ARM"

    def _parse_nso(self):
        """Parse Nintendo Switch NSO file."""
        self.bitness = 64
        self.arch = "ARM64"
        # NSO0 header parsing
        header = struct.unpack("<I3I", self.raw_data[:16])
        flags = header[1]
        # Decompress segments if needed

    def _parse_wasm(self):
        """Parse WebAssembly file."""
        self.bitness = 32
        self.arch = "WASM"
        version = struct.unpack("<I", self.raw_data[4:8])[0]

    def _describe_elf_arch(self, machine: int) -> str:
        """Map ELF machine type to architecture name."""
        arch_map = {
            0x28: "ARM",
            0xB7: "AArch64",
            0x03: "x86",
            0x3E: "x64",
            0x08: "MIPS",
            0x14: "PowerPC",
            0x15: "PowerPC64",
        }
        return arch_map.get(machine, f"Unknown(0x{machine:x})")

    def read_at(self, offset: int, size: int) -> bytes:
        """Read bytes at file offset."""
        return self.raw_data[offset:offset+size]

    def read_va(self, va: int, size: int) -> bytes:
        """Read bytes at virtual address."""
        for sec in self.sections:
            if sec["address"] <= va < sec["address"] + sec["size"]:
                file_offset = sec["offset"] + (va - sec["address"])
                return self.raw_data[file_offset:file_offset+size]
        return b""

    def va_to_file(self, va: int) -> Optional[int]:
        """Convert virtual address to file offset."""
        for sec in self.sections:
            if sec["address"] <= va < sec["address"] + sec["size"]:
                return sec["offset"] + (va - sec["address"])
        return None
