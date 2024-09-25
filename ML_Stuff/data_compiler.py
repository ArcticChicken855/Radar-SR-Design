"""
Script for loading Raw pickles, categorizing by notes
Creating labels and separating into test/training datasets
And finally saving as 'compiled' pickles for model training
"""

import pathlib as p
import numpy as np
import math

from pickle_utils import *
from data_parsing import *
from spectrogram_stuff import build_spectrogram_matrix
from data_manipulation import *

# what portion of data should be used in training vs. testing
# ie 0.8 indicates that 80% of data should be used in training
TRAINING_TESTING_RATIO = 0.80

# Currently paths are hardcoded to my (William's) files
# I should probably change this Todo
root_path = p.Path().home() / "RadarData" / "2RadarData"
raw_data_path = root_path / "IQpickles"
compiled_data_path = root_path / "CompiledData"


def get_valid_data_only(data_array):
    output_array = []
    for data in data_array:
        if is_data_valid(data):
            output_array.append(data)

    return output_array


def separate_falls(data_array):
    fall_array = []
    non_fall_array = []
    for data in data_array:
        if is_data_fall(data):
            fall_array.append(data)
        else:
            non_fall_array.append(data)

    return [fall_array, non_fall_array]


def get_radar_data(data_array):
    """
    Given an array of full data
    Returns a new array containing only the radar frames
    This includes the radar frames from both radar1 and radar2
    """

    output_array = []
    for data in data_array:
        output_array.append(get_radar1_frames(data))
        output_array.append(get_radar2_frames(data))

    return output_array


def get_spectrograms(radar_data_array):
    """
    Given an array of radar data
    Returns a new array of the spectrograms
    """

    output_array = []
    for radar_data in radar_data_array:
        spectrogram = build_spectrogram_matrix(radar_data)
        output_array.append(spectrogram)

    return output_array


def resize_spectrograms(spectrogram_array):
    """
    Given an array of spectrograms
    Return a new array of resized spectrograms according to data_manipulation.resize_spectrogram()
    """

    output_array = []
    for spectrogram in spectrogram_array:
        resized = resize_spectrogram(spectrogram)
        output_array.append(resized)

    return output_array


def split_training_vs_testing(data_array):
    data_count = len(data_array)
    training_count = math.ceil(data_count * TRAINING_TESTING_RATIO)

    training_data_array = data_array[0:training_count]
    testing_data_array = data_array[training_count:data_count]

    return [training_data_array, testing_data_array]


def main():
    print("Collecting Data.")
    data_array = get_all_data_from_path(raw_data_path)
    print("Found " + str(len(data_array)) + " recordings.")

    data_array = get_valid_data_only(data_array)
    print("Identified " + str(len(data_array)) + " valid recordings.")

    fall_array, non_fall_array = separate_falls(data_array)
    print("Identified " + str(len(fall_array)) + " falls.")
    print("Identified " + str(len(non_fall_array)) + " non-falls.")
    print("\n")

    print("Collecting Radar Frames.")
    fall_radar_data = get_radar_data(fall_array)
    non_fall_radar_data = get_radar_data(non_fall_array)
    print("Collected " + str(len(fall_radar_data)) + " falls.")
    print("Collected " + str(len(non_fall_radar_data)) + " non-falls.")
    print("\n")

    print("Creating Spectrograms.")
    fall_spectrograms = get_spectrograms(fall_radar_data)
    non_fall_spectrograms = get_spectrograms(non_fall_radar_data)

    print("Resizing Spectrograms.")
    fall_spectrograms_resized = resize_spectrograms(fall_spectrograms)
    non_fall_spectrograms_resized = resize_spectrograms(non_fall_spectrograms)
    print("\n")

    print("Splitting into Training and Testing Arrays.")
    fall_training_data, fall_testing_data = split_training_vs_testing(fall_spectrograms_resized)
    non_fall_training_data, non_fall_testing_data = split_training_vs_testing(non_fall_spectrograms_resized)
    print("Collected " + str(len(fall_training_data)) + " fall training data.")
    print("Collected " + str(len(fall_testing_data)) + " fall testing data.")
    print("Collected " + str(len(non_fall_training_data)) + " non-fall training data.")
    print("Collected " + str(len(non_fall_testing_data)) + " non-fall testing data.")
    print("\n")

    print("Creating Labels.")
    fall_training_labels = np.ones(len(fall_training_data))
    fall_testing_labels = np.ones(len(fall_testing_data))
    non_fall_training_labels = np.zeros(len(non_fall_training_data))
    non_fall_testing_labels = np.zeros(len(non_fall_testing_data))
    print("Created " + str(len(fall_training_labels)) + " fall training labels.")
    print("Created " + str(len(fall_testing_labels)) + " fall testing labels.")
    print("Created " + str(len(non_fall_training_labels)) + " non-fall training labels.")
    print("Created " + str(len(non_fall_testing_labels)) + " non-fall testing labels.")
    print("\n")

    print("Recombining Falls and Non-Falls.")
    training_data = np.concatenate((fall_training_data, non_fall_training_data))
    testing_data = np.concatenate((fall_testing_data, non_fall_testing_data))

    training_labels = np.concatenate((fall_training_labels, non_fall_training_labels))
    testing_labels = np.concatenate((fall_testing_labels, non_fall_testing_labels))
    print("Created " + str(len(training_data)) + " training data of shape " + str(np.shape(training_data)))
    print("Created " + str(len(training_labels)) + " training labels of shape " + str(np.shape(training_labels)))
    print("Created " + str(len(testing_data)) + " testing data of shape " + str(np.shape(testing_data)))
    print("Created " + str(len(testing_labels)) + " testing labels of shape " + str(np.shape(testing_labels)))
    print("\n")

    print("Saving Pickles.")
    save_data_to_path(compiled_data_path, "training_data.pkl", training_data)
    save_data_to_path(compiled_data_path, "training_labels.pkl", training_labels)
    save_data_to_path(compiled_data_path, "testing_data.pkl", testing_data)
    save_data_to_path(compiled_data_path, "testing_labels.pkl", testing_labels)
    print("Done Saving!")


main()
