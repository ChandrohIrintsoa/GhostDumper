"""
Ghidra Script Generator for GhostDumper v2.2

Generates Python scripts for Ghidra that create data types,
rename functions, and set comments based on IL2CPP metadata.
"""

from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class GhidraGenerator:
    """Generate Ghidra import scripts."""

    def __init__(self, result, output_dir: Path, stem: str):
        self.result = result
        self.output_dir = output_dir
        self.stem = stem
        self.lines: List[str] = []

    def generate(self):
        """Generate Ghidra Python script."""
        self._generate_header()
        self._generate_imports()
        self._generate_helpers()
        self._generate_data_types()
        self._generate_function_renames()
        self._generate_comments()
        self._generate_structs()

        output_path = self.output_dir / f"{self.stem}_ghidra.py"
        with open(output_path, "w") as f:
            f.write("\n".join(self.lines))

    def _generate_header(self):
        """Generate script header."""
        self.lines = [
            "# GhostDumper v2.2 — Ghidra Import Script",
            f"# Generated: {datetime.now().isoformat()}",
            f"# Classes: {len(self.result.types)}",
            f"# Methods: {len(self.result.methods)}",
            "",
            "# Run in Ghidra: File > Import File > Select Script",
            "# Or: Window > Script Manager > Run Script",
            "",
        ]

    def _generate_imports(self):
        """Generate Ghidra API imports."""
        self.lines.extend([
            "from ghidra.program.model.symbol import SourceType",
            "from ghidra.program.model.data import *",
            "from ghidra.program.model.listing import CodeUnit",
            "from ghidra.util.task import ConsoleTaskMonitor",
            "",
            "monitor = ConsoleTaskMonitor()",
            "listing = currentProgram.getListing()",
            "dtm = currentProgram.getDataTypeManager()",
            "symbol_table = currentProgram.getSymbolTable()",
            "",
        ])

    def _generate_helpers(self):
        """Generate helper functions."""
        self.lines.extend([
            "def get_address(offset):",
            "    return currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(offset)",
            "",
            "def create_namespace(name):",
            "    from ghidra.program.model.symbol import Namespace",
            "    return symbol_table.createNameSpace(None, name, SourceType.ANALYSIS)",
            "",
            "def rename_function(addr, name):",
            "    func = getFunctionAt(get_address(addr))",
            "    if func:",
            "        func.setName(name, SourceType.ANALYSIS)",
            "        return True",
            "    return False",
            "",
        ])

    def _generate_data_types(self):
        """Generate data type definitions."""
        self.lines.extend([
            "# Create basic IL2CPP data types",
            "",
            "def create_il2cpp_types():",
            "    types = {}",
        ])

        type_map = {
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
            "System.String": "pointer",
            "System.Object": "pointer",
        }

        for il2cpp_type, ghidra_type in type_map.items():
            self.lines.append(f'    types["{il2cpp_type}"] = {ghidra_type}')

        self.lines.extend([
            "    return types",
            "",
            "il2cpp_types = create_il2cpp_types()",
            "",
        ])

    def _generate_function_renames(self):
        """Generate function rename commands."""
        self.lines.extend([
            "# Rename functions",
            "",
            "def rename_all_functions():",
            "    renamed = 0",
            "    failed = 0",
        ])

        for method in self.result.methods:
            addr = method.get("address")
            name = method.get("name")
            if addr and name:
                safe_name = name.replace('"', '\"')
                self.lines.append(f'    if rename_function(0x{addr:08X}, "{safe_name}"):')
                self.lines.append(f'        renamed += 1')
                self.lines.append(f'    else:')
                self.lines.append(f'        failed += 1')

        self.lines.extend([
            "    print("Renamed {} functions, {} failed".format(renamed, failed))",
            "",
            "rename_all_functions()",
            "",
        ])

    def _generate_comments(self):
        """Generate comment setting commands."""
        self.lines.extend([
            "# Set comments",
            "",
            "def set_comments():",
        ])

        for type_info in self.result.types:
            for method in type_info.get("methods", []):
                addr = method.get("address")
                if addr:
                    token = method.get("token", 0)
                    params = ", ".join(method.get("parameters", []))
                    comment = f"Token: 0x{token:08X} | Params: {params}"
                    self.lines.append(f'    cu = listing.getCodeUnitAt(get_address(0x{addr:08X}))')
                    self.lines.append(f'    if cu:')
                    self.lines.append(f'        cu.setComment(CodeUnit.PLATE_COMMENT, "{comment}")')

        self.lines.extend([
            "",
            "set_comments()",
            "",
        ])

    def _generate_structs(self):
        """Generate struct creation commands."""
        self.lines.extend([
            "# Create class structs",
            "",
            "def create_structs():",
        ])

        for type_info in self.result.types:
            class_name = type_info["name"]
            safe_name = class_name.replace(".", "_")

            self.lines.extend([
                f'    # Struct: {class_name}',
                f'    struct = StructureDataType("{safe_name}", 0)',
            ])

            for field in type_info.get("fields", []):
                field_name = field.get("name", "field")
                field_type = field.get("type", "void*")
                offset = field.get("offset", 0)

                self.lines.append(
                    f'    struct.add(PointerDataType(), 8, "{field_name}", "")  # Offset: 0x{offset:04X}'
                )

            self.lines.append(f'    dtm.addDataType(struct, None)')
            self.lines.append('')

        self.lines.extend([
            "",
            "create_structs()",
            "",
        ])
