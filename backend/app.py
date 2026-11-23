import os
import sys
import uuid

from flask import Flask, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))          # .../backend
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))   # project root
UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, "uploads")
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")
STATIC_DIR = os.path.join(PROJECT_ROOT, "static")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Make sure `database.py` and `model.py` in this folder can be imported
sys.path.insert(0, BASE_DIR)

from database import get_history, init_db, save_prediction  # noqa: E402
from model import predict_image  # noqa: E402

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="/static")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB upload limit

# Runs on import, so it also works under gunicorn (not only `python app.py`)
init_db()


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/result")
def result_page():
    return send_from_directory(FRONTEND_DIR, "result.html")


@app.route("/history")
def history_page():
    return send_from_directory(FRONTEND_DIR, "history.html")


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------
@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Only PNG, JPG, JPEG or WEBP images are allowed"}), 400

    filename = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
    file.save(file_path)

    try:
        result = predict_image(file_path)
        confidence = float(result["confidence"])

        save_prediction(unique_name, result["disease"], confidence)

        return jsonify({
            "filename": unique_name,
            "prediction": result["disease"],
            "label": result["label"],
            "confidence": round(confidence, 4),
            "confidence_percent": round(confidence * 100, 2),
            "description": result["description"],
            "solution": result["solution"],
        })
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/history")
def history():
    return jsonify({"history": get_history()})


@app.errorhandler(413)
def file_too_large(_):
    return jsonify({"error": "File too large (max 10 MB)"}), 413


# ---------------------------------------------------------------------------
# Local run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("======================================")
    print("       LEAFGUARD BACKEND STARTING")
    print("======================================")
    print(f"Open: http://127.0.0.1:{port}")
    print("======================================")
    app.run(host="0.0.0.0", port=port, debug=False)