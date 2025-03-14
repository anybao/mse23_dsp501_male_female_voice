import os
import time

from flask import Blueprint, render_template, request, jsonify

from app.algorithms import get_pitch, classify_voice, generate_waveform_image

bp = Blueprint("routes", __name__)


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/classify", methods=["POST"])
def classify():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    file_path = "./" + str(int(time.time())) + "_temp_audio.wav"
    file.save(file_path)

    # Extract pitch and classify
    pitch = get_pitch(file_path)
    classification = classify_voice(pitch)

    # Generate waveform image
    waveform_image = generate_waveform_image(file_path)

    if os.path.exists(file_path):
        os.remove(file_path)

    return jsonify({
        "pitch": float(pitch),  # Convert float32 to float
        "classification": classification,
        "waveform": waveform_image  # Base64-encoded image
    })
