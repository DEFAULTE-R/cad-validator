import os
import uuid
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from src.validator import CADValidator

app = Flask(__name__)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.route("/")
def index():
    return send_from_directory("web", "app.html")


@app.route("/api/validate", methods=["POST"])
def validate():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if not (file.filename.endswith(".step") or file.filename.endswith(".stp")):
        return jsonify({"error": "Only STEP files supported"}), 400

    uid = str(uuid.uuid4())[:8]
    save_path = UPLOAD_DIR / f"{uid}_{file.filename}"
    file.save(save_path)

    try:
        v = CADValidator()
        results = v.validate(str(save_path))
        results["filename"] = file.filename
        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
