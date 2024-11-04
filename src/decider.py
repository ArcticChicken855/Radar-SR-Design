import tensorflow as tf
import keras

import pathlib as p
import matplotlib.pyplot as plt

import numpy as np
import skimage as ski


class Decider:
    """
    This class will act as the wrapper for a model and any processing the model needs  to make a decision.
    A single instance of this class should be created and reused to make decisions
    """
    model: keras.Sequential


    previous_time : float

    def __init__(self):
        # i've added a softmax layer to the output of the model to make the results
        # easier to understand
        saved_model_path = p.Path(__file__).parent.parent / "saved_model" / "model.keras"
        loaded_model = keras.models.load_model(saved_model_path)
        self.model = keras.Sequential([loaded_model, keras.layers.Softmax()])
        self.previous_time=0
        self.target_spectogram_size = (128, 128)

    def make_decision(self, radar1_spectrogram, radar2_spectrogram):
        combined = [np.array([radar1_spectrogram]), np.array([radar2_spectrogram])]

        prediction = self.model.predict(combined)[0]



        print(prediction)

        if prediction[0] < prediction[1]:
            return True
        else:
            return False
