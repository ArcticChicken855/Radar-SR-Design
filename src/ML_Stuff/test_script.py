"""
Fill this file with garbage functions and whatever else is needed for testing
Before moving important things to their own files
"""

import pathlib as p
import matplotlib.pyplot as plt
from decider import Decider

from pickle_utils import *
from data_parsing import *
from spectrogram_stuff import *
from data_manipulation import *


def build_and_plot_spectrogram(radar_frames):
    spectrogram = build_spectrogram_matrix(radar_frames)
    plot_image(spectrogram)


def plot_image(image, title=""):
    plt.ioff()
    fig, ax = plt.subplots()
    ax.set_title(title)
    ax.imshow(image, aspect='auto')
    plt.show()


datapath = p.Path().home() / "RadarData" / "2RadarData" / "IQpickles"
data_array = get_all_data_from_path(datapath)
test_data = data_array[10]

radar1_frames = get_radar1_frames(test_data)
spectrogram = build_spectrogram_matrix(radar1_frames)
resized = resize_spectrogram(spectrogram)

plot_image(resized)

