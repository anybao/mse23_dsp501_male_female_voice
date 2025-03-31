import sys
import os
import librosa
import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd
import soundfile as sf
import noisereduce as nr
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QFileDialog, QVBoxLayout, QHBoxLayout, QFrame
from PyQt6.QtGui import QPixmap, QImage, QMovie
from PyQt6.QtCore import QThread, Qt, QTimer

class VoiceClassifierApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Voice Gender Classifier")
        self.setGeometry(100, 100, 500, 400)
        self.setStyleSheet("background-color: #2E2E2E; font-family: Arial;")

        # UI Elements
        self.label = QLabel("Chọn một tệp âm thanh để phân loại", self)
        self.label.setStyleSheet("font-size: 16px; font-weight: bold; color: white; padding: 10px;")

        self.select_button = QPushButton("📂 Chọn Tệp Âm Thanh", self)
        self.select_button.setStyleSheet("font-size: 14px; padding: 10px; border-radius: 10px; background-color: #4CAF50; color: white;")
        self.select_button.clicked.connect(self.load_audio)

        self.play_button = QPushButton("🔊 Phát Âm Thanh", self)
        self.play_button.setEnabled(False)
        self.play_button.setStyleSheet("font-size: 14px; padding: 10px; border-radius: 10px; background-color: #2196F3; color: white;")
        self.play_button.clicked.connect(self.play_audio)

        self.record_button = QPushButton("🎙 Ghi Âm (5s)", self)
        self.record_button.setStyleSheet("font-size: 14px; padding: 10px; border-radius: 10px; background-color: #FF9800; color: white;")
        self.record_button.clicked.connect(self.record_audio)

        self.result_label = QLabel("", self)
        self.result_label.setStyleSheet("font-size: 20px; color: white; font-weight: bold; padding: 10px; border: 2px solid #FFFFFF;")
        self.result_label.setVisible(False)

        self.image_label = QLabel(self)
        self.image_label.setStyleSheet("border: 2px solid #FFFFFF;")
        self.image_label.setVisible(False)

        self.loading_label = QLabel(self)
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setVisible(False)

        loading_gif = QMovie("loading.gif")  # Add a loading.gif file in the project directory
        self.loading_label.setMovie(loading_gif)
        self.loading_label.setFixedSize(100, 100)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.select_button)
        layout.addWidget(self.record_button)
        layout.addWidget(self.play_button)

        result_frame = QFrame(self)
        result_layout = QVBoxLayout()
        result_layout.addWidget(self.result_label)
        result_frame.setLayout(result_layout)
        result_frame.setStyleSheet("background-color: #3E3E3E; padding: 10px; border-radius: 8px;")

        layout.addWidget(result_frame)
        layout.addWidget(self.image_label)
        layout.addWidget(self.loading_label)

        self.setLayout(layout)

        self.audio_data = None  # Store loaded audio data
        self.sr = None  # Store sample rate

    def show_loading(self):
        self.loading_label.setVisible(True)
        self.loading_label.movie().start()
        QApplication.processEvents()  # Force UI update

    def hide_loading(self):
        self.loading_label.setVisible(False)
        self.loading_label.movie().stop()

    def record_audio(self):
        self.result_label.setVisible(False)
        self.image_label.setVisible(False)
        self.show_loading()
        duration = 5  # Record for 5 seconds
        sample_rate = 16000
        audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
        sd.wait()

        recorded_file = "recorded_audio.wav"
        sf.write(recorded_file, audio_data, sample_rate)

        self.load_audio(recorded_file)

    def load_audio(self, file_path=None):
        self.result_label.setVisible(False)
        self.image_label.setVisible(False)
        self.show_loading()

        if not file_path:
            file_path, _ = QFileDialog.getOpenFileName(self, "Chọn Tệp Âm Thanh", "", "Audio Files (*.wav)")

        if file_path:
            QTimer.singleShot(100, lambda: self.process_audio(file_path))  # Delay processing slightly

    def process_audio(self, file_path):
        # Load the audio
        self.audio_data, self.sr = librosa.load(file_path, sr=16000)
        
        # Apply noise reduction
        self.audio_data = self.reduce_noise(self.audio_data, self.sr)
        
        # Save the noise-reduced audio temporarily for analysis
        temp_file = "temp_processed.wav"
        sf.write(temp_file, self.audio_data, self.sr)
        
        result, occurrences = self.analyze_new_audio(temp_file)
        self.result_label.setText(f"🗣 Kết quả: {result}")
        self.result_label.setVisible(True)
        self.image_label.setVisible(True)
        
        self.plot_waveform(temp_file)
        self.play_button.setEnabled(True)
        self.hide_loading()
        
        # Clean up temporary file
        if os.path.exists(temp_file):
            os.remove(temp_file)

    def play_audio(self):
        if self.audio_data is not None:
            sd.play(self.audio_data, self.sr)

    def plot_waveform(self, file_path):
        y, sr = librosa.load(file_path, sr=16000)
        plt.figure(figsize=(5, 2))
        plt.plot(y, color="blue")
        plt.axis("off")

        # Save image
        img_path = "waveform.png"
        plt.savefig(img_path, bbox_inches="tight", pad_inches=0, transparent=True)
        plt.close()

        # Load into UI
        pixmap = QPixmap(img_path)
        self.image_label.setPixmap(pixmap)
        self.image_label.setScaledContents(True)

    def reduce_noise(self, audio_data, sr):
        """
        Reduce noise from the audio signal using the noisereduce library.
        """
        # Estimate noise from a portion of the signal (first 1000 samples)
        noise_sample = audio_data[:1000]
        
        # Perform noise reduction
        reduced_noise = nr.reduce_noise(
            y=audio_data,
            sr=sr,
            prop_decrease=1.0,
            stationary=True,
            n_std_thresh_stationary=1.5
        )
        
        return reduced_noise

    def analyze_new_audio(self, file_path, threshold=19):
        # Load and automatically apply noise reduction
        y, sr = librosa.load(file_path, sr=16000)
        
        # Compute Spectral Flux on the noise-reduced signal
        spectral_flux = np.diff(librosa.feature.spectral_centroid(y=y, sr=sr), axis=1)
        
        # Compute Occurrence Pattern of SF
        sf_mean = np.mean(spectral_flux)
        sf_std = np.std(spectral_flux)
        
        # Count occurrences above threshold
        high_sf_occurrences = np.sum(spectral_flux > sf_mean + sf_std)
        
        # Classify based on occurrence pattern of Spectral Flux
        if high_sf_occurrences > threshold:
            return "Female", high_sf_occurrences
        else:
            return "Male", high_sf_occurrences

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VoiceClassifierApp()
    window.show()
    sys.exit(app.exec())