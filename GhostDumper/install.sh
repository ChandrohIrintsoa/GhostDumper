#!/bin/bash
set -e

GHOST_VERSION="2.2.1"
echo "👻 GhostDumper v${GHOST_VERSION} Installer"
echo "=========================================="

# Detect architecture
ARCH=$(uname -m)
OS=$(uname -o 2>/dev/null || uname -s)
echo "📱 Detected: ${OS} ${ARCH}"

# Detect mobile/Termux
IS_TERMUX=false
if command -v pkg &> /dev/null && [[ "$PREFIX" == *"com.termux"* ]]; then
    IS_TERMUX=true
    echo "📱 Termux environment detected — using mobile-optimized install"
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ python3 not found. Installing..."
    if [[ "$IS_TERMUX" == true ]]; then
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

# Mobile safety: prevent source compilation (which freezes phones)
if [[ "$IS_TERMUX" == true ]]; then
    echo "⚡ Mobile mode: forcing pre-built wheels only (no source compilation)"
    PIP_FLAGS="--prefer-binary --no-build-isolation"
else
    PIP_FLAGS=""
fi

# Install dependencies
echo "📦 Installing core dependencies..."
pip3 install --upgrade pip
pip3 install ${PIP_FLAGS} -e .

# Optional extras
if [[ "$1" == "--web" ]]; then
    echo "🌐 Installing web UI dependencies..."
    pip3 install ${PIP_FLAGS} -e ".[web]"
fi

if [[ "$1" == "--ai" ]]; then
    echo "🧠 Installing AI dependencies..."
    pip3 install ${PIP_FLAGS} -e ".[ai]"
fi

# Create config directory
mkdir -p ~/.config/ghostdumper/plugins
mkdir -p ~/.config/ghostdumper/cache

echo ""
echo "✅ GhostDumper v${GHOST_VERSION} installed successfully!"
echo ""
if [[ "$IS_TERMUX" == true ]]; then
    echo "📱 Mobile tips:"
    echo "  - Core install is light and fast."
    echo "  - Avoid --web and --ai on low-RAM phones (they pull heavy packages)."
    echo "  - If a package tries to compile and freezes, cancel and run:"
    echo "      pip install --prefer-binary --only-binary :all: <package>"
fi
echo ""
echo "Usage:"
echo "  ghostdump --help"
echo "  ghostdump -s libil2cpp.so -m global-metadata.dat"
echo ""
