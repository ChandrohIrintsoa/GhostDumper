"""
Type Resolution Engine for GhostDumper v2.2

Cross-references metadata with binary symbols to reconstruct
the complete IL2CPP type system.
"""

from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, field

from .metadata_parser import MetadataParser
from .binary_loader import BinaryLoader


class TypeResolver:
    """Resolves IL2CPP types and maps them to binary addresses."""

    def __init__(self, metadata: MetadataParser, binary: Optional[BinaryLoader], config):
        self.metadata = metadata
        self.binary = binary
        self.config = config

        self.types: List[Dict[str, Any]] = []
        self.methods: List[Dict[str, Any]] = []
        self.fields: List[Dict[str, Any]] = []
        self.vtables: List[Dict[str, Any]] = []

        # Symbol lookup cache
        self._symbol_cache: Dict[str, int] = {}

    def resolve(self):
        """Run full type resolution."""
        self._build_symbol_cache()
        self._resolve_types()
        self._resolve_methods()
        self._resolve_fields()
        self._resolve_vtables()
        self._cross_reference()

    def _build_symbol_cache(self):
        """Build fast symbol lookup cache."""
        if not self.binary:
            return

        for sym in self.binary.symbols:
            name = sym.get("name", "")
            if name:
                self._symbol_cache[name] = sym.get("address", 0)
                # Also cache demangled name
                try:
                    import cxxfilt
                    demangled = cxxfilt.demangle(name)
                    if demangled != name:
                        self._symbol_cache[demangled] = sym.get("address", 0)
                except:
                    pass

    def _resolve_types(self):
        """Resolve type definitions."""
        for type_def in self.metadata.types:
            type_info = {
                "name": type_def.name,
                "namespace": type_def.namespace,
                "full_name": f"{type_def.namespace}.{type_def.name}" if type_def.namespace else type_def.name,
                "image_index": type_def.image_index,
                "parent": None,
                "interfaces": [],
                "methods": [],
                "fields": [],
                "token": type_def.token,
                "flags": type_def.flags,
                "vtable_size": type_def.vtable_count,
            }

            # Resolve parent
            if type_def.parent_index >= 0:
                parent = self._get_type_by_index(type_def.parent_index)
                if parent:
                    type_info["parent"] = parent.name

            self.types.append(type_info)

    def _resolve_methods(self):
        """Resolve method definitions with binary addresses."""
        for method in self.metadata.methods:
            method_info = {
                "name": method.name,
                "return_type": method.return_type,
                "parameters": method.parameter_types,
                "flags": method.flags,
                "token": method.token,
                "slot": method.slot,
                "is_generic": method.is_generic,
                "generic_params": method.generic_params,
                "address": None,
                "size": 0,
            }

            # Try to find binary address
            if self.binary:
                addr = self._find_method_address(method)
                if addr:
                    method_info["address"] = addr

            self.methods.append(method_info)

    def _resolve_fields(self):
        """Resolve field definitions with offsets."""
        for field in self.metadata.fields:
            field_info = {
                "name": field.name,
                "type": field.type,
                "offset": field.offset,
                "token": field.token,
                "flags": field.flags,
                "default_value": field.default_value,
            }
            self.fields.append(field_info)

    def _resolve_vtables(self):
        """Resolve virtual method tables."""
        pass

    def _cross_reference(self):
        """Cross-reference types, methods, and fields."""
        # Link methods and fields to their parent types
        for type_info in self.types:
            type_info["methods"] = [m for m in self.methods if self._belongs_to(m, type_info)]
            type_info["fields"] = [f for f in self.fields if self._belongs_to(f, type_info)]

    def _find_method_address(self, method) -> Optional[int]:
        """Find binary address for a method."""
        # Try symbol cache
        for key in [method.name, f"{method.name}_method", f"_{method.name}"]:
            if key in self._symbol_cache:
                return self._symbol_cache[key]

        # Try pattern matching on token
        if method.token:
            # Search for token reference in binary
            pass

        return None

    def _get_type_by_index(self, index: int) -> Optional[Any]:
        """Get type by metadata index."""
        if 0 <= index < len(self.metadata.types):
            return self.metadata.types[index]
        return None

    def _belongs_to(self, item: Dict, type_info: Dict) -> bool:
        """Check if method/field belongs to type."""
        # Simplified - would need proper token analysis
        return True

    def get_class_hierarchy(self, class_name: str) -> List[str]:
        """Get inheritance chain for a class."""
        hierarchy = []
        current = self._find_type(class_name)

        while current:
            hierarchy.append(current["name"])
            parent_name = current.get("parent")
            current = self._find_type(parent_name) if parent_name else None

        return hierarchy

    def _find_type(self, name: str) -> Optional[Dict]:
        """Find type by name."""
        for t in self.types:
            if t["name"] == name or t["full_name"] == name:
                return t
        return None

    def find_methods_by_pattern(self, pattern: str) -> List[Dict]:
        """Find methods matching pattern."""
        import re
        regex = re.compile(pattern, re.IGNORECASE)
        return [m for m in self.methods if regex.search(m["name"])]

    def find_classes_by_pattern(self, pattern: str) -> List[Dict]:
        """Find classes matching pattern."""
        import re
        regex = re.compile(pattern, re.IGNORECASE)
        return [t for t in self.types if regex.search(t["name"]) or regex.search(t.get("full_name", ""))]
