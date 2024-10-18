"""
File containing a method to create the ML model
"""

import keras
from keras import layers



def create_model(normalization_layer):

    """
    Build and compile the ML model
    Input Shape: (128, 128)
    Output Shape: (2)
    """

    model = keras.Sequential([
        layers.Input(shape=(128, 128)),

        normalization_layer,

        layers.Conv1D(16, 3, padding='same', activation='relu'),
        layers.MaxPool1D(),
        layers.Conv1D(32, 3, padding='same', activation='relu'),
        layers.MaxPool1D(),
        layers.Conv1D(64, 3, padding='same', activation='relu'),
        layers.MaxPool1D(),
        layers.Flatten(),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(2)
    ])

    model.compile(optimizer='adam',
                  loss=keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                  metrics=['accuracy'])

    return model
