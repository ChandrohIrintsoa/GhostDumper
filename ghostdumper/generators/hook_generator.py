"""
Runtime Hook Generator for GhostDumper v2.2

Generates C++ hook scaffolding using:
- Frida (JavaScript)
- ADBI/Frida (C++)
- IL2CPP Resolver patterns
- Pattern scanning helpers
"""

from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class HookGenerator:
    """Generate runtime hook scaffolding."""

    def __init__(self, result, output_dir: Path, stem: str):
        self.result = result
        self.output_dir = output_dir
        self.stem = stem

    def generate(self):
        """Generate hook files."""
        self._generate_frida_js()
        self._generate_cpp_hooks()
        self._generate_pattern_scanner()

    def _generate_frida_js(self):
        """Generate Frida JavaScript hook script."""
        lines = [
            "// GhostDumper v2.2 — Frida Hook Script",
            f"// Generated: {datetime.now().isoformat()}",
            f"// Classes: {len(self.result.types)}",
            f"// Methods: {len(self.result.methods)}",
            "",
            "// Usage: frida -U -f com.package.name -l hook.js --no-pause",
            "",
            'var moduleName = "libil2cpp.so";',
            "var baseAddr = Module.findBaseAddress(moduleName);",
            "",
            "function hook_by_offset(offset, name, retType, argTypes) {",
            "    var addr = baseAddr.add(offset);",
            "    Interceptor.attach(addr, {",
            "        onEnter: function(args) {",
            "            console.log('[+] ' + name + ' called');",
            "            for (var i = 0; i < argTypes.length; i++) {",
            "                console.log('    arg' + i + ': ' + args[i]);",
            "            }",
            "        },",
            "        onLeave: function(retval) {",
            "            console.log('[-] ' + name + ' returned: ' + retval);",
            "        }",
            "    });",
            "}",
            "",
            "function hook_by_address(address, name) {",
            "    Interceptor.attach(ptr(address), {",
            "        onEnter: function(args) {",
            "            console.log('[+] ' + name + ' called');",
            "        },",
            "        onLeave: function(retval) {",
            "            console.log('[-] ' + name + ' returned');",
            "        }",
            "    });",
            "}",
            "",
            "// === Auto-generated hooks ===",
            "",
        ]

        base = self.result.binary_info.get("base_address", 0)

        for method in self.result.methods[:100]:  # Limit to first 100
            addr = method.get("address")
            name = method.get("name", "unknown")
            if addr and addr > base:
                offset = addr - base
                lines.append(f"// {name}")
                lines.append(f'hook_by_offset(0x{offset:08X}, "{name}", "void", []);')
                lines.append("")

        lines.extend([
            "",
            "console.log('[GhostDumper] Hooks installed');",
            "console.log('[GhostDumper] Module base: ' + baseAddr);",
        ])

        path = self.output_dir / f"{self.stem}_frida.js"
        with open(path, "w") as f:
            f.write("\n".join(lines))

    def _generate_cpp_hooks(self):
        """Generate C++ hook scaffolding."""
        lines = [
            "// GhostDumper v2.2 — C++ Hook Scaffold",
            f"// Generated: {datetime.now().isoformat()}",
            "",
            "#include <cstdint>",
            "#include <string>",
            "#include <vector>",
            "#include <dlfcn.h>",
            "",
            "// Platform-specific includes",
            "#ifdef __ANDROID__",
            "#include <android/log.h>",
            '#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, "GhostDumper", __VA_ARGS__)',
            "#else",
            "#define LOGI(...) printf(__VA_ARGS__)",
            "#endif",
            "",
            "namespace hooks {",
            "",
            "// Target module",
            'const char* TARGET_MODULE = "libil2cpp.so";',
            "",
            "// Base address (set at runtime)",
            "uintptr_t g_base_addr = 0;",
            "",
            "// Helper: Get module base",
            "uintptr_t get_module_base(const char* name) {",
            "    // Implementation depends on platform",
            "    // Android: parse /proc/self/maps",
            "    // Windows: GetModuleHandle",
            "    // Linux: dlopen + dlsym",
            "    return 0;",
            "}",
            "",
            "// Helper: Hook function",
            "template<typename T>",
            "bool hook_function(uintptr_t offset, T* hook, T** original) {",
            "    // Platform-specific hook implementation",
            "    // Options: PLT/GOT hooking, inline hooking, trampolines",
            "    return false;",
            "}",
            "",
            "// === Auto-generated hook stubs ===",
            "",
        ]

        for method in self.result.methods[:50]:
            addr = method.get("address")
            name = method.get("name", "unknown")
            ret_type = method.get("return_type", "void")
            params = method.get("parameters", [])

            if addr:
                param_list = ", ".join([f"void* arg{i}" for i in range(len(params))])
                lines.extend([
                    f"// Method: {name}",
                    f"// Address: 0x{addr:08X}",
                    f"// Return: {ret_type}",
                    f"typedef {ret_type} (*{name}_t)({param_list});",
                    f"{name}_t orig_{name} = nullptr;",
                    f"",
                    f"{ret_type} hook_{name}({param_list}) {{",
                    f'    LOGI("[GhostDumper] {name} called");',
                    f"    // Add your logic here",
                    f"    return orig_{name}({', '.join([f'arg{i}' for i in range(len(params))])});",
                    f"}}",
                    f"",
                ])

        lines.extend([
            "",
            "// Initialize all hooks",
            "bool initialize_hooks() {",
            "    g_base_addr = get_module_base(TARGET_MODULE);",
            "    if (!g_base_addr) return false;",
            "",
            '    LOGI("[GhostDumper] Base address: 0x%llx", g_base_addr);',
            "",
        ])

        for method in self.result.methods[:50]:
            name = method.get("name", "unknown")
            addr = method.get("address")
            if addr:
                base = self.result.binary_info.get("base_address", 0)
                offset = addr - base if addr > base else addr
                lines.append(
                    f'    hook_function(g_base_addr + 0x{offset:08X}, hook_{name}, &orig_{name});'
                )

        lines.extend([
            "",
            "    return true;",
            "}",
            "",
            "} // namespace hooks",
            "",
            "// Entry point",
            "__attribute__((constructor))",
            "void ghostdumper_init() {",
            "    hooks::initialize_hooks();",
            "}",
        ])

        path = self.output_dir / f"{self.stem}_hooks.cpp"
        with open(path, "w") as f:
            f.write("\n".join(lines))

    def _generate_pattern_scanner(self):
        """Generate pattern scanner helper."""
        lines = [
            "// GhostDumper v2.2 — Pattern Scanner",
            f"// Generated: {datetime.now().isoformat()}",
            "",
            "#include <cstdint>",
            "#include <cstring>",
            "",
            "namespace patterns {",
            "",
            "// Pattern: bytes with '?' as wildcard",
            "uintptr_t find_pattern(uintptr_t start, size_t size, const char* pattern) {",
            "    // Parse pattern string",
            '    // Example: "48 89 5C 24 ? 48 89 74 24 ? 57 48 83 EC 20"',
            "    ",
            "    // Simple implementation",
            "    return 0;",
            "}",
            "",
            "// Auto-generated patterns for key functions",
            "",
        ]

        # Generate patterns for important methods
        important_methods = ["il2cpp_init", "il2cpp_runtime_invoke", "il2cpp_string_new"]
        for method_name in important_methods:
            lines.extend([
                f"// Pattern for {method_name}",
                f"// TODO: Add known pattern from analysis",
                f'const char* pattern_{method_name} = "?? ?? ?? ??";',
                "",
            ])

        lines.extend([
            "",
            "} // namespace patterns",
        ])

        path = self.output_dir / f"{self.stem}_patterns.cpp"
        with open(path, "w") as f:
            f.write("\n".join(lines))
