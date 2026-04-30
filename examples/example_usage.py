"""
GhostDumper v2.2 — Usage Examples
"""

from ghostdumper import GhostEngine, GhostConfig
from ghostdumper.agents.semantic_agent import SemanticAgent


def example_basic():
    """Basic analysis example."""
    config = GhostConfig(
        so_path="/path/to/libil2cpp.so",
        metadata_path="/path/to/global-metadata.dat",
        output_dir="./output",
    )

    engine = GhostEngine(config)
    result = engine.analyze()

    print(f"Analysis complete in {result.duration:.2f}s")
    print(f"Found {len(result.types)} classes, {len(result.methods)} methods")


def example_deobfuscation():
    """Analysis with deobfuscation."""
    config = GhostConfig(
        so_path="/path/to/libil2cpp.so",
        metadata_path="/path/to/global-metadata.dat",
        deobfuscate=True,
        deobf_type="xor",
        deobf_key="0x42",
    )

    engine = GhostEngine(config)
    result = engine.analyze()

    print(f"Deobfuscation applied: {result.deobfuscation_applied}")


def example_agentic():
    """Agentic AI analysis example."""
    config = GhostConfig(
        so_path="/path/to/libil2cpp.so",
        metadata_path="/path/to/global-metadata.dat",
        enable_agent=True,
    )

    engine = GhostEngine(config)
    result = engine.analyze()

    agent = SemanticAgent(result, config)

    # Find player-related classes
    results = agent.query("player controller health damage")
    for r in results:
        print(f"{r.item_type}: {r.name} (score: {r.score:.2f})")

    # Get class hierarchy
    hierarchy = agent.find_class_hierarchy("PlayerController")
    print(f"Parents: {hierarchy['parents']}")
    print(f"Children: {hierarchy['children']}")

    # Security analysis
    security = agent.analyze_security()
    print(f"Crypto methods: {len(security['crypto_methods'])}")
    print(f"Network methods: {len(security['network_methods'])}")


def example_hooks():
    """Generate hook scaffolding."""
    config = GhostConfig(
        so_path="/path/to/libil2cpp.so",
        metadata_path="/path/to/global-metadata.dat",
        generate_hooks=True,
    )

    engine = GhostEngine(config)
    result = engine.analyze()

    # Output will include _frida.js and _hooks.cpp files


def example_batch():
    """Batch/CI mode example."""
    config = GhostConfig(
        so_path="/path/to/libil2cpp.so",
        metadata_path="/path/to/global-metadata.dat",
        batch_mode=True,
        generate_json=True,
    )

    engine = GhostEngine(config)
    result = engine.analyze()

    # Check for errors
    if result.errors:
        print("Errors occurred:")
        for err in result.errors:
            print(f"  - {err}")
        exit(1)

    print("Analysis successful")


if __name__ == "__main__":
    example_basic()
