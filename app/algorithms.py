import base64
import librosa
import matplotlib

from app.sound_analyze import analyze_new_audio

matplotlib.use('Agg')  # Use a non-interactive backend
import matplotlib.pyplot as plt
import io

# Function to classify voice
def classify_voice(file_path):
    result, confidence = analyze_new_audio(file_path)
    return result, confidence
    # return "Male" if pitch < 165 else "Female"


# Function to generate waveform image and return as Base64
def generate_waveform_image(audio_path):
    y, sr = librosa.load(audio_path, sr=16000)
    plt.figure(figsize=(10, 3), facecolor='black')  # Dark theme
    plt.plot(y, color="cyan", linewidth=2.5, alpha=0.8)  # Neon-style waveform
    plt.gca().set_facecolor('black')  # Set plot background to black
    plt.axis("off")  # Remove axes for a clean look

    # Save image to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", pad_inches=0, transparent=True)
    buf.seek(0)
    plt.close()

    # Encode to Base64
    return base64.b64encode(buf.getvalue()).decode("utf-8")
