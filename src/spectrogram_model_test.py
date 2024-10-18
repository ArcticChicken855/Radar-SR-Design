import numpy as np
import tensorflow as tf
import keras
from keras import layers

import pathlib as p
import matplotlib.pyplot as plt

from pickle_utils import *
from model_structure import create_model


# Currently paths are hardcoded to my (William's) files
# I should probably change this Todo
root_path = p.Path(__file__).parents[1] / "Fall_Data"
compiled_data_path = root_path / "CompiledData"

SAVED_MODEL_PATH = p.Path(__file__).parents[1] / "saved_model" / "model.keras"

# Todo I don't like having to rely on strings
training_data = get_data_from_path(compiled_data_path / "training_data.pkl")
training_labels = get_data_from_path(compiled_data_path / "training_labels.pkl")

testing_data = get_data_from_path(compiled_data_path / "testing_data.pkl")
testing_labels = get_data_from_path(compiled_data_path / "testing_labels.pkl")

training_dataset = tf.data.Dataset.from_tensor_slices((training_data, training_labels))
testing_dataset = tf.data.Dataset.from_tensor_slices((testing_data, testing_labels))

# Trying something to fix the imbalanced classes
# basically there is too many non-falls, which is screwing with the output predictions
# That didn't help, agh

neg, pos = np.bincount(training_labels)
total = neg + pos
weight_0 = (1 / neg) * (total / 2.0)
weight_1 = (1 / pos) * (total / 2.0)
class_weight = {0: weight_0, 1: weight_1}

# next idea, normalize data
normalization = layers.Normalization(axis=None)
normalization.adapt(training_data)

# Todo what are the best values to use here?
training_dataset = training_dataset.shuffle(50).batch(10)
testing_dataset = testing_dataset.batch(10)

# Todo again, tune this
model = create_model(normalization)

history = model.fit(
    training_dataset,
    validation_data=testing_dataset,
    epochs=100,
    class_weight=class_weight
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


model.save(SAVED_MODEL_PATH)
