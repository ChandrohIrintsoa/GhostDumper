
import os
import json
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any

from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO, emit

from ..core.engine import GhostEngine
from ..core.config import GhostConfig
from ..agents.semantic_agent import SemanticAgent


app = Flask(__name__, 
           template_folder="templates",
           static_folder="static")
app.config["SECRET_KEY"] = os.environ.get("GHOSTDUMPER_SECRET", os.urandom(32))
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024 * 1024  # 2GB max upload

socketio = SocketIO(app, cors_allowed_origins="*")

# Global state
_current_analysis: Optional[Dict[str, Any]] = None


@app.route("/")
def index():
    """Main web interface."""
    return render_template("index.html")


@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    """API endpoint to start analysis."""
    config = GhostConfig()

    # Handle file uploads
    if "so_file" in request.files:
        so_file = request.files["so_file"]
        if so_file.filename:
            so_path = Path(tempfile.gettempdir()) / so_file.filename
            so_file.save(so_path)
            config.so_path = str(so_path)

    if "metadata_file" in request.files:
        meta_file = request.files["metadata_file"]
        if meta_file.filename:
            meta_path = Path(tempfile.gettempdir()) / meta_file.filename
            meta_file.save(meta_path)
            config.metadata_path = str(meta_path)

    # Handle text paths
    if request.form.get("so_path"):
        config.so_path = request.form["so_path"]
    if request.form.get("metadata_path"):
        config.metadata_path = request.form["metadata_path"]

    config.batch_mode = True
    config.generate_json = True
    config.generate_web_report = True

    output_dir = Path(tempfile.gettempdir()) / "ghostdumper_web"
    output_dir.mkdir(exist_ok=True)
    config.output_dir = str(output_dir)

    try:
        engine = GhostEngine(config)
        result = engine.analyze()

        global _current_analysis
        _current_analysis = {
            "result": result,
            "config": config,
            "output_dir": output_dir,
        }

        return jsonify({
            "success": True,
            "duration": result.duration,
            "classes": len(result.types),
            "methods": len(result.methods),
            "fields": len(result.fields),
            "output_dir": str(output_dir),
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/search", methods=["POST"])
def api_search():
    """API endpoint for semantic search."""
    if not _current_analysis:
        return jsonify({"error": "No analysis available. Run analysis first."}), 400

    if not request.json:
        return jsonify({"error": "Missing JSON body"}), 400
    
    query = request.json.get("query", "")
    top_k = request.json.get("top_k", 10)

    agent = SemanticAgent(_current_analysis["result"], _current_analysis["config"])
    results = agent.query(query, top_k)

    return jsonify({
        "query": query,
        "results": [
            {
                "type": r.item_type,
                "name": r.name,
                "score": r.score,
                "data": r.data,
            }
            for r in results
        ]
    })


@app.route("/api/hierarchy/<class_name>")
def api_hierarchy(class_name):
    """API endpoint for class hierarchy."""
    if not _current_analysis:
        return jsonify({"error": "No analysis available"}), 400

    agent = SemanticAgent(_current_analysis["result"], _current_analysis["config"])
    hierarchy = agent.find_class_hierarchy(class_name)

    return jsonify(hierarchy)


@app.route("/api/download/<filename>")
def api_download(filename):
    """Download generated file."""
    if not _current_analysis:
        return jsonify({"error": "No analysis available"}), 400

    file_path = (_current_analysis["output_dir"] / filename).resolve()
    if not str(file_path).startswith(str(_current_analysis["output_dir"].resolve())):
        return jsonify({"error": "Invalid filename"}), 400
    if file_path.exists():
        return send_file(file_path, as_attachment=True)

    return jsonify({"error": "File not found"}), 404


@socketio.on("connect")
def handle_connect():
    emit("status", {"message": "Connected to GhostDumper v2.2"})


@socketio.on("start_analysis")
def handle_start_analysis(data):
    """Handle analysis start via WebSocket."""
    emit("progress", {"stage": "initializing", "progress": 0})

    config = GhostConfig(
        so_path=data.get("so_path"),
        metadata_path=data.get("metadata_path"),
        batch_mode=True,
    )

    try:
        engine = GhostEngine(config)
        result = engine.analyze()

        emit("complete", {
            "duration": result.duration,
            "classes": len(result.types),
            "methods": len(result.methods),
        })
    except Exception as e:
        emit("error", {"message": str(e)})


def start_server(host: str = "0.0.0.0", port: int = 8080, debug: bool = False):
    """Start the web server."""
    socketio.run(app, host=host, port=port, debug=debug)
