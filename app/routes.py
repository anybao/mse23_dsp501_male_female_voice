import base64
import logging
import os
import time

from flask import Blueprint, render_template, request, jsonify
from app.algorithms import classify_voice, generate_waveform_image
from pydub import AudioSegment

bp = Blueprint("routes", __name__)


@bp.route("/")
def index():
    return render_template("index.html")


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def get_file_size(file_path):
    """ Returns file size in MB """
    return round(os.path.getsize(file_path) / (1024 * 1024), 2)


@bp.route("/classify", methods=["POST"])
def classify():
    try:
        if "file" not in request.files:
            logging.warning("No file uploaded in request.")
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        base_dir = os.getenv('BASE_PATH', os.getcwd())
        data_dir = os.path.join(base_dir, 'data')
        os.makedirs(data_dir, exist_ok=True)  # Ensure 'data' directory exists

        timestamp = str(int(time.time()))
        file_path = os.path.join(data_dir, f"{timestamp}_temp_audio.wav")

        # Save uploaded file first
        logging.info(f"Saving uploaded audio: {file_path}")
        file.save(file_path)

        file_size = get_file_size(file_path)
        logging.info(f"Uploaded file size: {file_size} MB")

        # Convert to WAV using pydub
        wav_path = file_path.replace(".wav", "_converted.wav")
        logging.info(f"Converting audio to WAV: {wav_path}")

        audio = AudioSegment.from_file(file_path)
        audio.export(wav_path, format="wav")

        converted_size = get_file_size(wav_path)
        logging.info(f"Converted file size: {converted_size} MB")

        # Extract pitch and classify
        logging.info("Starting voice classification...")
        classification, confidence = classify_voice(wav_path)

        logging.info(f"Classification result: {classification} with confidence {confidence}")

        # Generate waveform image
        logging.info("Generating waveform image...")
        waveform_base64 = generate_waveform_image(file_path)

        # Clean up temporary audio files
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(wav_path):
            os.remove(wav_path)

        return jsonify({
            "confidence": float(confidence),  # Convert float32 to float
            "classification": classification,
            "waveform": waveform_base64  # Base64-encoded image
        })

    except Exception as e:
        logging.error(f"Error processing audio: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500
