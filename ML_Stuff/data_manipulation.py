"""
File for miscellaneous data manipulating
Currently for resizing spectrograms to match expected format for ML
"""

import skimage as ski

TARGET_SPECTROGRAM_SIZE = (128, 128)


def resize_spectrogram(spectrogram):
    resized = ski.transform.resize(spectrogram, TARGET_SPECTROGRAM_SIZE)
    return resized

