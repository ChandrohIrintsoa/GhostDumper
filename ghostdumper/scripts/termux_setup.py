"""
Termux Setup Script for GhostDumper v2.2

Automated setup for Termux (Android) environment.
"""

import os
import subprocess
import sys
from pathlib import Path


def setup_termux():
    """Configure Termux environment for GhostDumper."""
    print("👻 GhostDumper v2.2 — Termux Setup")
    print("=" * 50)

    # Check architecture
    arch = os.uname().machine
    print(f"📱 Architecture: {arch}")

    # Update packages
    print("📦 Updating packages...")
    subprocess.run(["pkg", "update", "-y"], check=True)

    # Install Python
    print("🐍 Installing Python...")
    subprocess.run(["pkg", "install", "-y", "python", "python-pip"], check=True)

    # Install git
    print("📥 Installing git...")
    subprocess.run(["pkg", "install", "-y", "git"], check=True)

    # Install build tools
    print("🔧 Installing build tools...")
    subprocess.run(["pkg", "install", "-y", "clang", "cmake"], check=True)

    # Install GhostDumper
    print("👻 Installing GhostDumper...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], check=True)

    # Create config directory
    config_dir = Path.home() / ".config" / "ghostdumper"
    config_dir.mkdir(parents=True, exist_ok=True)

    print("✅ Setup complete!")
    print(f"
Usage:")
    print(f"  ghostdump --help")
    print(f"  ghostdump -s /path/to/libil2cpp.so -m /path/to/global-metadata.dat")

    # Test installation
    print("
🧪 Testing installation...")
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
