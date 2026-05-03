"""
Batch Analysis Script for GhostDumper v2.2

Analyze multiple IL2CPP binaries in CI/CD pipelines.
"""

import json
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any

from ghostdumper import GhostEngine, GhostConfig


def batch_analyze(input_dir: str, output_dir: str, pattern: str = "*.so") -> Dict[str, Any]:
    """Analyze all matching binaries in a directory."""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    results = {
        "total": 0,
        "success": 0,
        "failed": 0,
        "analyses": [],
    }

    for binary_file in input_path.rglob(pattern):
        # Look for corresponding metadata
        metadata_file = binary_file.parent / "global-metadata.dat"
        if not metadata_file.exists():
            metadata_file = binary_file.parent.parent / "Metadata" / "global-metadata.dat"

        config = GhostConfig(
            so_path=str(binary_file),
            metadata_path=str(metadata_file) if metadata_file.exists() else None,
            output_dir=str(output_path / binary_file.stem),
            batch_mode=True,
            generate_json=True,
        )

        try:
            engine = GhostEngine(config)
            result = engine.analyze()

            results["total"] += 1
            results["success"] += 1
            results["analyses"].append({
                "binary": str(binary_file),
                "metadata": str(metadata_file) if metadata_file.exists() else None,
                "success": True,
                "classes": len(result.types),
                "methods": len(result.methods),
                "duration": result.duration,
            })
        except Exception as e:
            results["total"] += 1
            results["failed"] += 1
            results["analyses"].append({
                "binary": str(binary_file),
                "metadata": str(metadata_file) if metadata_file.exists() else None,
                "success": False,
                "error": str(e),
            })

    # Write summary
    summary_path = output_path / "batch_summary.json"
    with open(summary_path, "w") as f:
        json.dump(results, f, indent=2)

    return results


def main():
    parser = argparse.ArgumentParser(description="Batch IL2CPP analysis")
    parser.add_argument("-i", "--input", required=True, help="Input directory")
    parser.add_argument("-o", "--output", required=True, help="Output directory")
    parser.add_argument("-p", "--pattern", default="*.so", help="Binary file pattern")

    args = parser.parse_args()

    results = batch_analyze(args.input, args.output, args.pattern)

    print(f"\nBatch Analysis Complete:")
    print(f"  Total: {results['total']}")
    print(f"  Success: {results['success']}")
    print(f"  Failed: {results['failed']}")

    if results["failed"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
