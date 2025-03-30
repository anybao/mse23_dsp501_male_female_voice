# Male vs Female Voice Classification

## Introduction
This project classifies male and female voices using the occurrence pattern of spectral flux. It applies digital signal processing (DSP) techniques to analyze the spectral characteristics of voice recordings and determine gender based on frequency changes.

## Instructions

1. **Installation**
   - Ensure you have Python installed (preferably Python 3.8+).
   - Install required dependencies using:
     ```bash
     pip install -r requirements.txt
     ```

2. **Running the Application**
   - To start the desktop application, run:
     ```bash
     python app.py
     ```
   - Select an audio file or record your voice for analysis.
   - The application will process the input and display the classification results.

3. **Testing with Dataset**
   - Place male voice samples in `data/males/` and female voice samples in `data/females/`.
   - Run the Jupyter Notebook to determine the best threshold value for classification:
     ```bash
     python test_threshold.ipynb
     ```

4. **Understanding the Algorithm**
   - The classification is based on spectral flux variations.
   - A threshold is used to differentiate between male and female voices based on spectral flux occurrences.
   - The best threshold is determined through dataset evaluation.

5. **Troubleshooting**
   - If you encounter issues, check your dependencies and ensure audio files are in the correct format (WAV, 16kHz sample rate).
   - Enable debug mode in `config.py` for detailed logs.

## Contribution
Feel free to contribute by submitting issues or pull requests. Feedback and improvements are welcome!
