import keras
from data_manipulation import full_process_frames


class Decider:
    """
    This class will act as the wrapper for a model and any processing the model needs  to make a decision.
    A single instance of this class should be created and reused to make decisions
    """

    model: keras.Model

    # TODO define __init()__ to include loading and initializing a model to make decisions


    def make_decision(self, radar1_frames, radar2_frames):
        processed_radar1 = full_process_frames(radar1_frames)
        processed_radar2 = full_process_frames(radar2_frames)

        # TODO use model and decision fusion to detect falls
        # model.decide ...
        return True