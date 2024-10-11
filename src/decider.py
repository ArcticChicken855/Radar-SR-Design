import tensorflow as tf
import keras
from data_manipulation import full_process_frames
import pathlib as p
import matplotlib.pyplot as plt

import numpy as np
import time

def plot_image(image, title=""):
    fig, ax = plt.subplots()
    ax.set_title(title)
    ax.imshow(image, aspect='auto')
    plt.show()

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

    def make_decision(self, radar_frames, plot):
        # TODO stupid ugly function
        # changed to only handle one radar at a time


        processed_radar = np.array([full_process_frames(radar_frames)])

        if plot is True:
            plot_image(processed_radar[0])

        self.previous_time = time.time()
        prediction = self.model.predict(processed_radar)[0]

        print(prediction)

        current_time = time.time()
        diff = current_time - self.previous_time
        print("Decider Time: " + str(diff * 1000) + " ms")
        

        if prediction[0] < prediction[1]:
            return True
        else:
            return False
