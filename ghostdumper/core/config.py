"""Configuration management for GhostDumper v2.2"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pathlib import Path
import json
import os


@dataclass
class GhostConfig:
    """Central configuration for GhostDumper analysis pipeline."""

    # Input paths
    so_path: Optional[str] = None
    metadata_path: Optional[str] = None
    output_dir: Optional[str] = None

    # Analysis modes
    mode: str = "full"  # full, elf-only, meta-only, runtime
    batch_mode: bool = False
    verbose: bool = False
    timeout: int = 0  # 0 = auto

    # Output formats
    generate_cpp: bool = True
    generate_symbols: bool = True
    generate_r2: bool = True
    generate_ghidra: bool = False
    generate_ida: bool = False
    generate_dump_cs: bool = True
    generate_il2cpp_h: bool = False
    generate_json: bool = True
    generate_hooks: Optional[str] = None  # class name or None for all
    generate_web_report: bool = False

    # Deobfuscation
    deobfuscate: bool = False
    deobf_type: Optional[str] = None  # xor, rot, beebyte, custom
    deobf_key: Optional[str] = None

    # Plugin system
    plugins: List[str] = field(default_factory=list)
    plugin_dir: str = "~/.config/ghostdumper/plugins"

    # Agentic AI
    enable_agent: bool = False
    agent_query: Optional[str] = None
    embedding_model: str = "all-MiniLM-L6-v2"

    # Runtime analysis
    target_pid: Optional[int] = None
    target_package: Optional[str] = None

    # Web UI
    web_port: int = 8080
    web_host: str = "0.0.0.0"

    # Advanced
    unity_version: Optional[str] = None
    force_il2cpp_version: Optional[int] = None
    max_file_size_mb: int = 2048
    chunk_size: int = 10 * 1024 * 1024  # 10MB

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GhostConfig":
        """Create config from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    @classmethod
    def from_file(cls, path: str) -> "GhostConfig":
        """Load config from JSON file."""
        with open(path, "r") as f:
            return cls.from_dict(json.load(f))

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            k: str(v) if isinstance(v, Path) else v
            for k, v in self.__dict__.items()
        }

    def save(self, path: str):
        """Save config to JSON file."""
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    def get_output_dir(self) -> Path:
        """Resolve output directory."""
        if self.output_dir:
            return Path(self.output_dir)
        if self.so_path:
            so = Path(self.so_path)
            return so.parent / f"{so.stem}@ghost"
        return Path.cwd() / "ghost_output"

    def get_plugin_dir(self) -> Path:
        """Resolve plugin directory."""
        return Path(os.path.expanduser(self.plugin_dir))
