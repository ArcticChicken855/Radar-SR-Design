import tensorflow as tf
import keras
from keras import layers

import pathlib as p
import matplotlib.pyplot as plt
import numpy as np

from pickle_utils import *


# Currently paths are hardcoded to my (William's) files
# I should probably change this Todo
root_path = p.Path().home() / "RadarData" / "2RadarData"
compiled_data_path = root_path / "CompiledData"

# Todo I don't like having to rely on strings
training_data = get_data_from_path(compiled_data_path / "training_data.pkl")
training_labels = get_data_from_path(compiled_data_path / "training_labels.pkl")

testing_data = get_data_from_path(compiled_data_path / "testing_data.pkl")
testing_labels = get_data_from_path(compiled_data_path / "testing_labels.pkl")

training_dataset = tf.data.Dataset.from_tensor_slices((training_data, training_labels))
testing_dataset = tf.data.Dataset.from_tensor_slices((testing_data, testing_labels))

# Todo what are the best values to use here?
training_dataset = training_dataset.shuffle(50).batch(10)
testing_dataset = testing_dataset.batch(10)

# Todo again, tune this
model = keras.Sequential([
    layers.Input(shape=(128, 128)),
    layers.Conv1D(16, 3, padding='same', activation='relu'),
    layers.MaxPool1D(),
    layers.Conv1D(32, 3, padding='same', activation='relu'),
    layers.MaxPool1D(),
    layers.Conv1D(64, 3, padding='same', activation='relu'),
    layers.MaxPool1D(),
    layers.Flatten(),
    layers.Dense(128, activation='relu'),
    layers.Dense(2)
])

model.compile(optimizer='adam',
              loss=keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])

history = model.fit(
    training_dataset,
    validation_data=testing_dataset,
    epochs=50
)

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']

plt.figure(figsize=(8, 8))
plt.plot(acc, label='Training Accuracy')
plt.plot(val_acc, label='Validation Accuracy')
plt.legend(loc='lower right')
plt.ylabel('Accuracy')
plt.xlabel('Training Epochs')
plt.ylim([min(plt.ylim()), 1])
plt.title('Test me Boy')
plt.xticks(np.arange(0, 20, step=1))
plt.show()
