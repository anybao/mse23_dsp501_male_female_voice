import os
import time

from flask import Blueprint, render_template, request, jsonify
from app.algorithms import classify_voice, generate_waveform_image

bp = Blueprint("routes", __name__)


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/classify", methods=["POST"])
def classify():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    base_dir = os.getenv('BASE_PATH', os.getcwd())
    file_path = os.path.join(base_dir, 'data', str(int(time.time())) + "_temp_audio.wav")
    print('Record voice: ' + file_path)
    file.save(file_path)

    # Extract pitch and classify
    classification, confidence = classify_voice(file_path)

    # Generate waveform image
    waveform_image = generate_waveform_image(file_path)

    if os.path.exists(file_path):
        os.remove(file_path)

    return jsonify({
        "confidence": float(confidence),  # Convert float32 to float
        "classification": classification,
        "waveform": waveform_image  # Base64-encoded image
    })
