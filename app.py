import os
import uuid
from flask import Flask, request, jsonify, send_from_directory
from pathlib import Path
from src.validator import CADValidator

app = Flask(__name__)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.route("/")
def index():
    return send_from_directory("web", "app.html")

@app.route("/api/validate", methods=["POST"])
def validate():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if not file.filename.endswith(".step") and not file.filename.endswith(".stp"):
        return jsonify({"error": "Only STEP files (.step / .stp) are supported"}), 400

    # save uploaded file
    uid = str(uuid.uuid4())[:8]
    save_path = UPLOAD_DIR / f"{uid}_{file.filename}"
    file.save(save_path)

    try:
        min_wall = float(request.form.get("min_wall", 2.0))
        max_overhang = float(request.form.get("max_overhang", 45.0))
        min_radius = float(request.form.get("min_radius", 1.0))

        v = CADValidator(
            min_wall_mm=min_wall,
            max_overhang_deg=max_overhang,
            min_radius_mm=min_radius
        )
        results = v.validate(str(save_path))
        results["filename"] = file.filename
        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if save_path.exists():
            os.remove(save_path)

@app.route("/api/sample/<name>")
def validate_sample(name):
    allowed = ["thin_wall", "overhang", "clean_part"]
    if name not in allowed:
        return jsonify({"error": "Unknown sample"}), 404

    path = Path(f"tests/sample_files/{name}.step")
    v = CADValidator()
    results = v.validate(str(path))
    results["filename"] = f"{name}.step"
    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
