"""
File for miscellaneous data manipulating
And for the function that does the 'full data processing', so there's one function for the whole stack
"""

import numpy as np
import skimage as ski
from spectrogram_stuff import build_spectrogram_matrix, build_spectrogram_matrix_efficient

TARGET_SPECTROGRAM_SIZE = (128, 128)


def resize_spectrogram(spectrogram):
    resized = ski.transform.resize(spectrogram, TARGET_SPECTROGRAM_SIZE)
    return resized


def full_process_frames(raw_radar_frames):
    """
    Function performing the full processing
    From raw frames to final input to ml algorithm
    Use (or modify) this method to keep all processing consistent
    between training and decision
    """
    spectrogram = build_spectrogram_matrix_efficient(raw_radar_frames)
    print(np.shape(spectrogram))
    resized = resize_spectrogram(spectrogram)
    return resized