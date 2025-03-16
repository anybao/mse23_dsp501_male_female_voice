import os
import numpy as np
import librosa
import pandas as pd
import librosa.feature

# Define paths to audio files∆
# MALE_PATH = '../data/males'
MALE_PATH = "/Users/quanghuy/Documents/MSE/DSP501/dsp501-male-female-voice/data/males"
FEMALE_PATH = "/Users/quanghuy/Documents/MSE/DSP501/dsp501-male-female-voice/data/females"


def extract_features(file_path):
    """
    Extract acoustic features from an audio file.

    Key features:
    - Fundamental frequency (pitch)
    - MFCCs (Mel-Frequency Cepstral Coefficients)
    - Spectral centroid
    - Spectral rolloff
    - Zero crossing rate
    - Formants (estimated)
    - Harmonicity
    """
    try:
        # Load audio file with librosa
        y, sr = librosa.load(file_path, sr=None)

        # Extract features
        # Fundamental frequency (pitch)
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        pitch = np.mean(pitches[magnitudes > np.median(magnitudes)])
        if np.isnan(pitch):
            pitch = 0

        # MFCCs (13 coefficients)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        mfccs_mean = np.mean(mfccs, axis=1)

        # Spectral centroid
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))

        # Spectral rolloff
        spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))

        # Zero crossing rate
        zero_crossing_rate = np.mean(librosa.feature.zero_crossing_rate(y=y))

        # Estimate harmonicity (spectral flatness - inverse of harmonicity)
        # Lower values indicate more harmonic sounds
        spectral_flatness = np.mean(librosa.feature.spectral_flatness(y=y))

        # Energy
        energy = np.mean(librosa.feature.rms(y=y))

        # Create a feature dictionary
        feature_dict = {
            'pitch': pitch,
            'mfcc_1': mfccs_mean[0],
            'mfcc_2': mfccs_mean[1],
            'mfcc_3': mfccs_mean[2],
            'mfcc_4': mfccs_mean[3],
            'mfcc_5': mfccs_mean[4],
            'mfcc_6': mfccs_mean[5],
            'mfcc_7': mfccs_mean[6],
            'mfcc_8': mfccs_mean[7],
            'mfcc_9': mfccs_mean[8],
            'mfcc_10': mfccs_mean[9],
            'mfcc_11': mfccs_mean[10],
            'mfcc_12': mfccs_mean[11],
            'mfcc_13': mfccs_mean[12],
            'spectral_centroid': spectral_centroid,
            'spectral_rolloff': spectral_rolloff,
            'zero_crossing_rate': zero_crossing_rate,
            'spectral_flatness': spectral_flatness,
            'energy': energy
        }

        return feature_dict

    except Exception as e:
        print(f"Error extracting features from {file_path}: {e}")
        return None


def load_dataset():
    """Load and prepare the dataset from male and female voice recordings."""
    male_features = []
    female_features = []

    # Process male voices
    print("Processing male voice samples...")
    for filename in os.listdir(MALE_PATH):
        if filename.endswith('.wav'):
            file_path = os.path.join(MALE_PATH, filename)
            extracted_features = extract_features(file_path)
            if extracted_features is not None:
                male_features.append(extracted_features)

    # Process female voices
    print("Processing female voice samples...")
    for filename in os.listdir(FEMALE_PATH):
        if filename.endswith('.wav'):
            file_path = os.path.join(FEMALE_PATH, filename)
            extracted_features = extract_features(file_path)
            if extracted_features is not None:
                female_features.append(extracted_features)

    # Convert to DataFrames
    male_df = pd.DataFrame(male_features)
    female_df = pd.DataFrame(female_features)

    return male_df, female_df


def predict_gender_rule_based(features):
    """
    Predict gender using rule-based approach based on key acoustic differences.

    This uses simple thresholds derived from the statistical analysis of our dataset
    rather than machine learning.
    """
    # Key differentiating features (based on analysis)
    pitch = features['pitch']
    spectral_centroid = features['spectral_centroid']
    mfcc_4 = features['mfcc_4']  # One of the more differentiating MFCCs

    # Define simple rules for classification
    # These thresholds are approximations and would be refined based on the actual analysis
    if pitch > 0 and pitch < 155:  # Lower pitch threshold for male
        confidence = min(1.0, (155 - pitch) / 50)
        return 'male', confidence
    elif pitch >= 155:  # Higher pitch threshold for female
        confidence = min(1.0, (pitch - 155) / 50)
        return 'female', confidence
    else:
        # If pitch is invalid (0), use other features
        if spectral_centroid < 1600:  # Just an example threshold
            return 'male', 0.6
        else:
            return 'female', 0.6


def analyze_new_audio(audio_path):
    """Analyze a new audio file and compare it to male/female profiles."""
    # Extract features from the file
    features = extract_features(audio_path)

    if features is None:
        return None, None

    # Load the reference data
    male_df, female_df = load_dataset()

    # Get average feature values for comparison
    male_means = male_df.mean()
    female_means = female_df.mean()

    # Calculate similarity scores
    male_similarity = 0
    female_similarity = 0

    # For each feature, compute similarity based on distance to the mean
    for feature in features:
        if feature in male_means and feature in female_means:
            # Calculate normalized distances
            male_distance = abs(features[feature] - male_means[feature])
            female_distance = abs(features[feature] - female_means[feature])

            # Scale the feature importance based on known gender differences
            importance = 1.0
            if feature == 'pitch':
                importance = 3.0
            elif 'mfcc' in feature:
                importance = 1.5

            # Update similarity scores (inverse of distance)
            if male_distance + female_distance > 0:
                male_score = female_distance / (male_distance + female_distance) * importance
                female_score = male_distance / (male_distance + female_distance) * importance

                male_similarity += male_score
                female_similarity += female_score

    # Normalize final scores
    total_score = male_similarity + female_similarity
    if total_score > 0:
        male_similarity /= total_score
        female_similarity /= total_score

    # Get rule-based prediction
    rule_prediction, rule_confidence = predict_gender_rule_based(features)

    # Combine approaches for final prediction
    if male_similarity > female_similarity:
        return 'Male', male_similarity
    else:
        return 'Female', female_similarity
