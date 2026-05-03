# GhostDumper v2.2 API Documentation

## Python API

### GhostEngine

```python
from ghostdumper import GhostEngine, GhostConfig

config = GhostConfig(
    so_path="libil2cpp.so",
    metadata_path="global-metadata.dat",
    output_dir="./results",
    deobfuscate=True,
    deobf_type="xor",
)

engine = GhostEngine(config)
result = engine.analyze()

print(f"Classes: {len(result.types)}")
print(f"Methods: {len(result.methods)}")
```

### SemanticAgent

```python
from ghostdumper.agents.semantic_agent import SemanticAgent

agent = SemanticAgent(result, config)

# Search by natural language
results = agent.query("Find player health methods")

# Get class hierarchy
hierarchy = agent.find_class_hierarchy("PlayerController")

# Security analysis
security = agent.analyze_security()
```

## REST API

### POST /api/analyze
Upload files and start analysis.

**Request:**
```bash
curl -X POST -F "so_file=@libil2cpp.so" -F "metadata_file=@global-metadata.dat"   http://localhost:8080/api/analyze
```

**Response:**
```json
{
  "success": true,
  "duration": 12.34,
  "classes": 1500,
  "methods": 8500,
  "output_dir": "/tmp/ghostdumper_web"
}
```

### POST /api/search
Semantic search over analysis results.

**Request:**
```bash
curl -X POST -H "Content-Type: application/json"   -d '{"query": "Find encryption methods", "top_k": 10}'   http://localhost:8080/api/search
```

### GET /api/hierarchy/<class_name>
Get class inheritance hierarchy.

### GET /api/download/<filename>
Download generated output file.

## CLI API

```bash
# Basic analysis
ghostdump -s libil2cpp.so -m global-metadata.dat

# All formats
ghostdump -s libil2cpp.so -m global-metadata.dat --all-formats

# With deobfuscation
ghostdump -s libil2cpp.so -m global-metadata.dat --deobfuscate xor

# Agentic query
ghostdump -s libil2cpp.so -m global-metadata.dat --agent "Find Player class"

# Web UI
ghostdump --web --port 8080

# JSON output
ghostdump -s libil2cpp.so -m global-metadata.dat --json
```
