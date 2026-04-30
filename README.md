# 👻 GhostDumper v2.2 — IL2CPP Deep Analyzer & Runtime Toolkit

> **Version**: 2.2.0  
> **Codename**: *Phantom Core*  
> **License**: MIT  
> **Platform**: Cross-platform (Termux, Linux, Windows, macOS)

---

## 🎯 What is GhostDumper v2.2?

GhostDumper v2.2 is a **next-generation IL2CPP analysis and runtime manipulation toolkit** that combines the best features from the entire IL2CPP reverse-engineering ecosystem into a single, extensible Python framework.

Unlike v1.1 which was limited to ELF+metadata static analysis, **v2.2 is a complete rewrite** incorporating:
- **Multi-format binary support** (ELF, PE, Mach-O, NSO, WASM)
- **Advanced deobfuscation engine** (XOR, ROT, metadata reordering, encrypted strings)
- **Plugin architecture** for custom loaders and decrypters
- **Web-based UI** with real-time analysis streaming
- **Agentic AI layer** for semantic code search and intelligent analysis
- **Multi-disassembler script generation** (Radare2, Ghidra, IDA, x64dbg)
- **Runtime memory analysis** helpers and hook scaffolding
- **CI/CD batch mode** with JSON/structured output

---

## 📊 Comparison Matrix

| Feature | GhostDumper v1.1 | Il2CppDumper | Il2CppInspector | Il2CppGG | GhostDumper v2.2 |
|---------|-----------------|--------------|-----------------|----------|------------------|
| ELF Support | ✅ | ✅ | ✅ | ✅ | ✅ |
| PE Support | ❌ | ✅ | ✅ | ❌ | ✅ |
| Mach-O Support | ❌ | ✅ | ✅ | ❌ | ✅ |
| NSO/WASM | ❌ | ✅ | ❌ | ❌ | ✅ |
| Metadata-only mode | ✅ | ❌ | ❌ | ❌ | ✅ |
| ELF-only mode | ✅ | ❌ | ❌ | ❌ | ✅ |
| Web UI | ❌ | ❌ (Python port has it) | ❌ | ❌ | ✅ |
| Plugin System | ❌ | ❌ | ✅ | ❌ | ✅ |
| Deobfuscation | ❌ | Basic | Advanced | Basic | Advanced |
| Radare2 Scripts | ✅ | ❌ | ✅ | ❌ | ✅ |
| Ghidra Scripts | ❌ | ❌ | ✅ | ❌ | ✅ |
| IDA Scripts | ❌ | ✅ | ✅ | ❌ | ✅ |
| C++ Scaffolding | ❌ | ❌ | ✅ | ❌ | ✅ |
| Dummy DLL Info | ❌ | ✅ | ✅ | ❌ | ✅ |
| Runtime Hooks | ❌ | ❌ | ❌ | ✅ | ✅ |
| Agentic AI | ❌ | ❌ | ❌ | ❌ | ✅ |
| Semantic Search | ❌ | ❌ | ❌ | ❌ | ✅ |
| JSON API | ❌ | ❌ | ✅ | ❌ | ✅ |
| Termux Optimized | ✅ | ❌ | ❌ | ✅ | ✅ |
| Batch/CI Mode | Basic | ❌ | ❌ | ❌ | Advanced |

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/ChandrohIrintsoa/GhostDumper.git
cd GhostDumper

# Install (auto-detects architecture)
bash install.sh

# Or via pip
pip install -e .
```

### CLI Usage

```bash
# Interactive mode — scan current directory
ghostdump

# Direct analysis with metadata
ghostdump -s libil2cpp.so -m global-metadata.dat

# Full analysis with all outputs
ghostdump -s libil2cpp.so -m global-metadata.dat --all-formats

# Web UI mode
ghostdump --web --port 8080

# Batch mode with JSON output
ghostdump -s libil2cpp.so -m global-metadata.dat --batch --json -o ./results/

# Deobfuscation mode
ghostdump -s libil2cpp.so -m global-metadata.dat --deobfuscate xor

# Agentic analysis (semantic search)
ghostdump -s libil2cpp.so -m global-metadata.dat --agent "Find Player class hierarchy"

# Runtime hook generation
ghostdump -s libil2cpp.so -m global-metadata.dat --generate-hooks PlayerController
```

---

## 📁 Output Files

| File | Description |
|------|-------------|
| `<lib>_classes.cpp` | Classes + methods + offsets (C++ scaffold) |
| `<lib>_symbols.txt` | Sorted ELF symbols + metadata inventory |
| `<lib>_r2patch.r2` | Radare2 rename script |
| `<lib>_ghidra.py` | Ghidra import script |
| `<lib>_ida.py` | IDA Pro import script |
| `<lib>_dump.cs` | C# pseudocode with addresses |
| `<lib>_il2cpp.h` | C header for IDA/Ghidra |
| `<lib>_script.json` | Method addresses for scripting |
| `<lib>_metadata.json` | Full structured metadata |
| `<lib>_hooks.cpp` | Runtime hook scaffolding |
| `<lib>_analysis.html` | Interactive web report |

---

## 🏗️ Architecture

```
GhostDumper v2.2
├── Core Engine
│   ├── Binary Loader (ELF/PE/Mach-O/NSO/WASM)
│   ├── Metadata Parser (v16-v31)
│   ├── Type Resolution Engine
│   └── Deobfuscation Pipeline
├── Plugin System
│   ├── Loader Plugins (miHoYo, Beebyte, etc.)
│   ├── Decryptor Plugins (XOR, ROT, Custom)
│   └── Output Plugins
├── Generators
│   ├── C# Dump (dump.cs)
│   ├── C++ Scaffold (il2cpp.h, hooks.cpp)
│   ├── Script Generators (r2, ghidra, ida)
│   └── JSON Metadata
├── Agentic AI Layer
│   ├── Semantic Code Chunker
│   ├── Vector Embeddings (local)
│   ├── Class Hierarchy Analyzer
│   └── Natural Language Query
├── Web Interface
│   ├── Real-time Streaming
│   ├── Interactive Graphs
│   └── Search & Filter
└── Utils
    ├── Memory Pattern Scanner
    ├── String Decryptor
    └── Version Detector
```

---

## 🧪 Testing

```bash
pytest tests/ -v
```

---

## 🤝 Credits

- — Il2CppDumper (reference implementation)
- — Il2CppInspector (plugin architecture, deobfuscation)
- — Il2CppGG (runtime hook concepts)
- — Il2CppDumper-Python (web UI inspiration)
- **il2cpp-dump-analyzer**

---

## ⚠️ Disclaimer

This tool is for **educational and research purposes only**. Respect game developers' rights and terms of service.
