"""
IDA Pro Script Generator for GhostDumper v2.2

Generates IDC and Python scripts for IDA Pro that rename
functions, set types, and create structures from IL2CPP metadata.
"""

from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class IdaGenerator:
    """Generate IDA Pro import scripts."""

    def __init__(self, result, output_dir: Path, stem: str):
        self.result = result
        self.output_dir = output_dir
        self.stem = stem
        self.idc_lines: List[str] = []
        self.py_lines: List[str] = []

    def generate(self):
        """Generate both IDC and Python scripts."""
        self._generate_idc()
        self._generate_python()

        # Write IDC
        idc_path = self.output_dir / f"{self.stem}_ida.idc"
        with open(idc_path, "w") as f:
            f.write("\n".join(self.idc_lines))

        # Write Python
        py_path = self.output_dir / f"{self.stem}_ida.py"
        with open(py_path, "w") as f:
            f.write("\n".join(self.py_lines))

    def _generate_idc(self):
        """Generate IDC script."""
        self.idc_lines = [
            "// GhostDumper v2.2 — IDA Pro IDC Script",
            f"// Generated: {datetime.now().isoformat()}",
            f"// Classes: {len(self.result.types)}",
            f"// Methods: {len(self.result.methods)}",
            "",
            "#include <idc.idc>",
            "",
            "static main() {",
            "    auto renamed, failed, addr;",
            "    renamed = 0;",
            "    failed = 0;",
            "",
        ]

        # Function renames
        for method in self.result.methods:
            addr = method.get("address")
            name = method.get("name")
            if addr and name:
                safe_name = name.replace('"', '\\"').replace("'", "\\'")
                self.idc_lines.extend([
                    f"    addr = 0x{addr:08X};",
                    f'    if (MakeName(addr, "{safe_name}") == 0) {{',
                    f"        renamed++;",
                    f"    }} else {{",
                    f"        failed++;",
                    f"    }}",
                ])

        self.idc_lines.extend([
            "",
            '    Message("Renamed %d functions, %d failed\n", renamed, failed);',
            "}",
        ])

    def _generate_python(self):
        """Generate IDA Python script."""
        self.py_lines = [
            "# GhostDumper v2.2 — IDA Pro Python Script",
            f"# Generated: {datetime.now().isoformat()}",
            f"# Classes: {len(self.result.types)}",
            f"# Methods: {len(self.result.methods)}",
            "",
            "import idaapi",
            "import idc",
            "import idautils",
            "",
            "def rename_all_functions():",
            "    renamed = 0",
            "    failed = 0",
        ]

        for method in self.result.methods:
            addr = method.get("address")
            name = method.get("name")
            if addr and name:
                safe_name = name.replace('"', '\\"')
                self.py_lines.extend([
                    f'    if idc.set_name(0x{addr:08X}, "{safe_name}", idc.SN_CHECK):',
                    f'        renamed += 1',
                    f'    else:',
                    f'        failed += 1',
                ])

        self.py_lines.extend([
            '    print(f"Renamed {renamed} functions, {failed} failed")',
            "",
            "def set_comments():",
        ])

        for type_info in self.result.types:
            for method in type_info.get("methods", []):
                addr = method.get("address")
                if addr:
                    token = method.get("token", 0)
                    comment = f"Token: 0x{token:08X}"
                    self.py_lines.append(f'    idc.set_func_cmt(0x{addr:08X}, "{comment}", 1)')

        self.py_lines.extend([
            "",
            "def create_structs():",
            '    from idaapi import add_struc, add_struc_member, FF_DATA, FF_QWORD',
        ])

        for type_info in self.result.types:
            class_name = type_info["name"]
            safe_name = class_name.replace(".", "_").replace("<", "_").replace(">", "_")

            self.py_lines.extend([
                f'    # Struct: {class_name}',
                f'    sid = add_struc(-1, "{safe_name}", 0)',
            ])

            for field in type_info.get("fields", []):
                field_name = field.get("name", "field")
                offset = field.get("offset", 0)
                self.py_lines.append(
                    f'    add_struc_member(sid, "{field_name}", {offset}, FF_DATA|FF_QWORD, -1, 8)'
                )

            self.py_lines.append('')

        self.py_lines.extend([
            "",
            "if __name__ == '__main__':",
            "    rename_all_functions()",
            "    set_comments()",
            "    create_structs()",
            "    print('GhostDumper IDA script completed!')",
        ])
