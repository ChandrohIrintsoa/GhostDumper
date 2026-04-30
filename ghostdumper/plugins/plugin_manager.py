"""
Plugin Manager for GhostDumper v2.2

Supports custom loader plugins, decryptor plugins, and output plugins.
Plugins can be loaded from ~/.config/ghostdumper/plugins/ or embedded.
"""

import importlib.util
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from abc import ABC, abstractmethod


class GhostPlugin(ABC):
    """Base class for GhostDumper plugins."""

    name: str = "unnamed"
    version: str = "1.0"
    author: str = "unknown"
    description: str = ""

    @abstractmethod
    def execute(self, result: Any) -> Dict[str, Any]:
        """Execute plugin on analysis result."""
        pass

    def is_compatible(self, result: Any) -> bool:
        """Check if plugin is compatible with current analysis."""
        return True


class LoaderPlugin(GhostPlugin):
    """Plugin for custom binary/metadata loading."""

    @abstractmethod
    def load_binary(self, path: str) -> Any:
        """Load a custom binary format."""
        pass

    @abstractmethod
    def load_metadata(self, path: str) -> Any:
        """Load custom metadata format."""
        pass


class DecryptorPlugin(GhostPlugin):
    """Plugin for custom decryption/obfuscation handling."""

    @abstractmethod
    def decrypt(self, data: bytes, params: Dict[str, Any]) -> bytes:
        """Decrypt data."""
        pass

    @abstractmethod
    def detect(self, data: bytes) -> float:
        """Detect if this decryptor can handle the data (0.0-1.0)."""
        pass


class OutputPlugin(GhostPlugin):
    """Plugin for custom output formats."""

    @abstractmethod
    def generate(self, result: Any, output_dir: Path) -> Path:
        """Generate custom output."""
        pass


class PluginManager:
    """Manage and execute GhostDumper plugins."""

    BUILTIN_PLUGINS = {
        "mihoyo": "plugins.builtin.mihoyo",
        "beebyte": "plugins.builtin.beebyte",
        "unity2021": "plugins.builtin.unity2021",
    }

    def __init__(self, config):
        self.config = config
        self.plugins: Dict[str, GhostPlugin] = {}
        self._load_builtin_plugins()

    def load_plugins(self):
        """Load plugins from plugin directory."""
        plugin_dir = self.config.get_plugin_dir()
        if not plugin_dir.exists():
            return

        for plugin_file in plugin_dir.glob("*.py"):
            self._load_plugin_file(plugin_file)

    def _load_builtin_plugins(self):
        """Load built-in plugins."""
        # Built-in plugins are loaded from the package
        pass

    def _load_plugin_file(self, path: Path):
        """Load a plugin from file."""
        try:
            spec = importlib.util.spec_from_file_location(path.stem, path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[path.stem] = module
            spec.loader.exec_module(module)

            # Find plugin class
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, GhostPlugin) and 
                    attr is not GhostPlugin):
                    plugin = attr()
                    self.plugins[plugin.name] = plugin
                    break
        except Exception as e:
            print(f"Failed to load plugin {path}: {e}")

    def register_plugin(self, plugin: GhostPlugin):
        """Register a plugin instance."""
        self.plugins[plugin.name] = plugin

    def execute_all(self, result: Any) -> Dict[str, Any]:
        """Execute all compatible plugins."""
        results = {}

        for name, plugin in self.plugins.items():
            if plugin.is_compatible(result):
                try:
                    plugin_result = plugin.execute(result)
                    results[name] = {
                        "success": True,
                        "data": plugin_result,
                    }
                except Exception as e:
                    results[name] = {
                        "success": False,
                        "error": str(e),
                    }

        return results

    def get_plugin(self, name: str) -> Optional[GhostPlugin]:
        """Get plugin by name."""
        return self.plugins.get(name)

    def list_plugins(self) -> List[Dict[str, str]]:
        """List all loaded plugins."""
        return [
            {
                "name": p.name,
                "version": p.version,
                "author": p.author,
                "description": p.description,
            }
            for p in self.plugins.values()
        ]
