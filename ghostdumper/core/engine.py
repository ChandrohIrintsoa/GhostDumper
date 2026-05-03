"""
GhostDumper v2.2 — Core Analysis Engine

Orchestrates the full IL2CPP analysis pipeline:
1. Binary loading (ELF/PE/Mach-O/NSO/WASM)
2. Metadata parsing (v16-v31)
3. Type resolution & symbol reconstruction
4. Deobfuscation pipeline
5. Output generation (multi-format)
6. Plugin execution
"""

import struct
import json
import time
import hashlib
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple, Union
from dataclasses import dataclass, field

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.panel import Panel

from .config import GhostConfig
from ..parsers.binary_loader import BinaryLoader
from ..parsers.metadata_parser import MetadataParser
from ..parsers.type_resolver import TypeResolver
from ..parsers.deobfuscator import DeobfuscationPipeline
from ..generators.cpp_generator import CppGenerator
from ..generators.cs_generator import CsGenerator
from ..generators.r2_generator import R2Generator
from ..generators.ghidra_generator import GhidraGenerator
from ..generators.ida_generator import IdaGenerator
from ..generators.json_generator import JsonGenerator
from ..generators.hook_generator import HookGenerator
from ..generators.web_report import WebReportGenerator
from ..plugins.plugin_manager import PluginManager
from ..utils.logger import GhostLogger
from ..utils.version_detector import VersionDetector


@dataclass
class AnalysisResult:
    """Container for analysis results."""
    binary_info: Dict[str, Any] = field(default_factory=dict)
    metadata_info: Dict[str, Any] = field(default_factory=dict)
    types: List[Dict[str, Any]] = field(default_factory=list)
    methods: List[Dict[str, Any]] = field(default_factory=list)
    fields: List[Dict[str, Any]] = field(default_factory=list)
    strings: List[Dict[str, Any]] = field(default_factory=list)
    symbols: List[Dict[str, Any]] = field(default_factory=list)
    deobfuscation_applied: List[str] = field(default_factory=list)
    plugin_results: Dict[str, Any] = field(default_factory=dict)
    statistics: Dict[str, int] = field(default_factory=dict)
    duration: float = 0.0
    errors: List[str] = field(default_factory=list)


class GhostEngine:
    """Main analysis engine for GhostDumper v2.2."""

    SUPPORTED_FORMATS = ["ELF", "PE", "Mach-O", "NSO", "WASM"]
    SUPPORTED_METADATA_VERSIONS = list(range(16, 32))  # v16 to v31

    def __init__(self, config: GhostConfig):
        self.config = config
        self.console = Console()
        self.logger = GhostLogger(config.verbose)
        self.plugin_manager = PluginManager(config)
        self.result = AnalysisResult()

        # Pipeline components
        self.binary_loader: Optional[BinaryLoader] = None
        self.metadata_parser: Optional[MetadataParser] = None
        self.type_resolver: Optional[TypeResolver] = None
        self.deobf_pipeline: Optional[DeobfuscationPipeline] = None

    def analyze(self) -> AnalysisResult:
        """Run the full analysis pipeline."""
        start_time = time.time()

        self.console.print(Panel.fit(
            "[bold magenta]👻 GhostDumper v2.2 — Phantom Core[/bold magenta]",
            subtitle="IL2CPP Deep Analyzer & Runtime Toolkit"
        ))

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=self.console,
                disable=self.config.batch_mode
            ) as progress:

                # Stage 1: Load binary
                task = progress.add_task("[cyan]Loading binary...", total=100)
                self._load_binary(progress, task)

                # Stage 2: Parse metadata
                task = progress.add_task("[cyan]Parsing metadata...", total=100)
                self._parse_metadata(progress, task)

                # Stage 3: Resolve types
                task = progress.add_task("[cyan]Resolving types...", total=100)
                self._resolve_types(progress, task)

                # Stage 4: Deobfuscation
                if self.config.deobfuscate:
                    task = progress.add_task("[cyan]Deobfuscating...", total=100)
                    self._deobfuscate(progress, task)

                # Stage 5: Execute plugins
                task = progress.add_task("[cyan]Running plugins...", total=100)
                self._run_plugins(progress, task)

                # Stage 6: Generate outputs
                task = progress.add_task("[cyan]Generating outputs...", total=100)
                self._generate_outputs(progress, task)

        except Exception as e:
            self.result.errors.append(str(e))
            self.logger.error(f"Analysis failed: {e}")
            # Don't re-raise; return partial result with error information
            
        self.result.duration = time.time() - start_time
        self._print_summary()

        return self.result

    def _load_binary(self, progress, task):
        """Load and analyze the IL2CPP binary."""
        if not self.config.so_path:
            progress.update(task, completed=100, description="[yellow]Skipping binary (no .so provided)[/yellow]")
            return

        self.binary_loader = BinaryLoader(self.config.so_path, self.config)
        self.binary_loader.load()

        self.result.binary_info = {
            "format": self.binary_loader.format,
            "arch": self.binary_loader.arch,
            "bitness": self.binary_loader.bitness,
            "entry_point": hex(self.binary_loader.entry_point) if self.binary_loader.entry_point else None,
            "base_address": hex(self.binary_loader.base_address),
            "size": self.binary_loader.size,
            "symbols_count": len(self.binary_loader.symbols),
            "sections": [s["name"] for s in self.binary_loader.sections],
        }

        self.result.symbols = self.binary_loader.symbols
        progress.update(task, completed=100, description=f"[green]Binary loaded: {self.binary_loader.format} {self.binary_loader.arch}[/green]")

    def _parse_metadata(self, progress, task):
        """Parse global-metadata.dat."""
        if not self.config.metadata_path:
            progress.update(task, completed=100, description="[yellow]Skipping metadata (no file provided)[/yellow]")
            return

        self.metadata_parser = MetadataParser(self.config.metadata_path, self.config)
        self.metadata_parser.parse()

        self.result.metadata_info = {
            "version": self.metadata_parser.version,
            "string_count": len(self.metadata_parser.strings),
            "type_count": len(self.metadata_parser.types),
            "method_count": len(self.metadata_parser.methods),
            "field_count": len(self.metadata_parser.fields),
            "image_count": len(self.metadata_parser.images),
            "assembly_count": len(self.metadata_parser.assemblies),
        }

        self.result.strings = self.metadata_parser.strings
        progress.update(task, completed=100, description=f"[green]Metadata parsed: v{self.metadata_parser.version}[/green]")

    def _resolve_types(self, progress, task):
        """Resolve IL2CPP types and cross-reference binary/metadata."""
        if not self.metadata_parser:
            progress.update(task, completed=100, description="[yellow]Skipping type resolution (no metadata)[/yellow]")
            return

        self.type_resolver = TypeResolver(
            self.metadata_parser,
            self.binary_loader,
            self.config
        )
        self.type_resolver.resolve()

        self.result.types = self.type_resolver.types
        self.result.methods = self.type_resolver.methods
        self.result.fields = self.type_resolver.fields

        progress.update(task, completed=100, description=f"[green]Types resolved: {len(self.result.types)} classes[/green]")

    def _deobfuscate(self, progress, task):
        """Run deobfuscation pipeline."""
        self.deobf_pipeline = DeobfuscationPipeline(self.config)

        if self.binary_loader:
            self.deobf_pipeline.analyze_binary(self.binary_loader)
        if self.metadata_parser:
            self.deobf_pipeline.analyze_metadata(self.metadata_parser)

        applied = self.deobf_pipeline.apply()
        self.result.deobfuscation_applied = applied

        progress.update(task, completed=100, description=f"[green]Deobfuscation: {', '.join(applied) if applied else 'None detected'}[/green]")

    def _run_plugins(self, progress, task):
        """Execute loaded plugins."""
        self.plugin_manager.load_plugins()
        plugin_results = self.plugin_manager.execute_all(self.result)
        self.result.plugin_results = plugin_results
        progress.update(task, completed=100, description=f"[green]Plugins: {len(plugin_results)} executed[/green]")

    def _generate_outputs(self, progress, task):
        """Generate all requested output files."""
        output_dir = self.config.get_output_dir()
        output_dir.mkdir(parents=True, exist_ok=True)

        stem = Path(self.config.so_path).stem if self.config.so_path else Path(self.config.metadata_path).stem if self.config.metadata_path else "analysis"
        generators = []

        if self.config.generate_cpp:
            generators.append(("C++ Scaffold", CppGenerator(self.result, output_dir, stem)))
        if self.config.generate_dump_cs:
            generators.append(("C# Dump", CsGenerator(self.result, output_dir, stem)))
        if self.config.generate_r2:
            generators.append(("Radare2", R2Generator(self.result, output_dir, stem)))
        if self.config.generate_ghidra:
            generators.append(("Ghidra", GhidraGenerator(self.result, output_dir, stem)))
        if self.config.generate_ida:
            generators.append(("IDA Pro", IdaGenerator(self.result, output_dir, stem)))
        if self.config.generate_json:
            generators.append(("JSON", JsonGenerator(self.result, output_dir, stem)))
        if self.config.generate_hooks is not None:
            generators.append(("Hooks", HookGenerator(self.result, output_dir, stem)))
        if self.config.generate_web_report:
            generators.append(("Web Report", WebReportGenerator(self.result, output_dir, stem)))

        total = len(generators)
        for i, (name, gen) in enumerate(generators):
            try:
                gen.generate()
                progress.update(task, completed=int((i + 1) / total * 100), 
                              description=f"[cyan]Generating {name}... ({i+1}/{total})[/cyan]")
            except Exception as e:
                self.logger.error(f"Generator {name} failed: {e}")
                self.result.errors.append(f"Generator {name}: {e}")
                progress.update(task, completed=int((i + 1) / total * 100), 
                              description=f"[red]{name} failed: {e}[/red]")

        progress.update(task, completed=100, description=f"[green]Outputs generated in {output_dir}[/green]")

    def _print_summary(self):
        """Print analysis summary."""
        if self.config.batch_mode:
            return

        table = Table(title="Analysis Summary", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Duration", f"{self.result.duration:.2f}s")
        table.add_row("Binary Format", self.result.binary_info.get("format", "N/A"))
        table.add_row("Architecture", self.result.binary_info.get("arch", "N/A"))
        table.add_row("Metadata Version", str(self.result.metadata_info.get("version", "N/A")))
        table.add_row("Classes", str(len(self.result.types)))
        table.add_row("Methods", str(len(self.result.methods)))
        table.add_row("Fields", str(len(self.result.fields)))
        table.add_row("Strings", str(self.result.metadata_info.get("string_count", 0)))
        table.add_row("Symbols", str(len(self.result.symbols)))

        if self.result.deobfuscation_applied:
            table.add_row("Deobfuscation", ", ".join(self.result.deobfuscation_applied))

        self.console.print(table)

        if self.result.errors:
            self.console.print("[bold red]Errors:[/bold red]")
            for err in self.result.errors:
                self.console.print(f"  • {err}")
