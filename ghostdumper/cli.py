"""
GhostDumper v2.2 — Command Line Interface

Main entry point with rich CLI experience.
"""

import sys
import os
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from .core.engine import GhostEngine
from .core.config import GhostConfig
from .web.server import start_server
from .agents.semantic_agent import SemanticAgent


console = Console()


@click.command()
@click.option("-s", "--so", "so_path", type=click.Path(exists=True), help="IL2CPP binary (.so) path")
@click.option("-m", "--meta", "metadata_path", type=click.Path(exists=True), help="global-metadata.dat path")
@click.option("-d", "--dir", "scan_dir", type=click.Path(exists=True), help="Directory to scan recursively")
@click.option("-o", "--out", "output_dir", type=click.Path(), help="Output directory")
@click.option("-t", "--timeout", type=int, default=0, help="Timeout in seconds (0=auto)")
@click.option("--batch", is_flag=True, help="Batch mode (no animations)")
@click.option("-v", "--verbose", is_flag=True, help="Verbose output")
@click.option("--all-formats", is_flag=True, help="Generate all output formats")
@click.option("--deobfuscate", type=click.Choice(["xor", "rot", "beebyte", "mihoyo", "custom"]), help="Deobfuscation type")
@click.option("--deobf-key", help="Deobfuscation key")
@click.option("--generate-hooks", is_flag=True, help="Generate runtime hook scaffolding")
@click.option("--web", is_flag=True, help="Launch web UI")
@click.option("--web-port", default=8080, help="Web UI port")
@click.option("--web-host", default="0.0.0.0", help="Web UI host")
@click.option("--agent", "agent_query", help="Agentic AI query")
@click.option("--json", "json_output", is_flag=True, help="Output JSON to stdout")
@click.option("--version", is_flag=True, help="Show version")
def main(so_path, metadata_path, scan_dir, output_dir, timeout, batch, verbose,
         all_formats, deobfuscate, deobf_key, generate_hooks, web, web_port, web_host,
         agent_query, json_output, version):
    """👻 GhostDumper v2.2 — IL2CPP Deep Analyzer & Runtime Toolkit"""

    if version:
        console.print("[bold magenta]GhostDumper v2.2.0[/bold magenta]")
        console.print("Phantom Core — IL2CPP Deep Analyzer")
        return

    if web:
        console.print(Panel.fit(
            "[bold magenta]👻 GhostDumper v2.2 Web UI[/bold magenta]",
            subtitle=f"Starting server on http://{web_host}:{web_port}"
        ))
        start_server(host=web_host, port=web_port)
        return

    # Build configuration
    config = GhostConfig(
        so_path=so_path,
        metadata_path=metadata_path,
        output_dir=output_dir,
        batch_mode=batch,
        verbose=verbose,
        timeout=timeout,
        deobfuscate=bool(deobfuscate),
        deobf_type=deobfuscate,
        deobf_key=deobf_key,
        enable_agent=bool(agent_query),
        agent_query=agent_query,
    )

    if all_formats:
        config.generate_cpp = True
        config.generate_symbols = True
        config.generate_r2 = True
        config.generate_ghidra = True
        config.generate_ida = True
        config.generate_dump_cs = True
        config.generate_il2cpp_h = True
        config.generate_json = True
        config.generate_hooks = True
        config.generate_web_report = True

    if generate_hooks:
        config.generate_hooks = True

    # Validate inputs
    if not so_path and not metadata_path and not scan_dir:
        console.print("[bold red]Error:[/bold red] No input files specified. Use -s, -m, or -d.")
        console.print("
Usage examples:")
        console.print("  ghostdump -s libil2cpp.so -m global-metadata.dat")
        console.print("  ghostdump -d /path/to/game/")
        console.print("  ghostdump --web")
        sys.exit(1)

    # Handle directory scan
    if scan_dir:
        scan_path = Path(scan_dir)
        # Auto-find libil2cpp.so and global-metadata.dat
        for root, dirs, files in os.walk(scan_path):
            for file in files:
                if file == "libil2cpp.so" and not config.so_path:
                    config.so_path = str(Path(root) / file)
                elif file == "global-metadata.dat" and not config.metadata_path:
                    config.metadata_path = str(Path(root) / file)

    # Run analysis
    try:
        engine = GhostEngine(config)
        result = engine.analyze()

        # Agentic query if requested
        if agent_query:
            console.print(f"\n[bold cyan]🤖 Agentic Query:[/bold cyan] {agent_query}")
            agent = SemanticAgent(result, config)
            search_results = agent.query(agent_query)

            table = Table(title="Agent Results")
            table.add_column("Type", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Score", style="yellow")

            for r in search_results:
                table.add_row(r.item_type, r.name, f"{r.score:.2f}")

            console.print(table)

        # JSON output if requested
        if json_output:
            import json
            output = {
                "success": True,
                "duration": result.duration,
                "binary": result.binary_info,
                "metadata": result.metadata_info,
                "classes_count": len(result.types),
                "methods_count": len(result.methods),
                "fields_count": len(result.fields),
                "deobfuscation": result.deobfuscation_applied,
                "output_dir": str(config.get_output_dir()),
            }
            console.print_json(json.dumps(output))

    except Exception as e:
        console.print(f"[bold red]Analysis failed:[/bold red] {e}")
        if verbose:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
