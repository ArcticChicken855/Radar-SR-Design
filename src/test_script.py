"""
Fill this file with garbage functions and whatever else is needed for testing
Before moving important things to their own files
"""

import pathlib as p
import matplotlib.pyplot as plt

from pickle_utils import *
from data_parsing import *
from data_manipulation import *
from decider import Decider


def build_and_plot_spectrogram(radar_frames):
    spectrogram = build_spectrogram_matrix(radar_frames)
    plot_image(spectrogram)


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

        decision = decider.make_decision(radar1_frames, radar2_frames)

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


evaluate_decider(p.Path().home() / "RadarData" / "2RadarData" / "IQpickles")
