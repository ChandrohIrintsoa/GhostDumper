"""
JSON Metadata Generator for GhostDumper v2.2

Generates structured JSON output for programmatic consumption,
CI/CD integration, and API usage.
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class JsonGenerator:
    """Generate JSON metadata output."""

    def __init__(self, result, output_dir: Path, stem: str):
        self.result = result
        self.output_dir = output_dir
        self.stem = stem

    def generate(self):
        """Generate JSON output files."""
        # Full metadata
        full_data = {
            "ghostdumper_version": "2.2.0",
            "generated_at": datetime.now().isoformat(),
            "binary": self.result.binary_info,
            "metadata": self.result.metadata_info,
            "statistics": self.result.statistics,
            "deobfuscation": self.result.deobfuscation_applied,
            "plugin_results": self.result.plugin_results,
            "duration": self.result.duration,
            "errors": self.result.errors,
            "types": self.result.types,
            "methods": self.result.methods,
            "fields": self.result.fields,
            "strings": self.result.strings[:1000] if len(self.result.strings) > 1000 else self.result.strings,
            "symbols": self.result.symbols[:5000] if len(self.result.symbols) > 5000 else self.result.symbols,
        }

        full_path = self.output_dir / f"{self.stem}_metadata.json"
        with open(full_path, "w") as f:
            json.dump(full_data, f, indent=2, default=str)

        # Methods-only for scripting
        methods_data = {
            "version": "2.2.0",
            "generated_at": datetime.now().isoformat(),
            "method_count": len(self.result.methods),
            "methods": [
                {
                    "name": m["name"],
                    "address": m.get("address"),
                    "token": m.get("token"),
                    "return_type": m.get("return_type"),
                    "parameters": m.get("parameters", []),
                    "flags": m.get("flags"),
                }
                for m in self.result.methods
            ],
        }

        methods_path = self.output_dir / f"{self.stem}_script.json"
        with open(methods_path, "w") as f:
            json.dump(methods_data, f, indent=2)

        # Strings-only
        strings_data = {
            "version": "2.2.0",
            "string_count": len(self.result.strings),
            "strings": self.result.strings[:5000],
        }

        strings_path = self.output_dir / f"{self.stem}_strings.json"
        with open(strings_path, "w") as f:
            json.dump(strings_data, f, indent=2)
