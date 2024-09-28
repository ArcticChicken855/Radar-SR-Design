import tensorflow as tf
import keras
from data_manipulation import full_process_frames
import pathlib as p

import numpy as np


class Decider:
    """
    This class will act as the wrapper for a model and any processing the model needs  to make a decision.
    A single instance of this class should be created and reused to make decisions
    """
    model: keras.Sequential

    def __init__(self):
        # i've added a softmax layer to the output of the model to make the results
        # easier to understand
        saved_model_path = p.Path().cwd().parents[1] / "saved_model" / "model.keras"
        loaded_model = keras.models.load_model(saved_model_path)
        self.model = keras.Sequential([loaded_model, keras.layers.Softmax()])

    def make_decision(self, radar_frames):
        # TODO stupid ugly function
        # changed to only handle one radar at a time
        processed_radar = np.array([full_process_frames(radar_frames)])

        prediction = self.model.predict(processed_radar)[0]

        print(prediction)

        if prediction[0] < prediction[1]:
            return True
        else:
            return False
