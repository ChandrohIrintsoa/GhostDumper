
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import json


@dataclass
class SearchResult:
    """Result from semantic search."""
    item_type: str  # "class", "method", "field", "string"
    name: str
    score: float
    data: Dict[str, Any]
    context: str = ""


class SemanticAgent:
    """Agentic AI for IL2CPP code analysis."""

    def __init__(self, result, config):
        self.result = result
        self.config = config
        self.embeddings_available = False
        self._embedding_model = None
        self._vector_store = {}

        if config.enable_agent:
            self._init_embeddings()

    def _init_embeddings(self):
        """Initialize embedding model."""
        try:
            from sentence_transformers import SentenceTransformer
            self._embedding_model = SentenceTransformer(self.config.embedding_model)
            self.embeddings_available = True
            self._build_index()
        except ImportError:
            self.embeddings_available = False

    def _build_index(self):
        """Build vector index for semantic search."""
        if not self.embeddings_available:
            return

        texts = []
        items = []

        # Index classes
        for type_info in self.result.types:
            context = f"Class {type_info.get('name', '')} in namespace {type_info.get('namespace', '')}"
            if type_info.get('parent'):
                context += f", inherits from {type_info['parent']}"
            texts.append(context)
            items.append(("class", type_info))

        # Index methods
        for method in self.result.methods:
            context = f"Method {method.get('name', '')} returns {method.get('return_type', 'void')}"
            params = method.get('parameters', [])
            if params:
                context += f", parameters: {', '.join(params)}"
            texts.append(context)
            items.append(("method", method))

        # Index strings
        for i, s in enumerate(self.result.strings[:5000]):
            if len(s) > 3:
                texts.append(f"String: {s}")
                items.append(("string", {"value": s, "index": i}))

        if texts:
            embeddings = self._embedding_model.encode(texts, show_progress_bar=False)
            self._vector_store = {
                "items": items,
                "embeddings": embeddings,
            }

    def query(self, query: str, top_k: int = 10) -> List[SearchResult]:
        """Execute natural language query."""
        if self.embeddings_available and self._vector_store:
            return self._semantic_search(query, top_k)
        else:
            return self._fallback_search(query, top_k)

    def _semantic_search(self, query: str, top_k: int) -> List[SearchResult]:
        """Semantic search using embeddings."""
        from numpy import dot
        from numpy.linalg import norm

        query_embedding = self._embedding_model.encode([query])[0]
        embeddings = self._vector_store["embeddings"]
        items = self._vector_store["items"]

        # Compute cosine similarity
        similarities = []
        for i, emb in enumerate(embeddings):
            sim = dot(query_embedding, emb) / (norm(query_embedding) * norm(emb))
            similarities.append((sim, i))

        # Sort by similarity
        similarities.sort(reverse=True)

        results = []
        for sim, idx in similarities[:top_k]:
            item_type, data = items[idx]
            name = data.get("name", data.get("value", "unknown"))
            results.append(SearchResult(
                item_type=item_type,
                name=name,
                score=float(sim),
                data=data,
            ))

        return results

    def _fallback_search(self, query: str, top_k: int) -> List[SearchResult]:
        """Fallback keyword search when embeddings unavailable."""
        query_lower = query.lower()
        results = []

        # Search classes
        for type_info in self.result.types:
            name = type_info.get("name", "")
            namespace = type_info.get("namespace", "")
            if query_lower in name.lower() or query_lower in namespace.lower():
                results.append(SearchResult(
                    item_type="class",
                    name=name,
                    score=0.8,
                    data=type_info,
                ))

        # Search methods
        for method in self.result.methods:
            name = method.get("name", "")
            if query_lower in name.lower():
                results.append(SearchResult(
                    item_type="method",
                    name=name,
                    score=0.7,
                    data=method,
                ))

        # Search strings
        for i, s in enumerate(self.result.strings):
            if query_lower in s.lower():
                results.append(SearchResult(
                    item_type="string",
                    name=s[:50],
                    score=0.6,
                    data={"value": s, "index": i},
                ))

        # Sort by score and limit
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

    def find_class_hierarchy(self, class_name: str) -> Dict[str, Any]:
        """Find full class hierarchy."""
        hierarchy = {
            "class": class_name,
            "parents": [],
            "children": [],
            "siblings": [],
        }

        # Find the class
        target = None
        for type_info in self.result.types:
            if type_info["name"] == class_name:
                target = type_info
                break

        if not target:
            return hierarchy

        # Build parent chain
        current = target
        while current and current.get("parent"):
            parent_name = current["parent"]
            hierarchy["parents"].append(parent_name)

            # Find parent class
            current = None
            for t in self.result.types:
                if t["name"] == parent_name:
                    current = t
                    break

        # Find children
        for type_info in self.result.types:
            if type_info.get("parent") == class_name:
                hierarchy["children"].append(type_info["name"])

        # Find siblings (same parent)
        parent = target.get("parent")
        if parent:
            for type_info in self.result.types:
                if type_info.get("parent") == parent and type_info["name"] != class_name:
                    hierarchy["siblings"].append(type_info["name"])

        return hierarchy

    def find_cross_references(self, name: str) -> Dict[str, List[str]]:
        """Find cross-references to a class/method."""
        refs = {
            "called_by": [],
            "calls": [],
            "uses_fields": [],
        }

        # Simple string-based cross-reference
        for method in self.result.methods:
            method_name = method.get("name", "")
            if name in method_name and method_name != name:
                refs["called_by"].append(method_name)

        return refs

    def analyze_security(self) -> Dict[str, Any]:
        """Analyze binary for security-relevant patterns."""
        findings = {
            "crypto_methods": [],
            "network_methods": [],
            "obfuscation_indicators": [],
            "dangerous_apis": [],
        }

        crypto_patterns = ["encrypt", "decrypt", "aes", "rsa", "cipher", "hash", "md5", "sha"]
        network_patterns = ["http", "socket", "tcp", "udp", "request", "response", "download"]
        dangerous_patterns = ["exec", "system", "popen", "shell", "eval"]

        for method in self.result.methods:
            name = method.get("name", "").lower()

            for pattern in crypto_patterns:
                if pattern in name:
                    findings["crypto_methods"].append(method)
                    break

            for pattern in network_patterns:
                if pattern in name:
                    findings["network_methods"].append(method)
                    break

            for pattern in dangerous_patterns:
                if pattern in name:
                    findings["dangerous_apis"].append(method)
                    break

        return findings
