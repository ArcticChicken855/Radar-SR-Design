import tensorflow as tf
import keras
from src.data_processing.data_manipulation import full_process_frames
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

    def make_decision(self, radar1_frames, radar2_frames):
        # TODO stupid ugly function
        processed_radar1 = np.array([full_process_frames(radar1_frames)])
        processed_radar2 = np.array([full_process_frames(radar2_frames)])

        prediction1 = self.model.predict(processed_radar1)[0]
        prediction2 = self.model.predict(processed_radar2)[0]

        print(prediction1)
        print(prediction2)

        if prediction1[0] < prediction1[1] or prediction2[0] < prediction2[1]:
            return True
        else:
            return False
