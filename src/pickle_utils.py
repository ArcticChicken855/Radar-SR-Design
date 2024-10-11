"""
Functions to load and save pickles
Use this rather than interacting manually to avoid mistakes
And just to make things easier
"""

import pickle

# A lot of what im saving and loading is numpy arrays
# Even though this file does not use numpy,
# it seems to need the import so that numpy arrays can be properly saved and loaded
import numpy as np


def get_data_from_path(path):
    pkl = open(path, 'rb')
    data = pickle.load(pkl)
    pkl.close()
    return data


def get_all_data_from_path(path):
    data_array = []
    for file_path in path.glob("*"):
        data = get_data_from_path(file_path)
        data_array.append(data)
    return data_array


def save_data_to_path(path, file_name, data):
    with open(path / file_name, 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
