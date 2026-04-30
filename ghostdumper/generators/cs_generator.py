"""
C# Dump Generator for GhostDumper v2.2

Generates dump.cs style output with full class/method/field
information including RVA addresses.
"""

from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class CsGenerator:
    """Generate C# dump.cs output."""

    def __init__(self, result, output_dir: Path, stem: str):
        self.result = result
        self.output_dir = output_dir
        self.stem = stem
        self.lines: List[str] = []

    def generate(self):
        """Generate dump.cs file."""
        self._generate_header()
        self._generate_assemblies()

        output_path = self.output_dir / f"{self.stem}_dump.cs"
        with open(output_path, "w") as f:
            f.write("\n".join(self.lines))

    def _generate_header(self):
        """Generate file header."""
        self.lines = [
            "// GhostDumper v2.2 — IL2CPP C# Dump",
            f"// Generated: {datetime.now().isoformat()}",
            f"// Binary: {self.result.binary_info.get('format', 'Unknown')} {self.result.binary_info.get('arch', 'Unknown')}",
            f"// Base: 0x{self.result.binary_info.get('base_address', 0):08X}",
            "",
            "using System;",
            "using System.Collections.Generic;",
            "",
        ]

    def _generate_assemblies(self):
        """Generate assembly and class definitions."""
        # Group types by namespace
        namespaces: Dict[str, List[Dict]] = {}
        for type_info in self.result.types:
            ns = type_info.get("namespace", "")
            if ns not in namespaces:
                namespaces[ns] = []
            namespaces[ns].append(type_info)

        for ns, types in sorted(namespaces.items()):
            if ns:
                self.lines.extend([f"namespace {ns} {{", ""])

            for type_info in types:
                self._generate_class(type_info)

            if ns:
                self.lines.extend(["", "}", ""])

    def _generate_class(self, type_info: Dict[str, Any]):
        """Generate single class definition."""
        name = type_info["name"]
        parent = type_info.get("parent")
        flags = type_info.get("flags", 0)
        token = type_info.get("token", 0)

        # Class attributes
        attrs = []
        if flags & 0x1: attrs.append("public")
        elif flags & 0x2: attrs.append("private")
        if flags & 0x80: attrs.append("abstract")
        if flags & 0x100: attrs.append("sealed")

        attr_str = " ".join(attrs) if attrs else "internal"
        inheritance = f" : {parent}" if parent else ""

        self.lines.extend([
            f"    // Token: 0x{token:08X}",
            f"    {attr_str} class {name}{inheritance} {{",
        ])

        # Fields
        for field in type_info.get("fields", []):
            self._generate_field(field)

        # Methods
        for method in type_info.get("methods", []):
            self._generate_method(method)

        self.lines.extend(["    }", ""])

    def _generate_field(self, field: Dict[str, Any]):
        """Generate field definition."""
        name = field["name"]
        type_str = self._cs_type(field["type"])
        offset = field.get("offset", 0)
        flags = field.get("flags", 0)

        attrs = []
        if flags & 0x1: attrs.append("public")
        elif flags & 0x2: attrs.append("private")
        if flags & 0x10: attrs.append("static")
        if flags & 0x40: attrs.append("readonly")

        attr_str = " ".join(attrs) if attrs else "private"

        self.lines.append(
            f"        {attr_str} {type_str} {name}; // 0x{offset:04X}"
        )

    def _generate_method(self, method: Dict[str, Any]):
        """Generate method definition."""
        name = method["name"]
        ret_type = self._cs_type(method.get("return_type", "void"))
        params = ", ".join(
            f"{self._cs_type(p)} arg{i}"
            for i, p in enumerate(method.get("parameters", []))
        )
        addr = method.get("address")
        token = method.get("token", 0)
        flags = method.get("flags", 0)
        slot = method.get("slot", -1)

        attrs = []
        if flags & 0x1: attrs.append("public")
        elif flags & 0x2: attrs.append("private")
        if flags & 0x10: attrs.append("static")
        if flags & 0x400: attrs.append("virtual")
        if flags & 0x800: attrs.append("abstract")

        attr_str = " ".join(attrs) if attrs else "private"
        addr_str = f" // RVA: 0x{addr:08X}" if addr else ""
        slot_str = f" Slot: {slot}" if slot >= 0 else ""

        self.lines.extend([
            f"        // Token: 0x{token:08X}{slot_str}",
            f"        {attr_str} {ret_type} {name}({params});{addr_str}",
        ])

    def _cs_type(self, il2cpp_type: str) -> str:
        """Map IL2CPP type to C# type."""
        type_map = {
            "System.Void": "void",
            "System.Boolean": "bool",
            "System.Byte": "byte",
            "System.SByte": "sbyte",
            "System.Int16": "short",
            "System.UInt16": "ushort",
            "System.Int32": "int",
            "System.UInt32": "uint",
            "System.Int64": "long",
            "System.UInt64": "ulong",
            "System.Single": "float",
            "System.Double": "double",
            "System.String": "string",
            "System.Object": "object",
        }
        return type_map.get(il2cpp_type, il2cpp_type)
