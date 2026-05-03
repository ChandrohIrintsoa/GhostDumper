"""
Termux Setup Script for GhostDumper v2.2

Automated lightweight setup for Termux (Android) environment.
Avoids heavy compilation that freezes low-RAM phones.
"""

import os
import subprocess
import sys
from pathlib import Path


def setup_termux():
    """Configure Termux environment for GhostDumper."""
    print("👻 GhostDumper v2.2 — Termux Mobile Setup")
    print("=" * 50)

    # Check architecture
    arch = os.uname().machine
    print(f"📱 Architecture: {arch}")

    # Update packages
    print("📦 Updating packages...")
    subprocess.run(["pkg", "update", "-y"], check=True)

    # Install Python (pre-built, no compilation)
    print("🐍 Installing Python (pre-built wheel)...")
    subprocess.run(["pkg", "install", "-y", "python", "python-pip"], check=True)

    # Install git
    print("📥 Installing git...")
    subprocess.run(["pkg", "install", "-y", "git"], check=True)

    # Skip clang/cmake — GhostDumper core no longer needs compilation
    print("⚡ Skipping clang/cmake (not needed for mobile core install)")

    # Install GhostDumper with pre-built wheels only
    print("👻 Installing GhostDumper (no source compilation)...")
    subprocess.run([
        sys.executable, "-m", "pip", "install",
        "--prefer-binary", "-e", "."
    ], check=True)

    # Create config directory
    config_dir = Path.home() / ".config" / "ghostdumper"
    config_dir.mkdir(parents=True, exist_ok=True)

    print("✅ Setup complete!")
    print(f"\nUsage:")
    print(f"  ghostdump --help")
    print(f"  ghostdump -s /path/to/libil2cpp.so -m /path/to/global-metadata.dat")
    print(f"\n📱 Mobile tips:")
    print(f"  - Core install is fast (~5 MB of deps)")
    print(f"  - Web UI and AI features are NOT installed by default")
    print(f"  - To add them later (may freeze on low-RAM phones):")
    print(f"      pip install --prefer-binary -e '.[web]'")
    print(f"      pip install --prefer-binary -e '.[ai]'")

    # Test installation
    print("\n🧪 Testing installation...")
    result = subprocess.run(["ghostdump", "--version"], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ {result.stdout.strip()}")
    else:
        print(f"❌ Test failed: {result.stderr}")


if __name__ == "__main__":
    try:
        setup_termux()
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)
