# GhostDumper v2.2 Architecture

## Overview

GhostDumper v2.2 uses a modular pipeline architecture:

```
Input → Binary Loader → Metadata Parser → Type Resolver → Deobfuscator → Plugin System → Generators → Output
```

## Core Components

### 1. Binary Loader (`parsers/binary_loader.py`)
- Auto-detects binary format (ELF/PE/Mach-O/NSO/WASM)
- Parses headers, sections, symbols
- Provides virtual address → file offset translation
- Supports 32-bit and 64-bit architectures

### 2. Metadata Parser (`parsers/metadata_parser.py`)
- Supports IL2CPP metadata versions 16-31
- Detects encrypted/obfuscated metadata
- Parses strings, images, assemblies, types, methods, fields
- Handles custom metadata formats via plugins

### 3. Type Resolver (`parsers/type_resolver.py`)
- Cross-references metadata with binary symbols
- Reconstructs class hierarchies
- Maps methods to binary addresses
- Resolves field offsets

### 4. Deobfuscation Pipeline (`parsers/deobfuscator.py`)
- Entropy analysis for encrypted sections
- XOR/ROT brute force
- AES decryption support
- Beebyte and miHoYo custom format support
- Plugin-based extensibility

### 5. Plugin System (`plugins/plugin_manager.py`)
- Loader plugins for custom formats
- Decryptor plugins for game-specific encryption
- Output plugins for custom formats
- Hot-reload from ~/.config/ghostdumper/plugins/

### 6. Generators (`generators/`)
- `cpp_generator.py`: C++ header/source scaffold
- `cs_generator.py`: C# dump.cs output
- `r2_generator.py`: Radare2 rename scripts
- `ghidra_generator.py`: Ghidra Python scripts
- `ida_generator.py`: IDA Pro IDC/Python scripts
- `json_generator.py`: Structured JSON output
- `hook_generator.py`: Frida/C++ hook scaffolding
- `web_report.py`: Interactive HTML report

### 7. Agentic AI (`agents/semantic_agent.py`)
- Vector embeddings for semantic search
- Natural language queries
- Class hierarchy analysis
- Security pattern detection
- Cross-reference analysis

### 8. Web Interface (`web/`)
- Flask-based web UI
- WebSocket real-time progress
- File upload support
- Interactive results browser
- REST API endpoints

## Data Flow

1. **Input**: User provides .so and/or global-metadata.dat
2. **Load**: BinaryLoader parses the executable
3. **Parse**: MetadataParser extracts IL2CPP structures
4. **Resolve**: TypeResolver cross-references everything
5. **Deobfuscate**: DeobfuscationPipeline fixes obfuscation
6. **Plugin**: PluginManager runs custom plugins
7. **Generate**: All enabled generators produce output
8. **Report**: Results presented via CLI or Web UI

## Extension Points

### Adding a New Binary Format
1. Extend `BinaryLoader` with new `_parse_*` method
2. Add magic bytes to `_detect_format()`

### Adding a New Generator
1. Create class in `generators/`
2. Inherit from base pattern
3. Register in `GhostEngine._generate_outputs()`

### Adding a New Plugin
1. Create class inheriting from `GhostPlugin`
2. Implement `execute()` method
3. Place in `~/.config/ghostdumper/plugins/`

### Adding a New Deobfuscator
1. Add `ObfuscationType` enum value
2. Implement `_decrypt_*` method
3. Add detection logic
