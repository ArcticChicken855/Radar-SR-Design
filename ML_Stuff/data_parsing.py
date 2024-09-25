import pathlib as p
import numpy as np
from data_utils import *


def get_notes(data):
    raw_notes = data['notes']
    notes = raw_notes.split("-")
    return notes


def is_data_fall(data):
    notes = get_notes(data)
    data_type = notes[1]
    if data_type == "w" or data_type == "n":
        return False
    else:
        return True


def is_data_valid(data):
    notes = get_notes(data)
    if len(notes) >= 2:
        return True
    else:
        return False


def get_radar1_frames(data):
    return data['frames_R1']


def get_radar2_frames(data):
    return data['frames_R2']


def get_radar1_config(data):
    return data['config1']


def get_radar2_config(data):
    return data['config2']


def test_is_data_fall(data_array):
    for data in data_array:
        if not is_data_valid(data):
            print("Invalid Data")
        elif is_data_fall(data):
            print("Fall: ")
        else:
            print("No Fall: ")
        print(get_notes(data))
        print("-----------------")
