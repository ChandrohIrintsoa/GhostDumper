"""
C++ Scaffold Generator for GhostDumper v2.2

Generates C++ header and source files with class definitions,
method signatures, field offsets, and vtable structures.
"""

from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class CppGenerator:
    """Generate C++ scaffolding from IL2CPP analysis."""

    def __init__(self, result, output_dir: Path, stem: str):
        self.result = result
        self.output_dir = output_dir
        self.stem = stem
        self.header_lines: List[str] = []
        self.source_lines: List[str] = []

    def generate(self):
        """Generate C++ output files."""
        self._generate_header()
        self._generate_source()

        # Write header
        header_path = self.output_dir / f"{self.stem}_classes.h"
        with open(header_path, "w") as f:
            f.write("\n".join(self.header_lines))

        # Write source
        source_path = self.output_dir / f"{self.stem}_classes.cpp"
        with open(source_path, "w") as f:
            f.write("\n".join(self.source_lines))

    def _generate_header(self):
        """Generate C++ header file."""
        self.header_lines = [
            f"// GhostDumper v2.2 — C++ Class Scaffold",
            f"// Generated: {datetime.now().isoformat()}",
            f"// Binary: {self.result.binary_info.get('format', 'Unknown')} {self.result.binary_info.get('arch', 'Unknown')}",
            f"// Classes: {len(self.result.types)}",
            "",
            "#pragma once",
            "",
            "#include <cstdint>",
            "#include <string>",
            "#include <vector>",
            "",
            "namespace il2cpp {",
            "",
            "// Forward declarations",
        ]

        # Forward declarations
        for type_info in self.result.types:
            name = type_info["name"]
            self.header_lines.append(f"class {name};")

        self.header_lines.extend(["", "// Class definitions"])

        # Class definitions
        for type_info in self.result.types:
            self._generate_class_header(type_info)

        self.header_lines.extend(["", "} // namespace il2cpp", ""])

    def _generate_class_header(self, type_info: Dict[str, Any]):
        """Generate header for a single class."""
        name = type_info["name"]
        namespace = type_info.get("namespace", "")
        parent = type_info.get("parent")

        # Namespace wrapper
        if namespace:
            self.header_lines.extend([f"", f"namespace {namespace} {{"])

        # Class declaration
        inheritance = f" : public {parent}" if parent else ""
        self.header_lines.extend([
            f"",
            f"class {name}{inheritance} {{",
            f"public:",
            f"    static constexpr uint32_t TOKEN = 0x{type_info.get('token', 0):08X};",
            f"    static constexpr uint32_t FLAGS = 0x{type_info.get('flags', 0):08X};",
        ])

        # Fields
        fields = type_info.get("fields", [])
        if fields:
            self.header_lines.append("    // Fields")
            for field in fields:
                self._generate_field(field)

        # Methods
        methods = type_info.get("methods", [])
        if methods:
            self.header_lines.append("    // Methods")
            for method in methods:
                self._generate_method_decl(method)

        # VTable
        vtable_size = type_info.get("vtable_size", 0)
        if vtable_size > 0:
            self.header_lines.extend([
                f"    // VTable ({vtable_size} entries)",
                f"    void** vtable[{vtable_size}];",
            ])

        self.header_lines.extend(["};", ""])

        if namespace:
            self.header_lines.append(f"}} // namespace {namespace}")

    def _generate_field(self, field: Dict[str, Any]):
        """Generate field declaration."""
        name = field["name"]
        type_str = self._cpp_type(field["type"])
        offset = field.get("offset", 0)

        self.header_lines.append(
            f"    {type_str} {name}; // Offset: 0x{offset:04X}"
        )

    def _generate_method_decl(self, method: Dict[str, Any]):
        """Generate method declaration."""
        name = method["name"]
        ret_type = self._cpp_type(method.get("return_type", "void"))
        params = ", ".join(
            f"{self._cpp_type(p)} arg{i}"
            for i, p in enumerate(method.get("parameters", []))
        )

        addr = method.get("address")
        addr_str = f" // Address: 0x{addr:08X}" if addr else ""

        self.header_lines.append(
            f"    {ret_type} {name}({params});{addr_str}"
        )

    def _generate_source(self):
        """Generate C++ source file with implementations."""
        self.source_lines = [
            f"// GhostDumper v2.2 — C++ Class Implementations",
            f"// Generated: {datetime.now().isoformat()}",
            "",
            f'#include "{self.stem}_classes.h"',
            "",
            "namespace il2cpp {",
            "",
        ]

        # Method implementations
        for type_info in self.result.types:
            for method in type_info.get("methods", []):
                self._generate_method_impl(type_info, method)

        self.source_lines.extend(["", "} // namespace il2cpp", ""])

    def _generate_method_impl(self, type_info: Dict[str, Any], method: Dict[str, Any]):
        """Generate method implementation stub."""
        class_name = type_info["name"]
        namespace = type_info.get("namespace", "")
        name = method["name"]
        ret_type = self._cpp_type(method.get("return_type", "void"))
        params = ", ".join(
            f"{self._cpp_type(p)} arg{i}"
            for i, p in enumerate(method.get("parameters", []))
        )

        prefix = f"{namespace}::" if namespace else ""

        self.source_lines.extend([
            f"",
            f"{ret_type} {prefix}{class_name}::{name}({params}) {{",
            f"    // TODO: Implement",
            f"    // Token: 0x{method.get('token', 0):08X}",
            f"    // Address: 0x{method.get('address', 0):08X}",
            f"    return {self._default_return(ret_type)};",
            f"}}",
        ])

    def _cpp_type(self, il2cpp_type: str) -> str:
        """Map IL2CPP type to C++ type."""
        type_map = {
            "System.Void": "void",
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
            "System.String": "std::string",
            "System.Object": "void*",
        }
        return type_map.get(il2cpp_type, il2cpp_type.replace(".", "::"))

    def _default_return(self, cpp_type: str) -> str:
        """Get default return value for type."""
        if cpp_type == "void":
            return ""
        elif cpp_type == "bool":
            return "false"
        elif cpp_type in ("int8_t", "int16_t", "int32_t", "int64_t", "float", "double"):
            return "0"
        elif cpp_type.startswith("uint"):
            return "0"
        elif cpp_type == "std::string":
            return '""'
        else:
            return "nullptr"
