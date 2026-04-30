#!/bin/bash
set -e

GHOST_VERSION="2.2.0"
echo "👻 GhostDumper v${GHOST_VERSION} Installer"
echo "=========================================="

# Detect architecture
ARCH=$(uname -m)
OS=$(uname -o 2>/dev/null || uname -s)
echo "📱 Detected: ${OS} ${ARCH}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ python3 not found. Installing..."
    if command -v pkg &> /dev/null; then
        pkg install -y python python-pip
    elif command -v apt &> /dev/null; then
        apt update && apt install -y python3 python3-pip
    elif command -v pacman &> /dev/null; then
        pacman -S --noconfirm python python-pip
    else
        echo "❌ Cannot install Python automatically. Please install Python 3.9+ manually."
        exit 1
    fi
fi

PYTHON_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "🐍 Python version: ${PYTHON_VER}"

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install --upgrade pip
pip3 install -e .

# Create config directory
mkdir -p ~/.config/ghostdumper/plugins
mkdir -p ~/.config/ghostdumper/cache

echo ""
echo "✅ GhostDumper v${GHOST_VERSION} installed successfully!"
echo ""
echo "Usage:"
echo "  ghostdump --help"
echo "  ghostdump -s libil2cpp.so -m global-metadata.dat"
echo ""
