"""
Radare2 Script Generator for GhostDumper v2.2

Generates r2 scripts that rename functions, set types,
and annotate the binary with IL2CPP metadata information.
"""

from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class R2Generator:
    """Generate Radare2 analysis scripts."""

    def __init__(self, result, output_dir: Path, stem: str):
        self.result = result
        self.output_dir = output_dir
        self.stem = stem
        self.lines: List[str] = []

    def generate(self):
        """Generate r2 script file."""
        self._generate_header()
        self._generate_comments()
        self._generate_renames()
        self._generate_flags()
        self._generate_structs()
        self._generate_vtables()

        output_path = self.output_dir / f"{self.stem}_r2patch.r2"
        with open(output_path, "w") as f:
            f.write("\n".join(self.lines))

    def _generate_header(self):
        """Generate script header."""
        self.lines = [
            "# GhostDumper v2.2 — Radare2 Analysis Script",
            f"# Generated: {datetime.now().isoformat()}",
            f"# Classes: {len(self.result.types)}",
            f"# Methods: {len(self.result.methods)}",
            "",
            "# Analysis setup",
            "e anal.in=io.maps",
            "e anal.hasnext=true",
            "",
        ]

    def _generate_comments(self):
        """Generate comments for known addresses."""
        self.lines.extend(["# Class and method comments", ""])

        for type_info in self.result.types:
            # Comment class token at relevant addresses
            token = type_info.get("token", 0)
            if token:
                # Find potential type info address
                pass

    def _generate_renames(self):
        """Generate function rename commands."""
        self.lines.extend(["# Function renames", ""])

        renamed = 0
        for method in self.result.methods:
            addr = method.get("address")
            name = method.get("name")

            if addr and name and not name.startswith("sub_"):
                # Sanitize name for r2
                safe_name = self._sanitize_name(name)
                self.lines.append(f"afn {safe_name} @ 0x{addr:08X}")
                renamed += 1

        self.lines.extend([
            "",
            f"# Total functions renamed: {renamed}",
            "",
        ])

    def _generate_flags(self):
        """Generate flag commands for classes and methods."""
        self.lines.extend(["# Class and method flags", ""])

        for type_info in self.result.types:
            class_name = type_info["name"]
            namespace = type_info.get("namespace", "")

            # Create flag space for class
            full_name = f"{namespace}.{class_name}" if namespace else class_name
            safe_name = self._sanitize_name(full_name)

            for method in type_info.get("methods", []):
                addr = method.get("address")
                if addr:
                    method_name = method.get("name", "unknown")
                    flag_name = f"method.{safe_name}.{method_name}"
                    self.lines.append(f"f {flag_name} @ 0x{addr:08X}")

            # Flag fields
            for field in type_info.get("fields", []):
                offset = field.get("offset", 0)
                field_name = field.get("name", "unknown")
                flag_name = f"field.{safe_name}.{field_name}"
                self.lines.append(f"f {flag_name} @ {offset}")

        self.lines.append("")

    def _generate_structs(self):
        """Generate struct definitions for classes."""
        self.lines.extend(["# Class struct definitions", ""])

        for type_info in self.result.types:
            class_name = type_info["name"]
            safe_name = self._sanitize_name(class_name)

            self.lines.extend([
                f'"td struct {safe_name} {{"',
                f'"  void* vtable;"',
            ])

            for field in type_info.get("fields", []):
                field_name = field.get("name", "field")
                field_type = self._r2_type(field.get("type", "void*"))
                offset = field.get("offset", 0)
                self.lines.append(f'"  {field_type} {field_name}; // 0x{offset:04X}"')

            self.lines.extend([
                f'""}};""',
                f"ts+ {safe_name}",
                "",
            ])

    def _generate_vtables(self):
        """Generate vtable structure definitions."""
        self.lines.extend(["# VTable definitions", ""])

        for type_info in self.result.types:
            vtable_size = type_info.get("vtable_size", 0)
            if vtable_size > 0:
                class_name = type_info["name"]
                safe_name = self._sanitize_name(class_name)

                self.lines.extend([
                    f'"td struct {safe_name}_vtable {{"',
                ])

                for i in range(vtable_size):
                    self.lines.append(f'"  void* method_{i};"')

                self.lines.extend([
                    f'""}};""',
                    f"ts+ {safe_name}_vtable",
                    "",
                ])

    def _sanitize_name(self, name: str) -> str:
        """Sanitize name for r2 compatibility."""
        return name.replace(".", "_").replace("<", "_").replace(">", "_").replace(" ", "_").replace(",", "_")

    def _r2_type(self, il2cpp_type: str) -> str:
        """Map IL2CPP type to r2 type."""
        type_map = {
            "System.Boolean": "bool",
            "System.Byte": "uint8_t",
            "System.SByte": "int8_t",
            "System.Int16": "int16_t",
            "System.UInt16": "uint16_t",
            "System.Int32": "int32_t",
            "System.UInt32": "uint32_t",
            "System.Int64": "int64_t",
            "System.UInt64": "uint64_t",
            "System.Single": "float",
            "System.Double": "double",
            "System.String": "char*",
            "System.Object": "void*",
        }
        return type_map.get(il2cpp_type, "void*")
