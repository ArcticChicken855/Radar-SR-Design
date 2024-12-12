"""
Fill this file with garbage functions and whatever else is needed for testing
Before moving important things to their own files
"""

import pathlib as p
import matplotlib.pyplot as plt


from pickle_utils import *
from data_parsing import *
from spectrogram_stuff import *
from decider import Decider
from processing_parameters_bob import processing_params
from src.data_manipulation import full_process_frames


def build_and_plot_spectrogram(radar_frames, metrics, title=""):
    spectrogram = build_spectrogram_matrix(radar_frames, processing_params, metrics)
    plot_image(spectrogram, title)



def plot_image(image, title=""):
    plt.ioff()
    fig, ax = plt.subplots()
    ax.set_title(title)
    ax.imshow(image, aspect='auto')
    plt.show()


def evaluate_decider(test_data_path):
    correct_decisions = 0
    incorrect_decisions = 0

    data_array = get_all_data_from_path(test_data_path)

    print("Initializing Decider: ")
    decider = Decider()

    print("Decider Initialized. Running Evaluation.")
    for data in data_array:
        if not is_data_valid(data):
            continue

        print("--------------------------------")
        is_fall = is_data_fall(data)

        if is_fall:
            print("Data contains a fall")
        else:
            print("Data contains no fall")

        radar1_frames = get_radar1_frames(data)
        radar2_frames = get_radar2_frames(data)

        radar1_spectrogram = full_process_frames(radar1_frames)
        radar2_spectrogram = full_process_frames(radar2_frames)

        decision = decider.make_decision(radar1_spectrogram, radar2_spectrogram)

        if decision:
            print("Fall Detected!")
        else:
            print("No Fall Detected!")

        if decision == is_fall:
            print("Correct!")
            correct_decisions += 1
        else:
            print("Incorrect!")
            incorrect_decisions += 1

    accuracy = correct_decisions / (correct_decisions + incorrect_decisions)
    print("------------------------------")
    print("Evaluation Complete.")
    print("Correct Decisions: " + str(correct_decisions))
    print("Incorrect Decisions: " + str(incorrect_decisions))
    print("Overall Accuracy: " + str(accuracy) + "%")



fall_data_path = p.Path(__file__).parents[1] / "Fall_Data" / "RawData" / "dec10" / "IQpickles"

evaluate_decider(fall_data_path)



