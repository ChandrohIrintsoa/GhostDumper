# Changelog

## [2.2.0] - 2026-04-29 — Phantom Core

### Added
- **Multi-format binary support**: ELF, PE, Mach-O, NSO, WASM
- **Advanced deobfuscation engine**: XOR, ROT, AES, Beebyte, miHoYo
- **Plugin architecture**: Custom loaders, decryptors, and output plugins
- **Web-based UI**: Flask + WebSocket real-time analysis streaming
- **Agentic AI layer**: Semantic search, natural language queries, class hierarchy analysis
- **Multi-disassembler script generation**: Radare2, Ghidra, IDA Pro, x64dbg
- **Runtime hook scaffolding**: Frida JS, C++ hooks, pattern scanners
- **Interactive HTML report**: Searchable browser with filtering
- **JSON API**: Structured output for CI/CD integration
- **Batch/CI mode**: Automated analysis with exit codes
- **Memory pattern scanner**: Runtime analysis helpers
- **Version auto-detection**: Unity and IL2CPP version detection
- **Encrypted metadata detection**: Automatic obfuscation identification

### Changed
- Complete architecture rewrite from v1.1
- Modular parser/generator/plugin system
- Rich CLI with progress bars and tables
- Improved Termux compatibility

### Fixed
- Memory usage optimization for large binaries (>500MB)
- Timeout handling for long-running analyses
- Better error reporting and recovery

## [1.1.0] - 2024

### Added
- Initial ELF + metadata analysis
- C++ class scaffold generation
- Radare2 script generation
- Termux support (32 & 64-bit)
- Basic CLI interface

## [1.0.0] - 2024

### Added
- Initial release
- Basic IL2CPP symbol extraction
