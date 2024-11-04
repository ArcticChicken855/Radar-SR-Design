"""
Script for loading Raw pickles, categorizing by notes
Creating labels and separating into test/training datasets
And finally saving as 'compiled' pickles for model training
"""

import pathlib as p
import math
import random


from tensorflow.python.keras.backend import dtype
from pickle_utils import *
from data_parsing import *
from data_manipulation import *

# what portion of data should be used in training vs. testing
# ie 0.8 indicates that 80% of data should be used in training
TRAINING_TESTING_RATIO = 0.80

# Currently paths are hardcoded to my (William's) files
# I should probably change this Todo

root_path = p.Path(__file__).parents[1]
raw_data_path = root_path / "Fall_Data" / "RawData"
compiled_data_path = root_path / "Fall_Data" / "CompiledData"



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

    radar1_array = [get_radar1_frames(data) for data in data_array]
    radar2_array = [get_radar2_frames(data) for data in data_array]
    output_array = [radar1_array, radar2_array]

    return output_array



def process_frames(data_array):
    #remember that data array is now (2, radar_frames), meaning that I need to process the second dimension, not the first
    radar1_processed = [full_process_frames(data) for data in data_array[0]]
    radar2_processed = [full_process_frames(data) for data in data_array[1]]

    output_array = [radar1_processed, radar2_processed]
    return output_array


def split_training_vs_testing(data_array):
    # this one is going to be a little more complicated
    data_count = len(data_array[0])
    training_count = math.ceil(data_count * TRAINING_TESTING_RATIO)

    # does this even work??
    # everybody shut your eyes I'm getting freaky
    training_data_array = np.array(data_array)[:,0:training_count]
    testing_data_array = np.array(data_array)[:,training_count:data_count]

    return [training_data_array, testing_data_array]


def main():
    print("Collecting Data.")
    data_array = get_all_data_from_path(raw_data_path / "sep_23")
    data_array += get_all_data_from_path(raw_data_path / "oct_2")
    data_array += get_all_data_from_path(raw_data_path / "oct_3")
    print("Found " + str(len(data_array)) + " recordings.")
    data_array = get_valid_data_only(data_array)
    print("Identified " + str(len(data_array)) + " valid recordings.")

    print("Shuffling Data.")
    random.shuffle(data_array)

    fall_array, non_fall_array = separate_falls(data_array)
    print("Identified " + str(len(fall_array)) + " falls.")
    print("Identified " + str(len(non_fall_array)) + " non-falls.")
    print("\n")

    print("Collecting Radar Frames.")
    fall_radar_data = get_radar_data(fall_array)
    non_fall_radar_data = get_radar_data(non_fall_array)
    print("Collected " + str(len(fall_radar_data[0])) + " falls.")
    print("Collected " + str(len(non_fall_radar_data[0])) + " non-falls.")
    print("\n")



    print("Processing Data.")
    fall_spectrograms_resized = process_frames(fall_radar_data)
    non_fall_spectrograms_resized = process_frames(non_fall_radar_data)
    print("\n")

    print("Splitting into Training and Testing Arrays.")
    fall_training_data, fall_testing_data = split_training_vs_testing(fall_spectrograms_resized)
    non_fall_training_data, non_fall_testing_data = split_training_vs_testing(non_fall_spectrograms_resized)
    print("Collected " + str(len(fall_training_data[0])) + " fall training data.")
    print("Collected " + str(len(fall_testing_data[0])) + " fall testing data.")
    print("Collected " + str(len(non_fall_training_data[0])) + " non-fall training data.")
    print("Collected " + str(len(non_fall_testing_data[0])) + " non-fall testing data.")
    print("\n")

    print("Creating Labels.")

    fall_training_labels = np.ones(len(fall_training_data[0]), dtype=np.int64)
    fall_testing_labels = np.ones(len(fall_testing_data[0]), dtype=np.int64)
    non_fall_training_labels = np.zeros(len(non_fall_training_data[0]), dtype=np.int64)
    non_fall_testing_labels = np.zeros(len(non_fall_testing_data[0]), dtype=np.int64)

    print("Created " + str(len(fall_training_labels)) + " fall training labels.")
    print("Created " + str(len(fall_testing_labels)) + " fall testing labels.")
    print("Created " + str(len(non_fall_training_labels)) + " non-fall training labels.")
    print("Created " + str(len(non_fall_testing_labels)) + " non-fall testing labels.")
    print("\n")

    print("Recombining Falls and Non-Falls.")
    training_data0 = np.concatenate((fall_training_data[0], non_fall_training_data[0]))
    training_data1 = np.concatenate((fall_training_data[1], non_fall_training_data[1]))
    training_data = [training_data0, training_data1]

    testing_data0 = np.concatenate((fall_testing_data[0], non_fall_testing_data[0]))
    testing_data1 = np.concatenate((fall_testing_data[1], non_fall_testing_data[1]))
    testing_data = [testing_data0, testing_data1]

    training_labels = np.concatenate((fall_training_labels, non_fall_training_labels))
    testing_labels = np.concatenate((fall_testing_labels, non_fall_testing_labels))
    print("Created " + str(len(training_data[0])) + " training data of shape " + str(np.shape(training_data)))
    print("Created " + str(len(training_labels)) + " training labels of shape " + str(np.shape(training_labels)))
    print("Created " + str(len(testing_data[0])) + " testing data of shape " + str(np.shape(testing_data)))
    print("Created " + str(len(testing_labels)) + " testing labels of shape " + str(np.shape(testing_labels)))
    print("\n")

    print("Saving Pickles.")
    save_data_to_path(compiled_data_path, "training_data.pkl", training_data)
    save_data_to_path(compiled_data_path, "training_labels.pkl", training_labels)
    save_data_to_path(compiled_data_path, "testing_data.pkl", testing_data)
    save_data_to_path(compiled_data_path, "testing_labels.pkl", testing_labels)
    print("Done Saving!")


main()
