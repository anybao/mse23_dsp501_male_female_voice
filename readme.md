# Male vs Female Voice Classification

## Introduction
This project implements a male vs female voice classification system based on the paper **"Discrimination of Male and Female Voice Using Occurrence Pattern of Spectral Flux"**. It analyzes spectral flux patterns to distinguish between male and female voices.

The project includes:
- A **web application** for online classification.
- A **desktop application** for offline analysis and visualization.

## Requirements
Ensure you have the following dependencies installed:

### Common Dependencies
- Python 3.8+
- `librosa`
- `numpy`
- `matplotlib`
- `PyQt6` (for the desktop app)
- `Flask` (for the web app)

Install dependencies via:

```
pip install -r requirements.txt
```

## Project Structure
```
/              # Web-based application (Flask)
/desktop       # Desktop application (PyQt6)
/data          # Contains sample male/female voice recordings
/app           # Core algorithm and logic
```

## Instructions

### Web Application
1. Navigate to the `webapp` directory:
   ```
   cd /
   ```
2. Start the Flask server:
   ```
   python run.py
   ```
3. Open the browser and access `http://127.0.0.1:5000`.

### Desktop Application
1. Navigate to the `desktop-app` directory:
   ```
   cd desktop-app
   ```
2. Run the application:
   ```
   python app.py
   ```
3. Use the UI to load an audio file or record and analyze.

## Algorithm Overview
The classification is based on spectral flux patterns:
- Compute the **Spectral Centroid**.
- Analyze **Spectral Flux Variability**.
- Count high flux occurrences.
- Compare against a **threshold** to classify gender.

## Troubleshooting
- If dependencies fail, ensure you have the correct Python version.
- For audio processing errors, check `librosa` installation.

## Contribution
Feel free to contribute by submitting issues or pull requests!
