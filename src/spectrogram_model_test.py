
import numpy as np

import tensorflow as tf
import keras
from keras import layers

import pathlib as p
import matplotlib.pyplot as plt


from pickle_utils import *
from model_structure import create_model


#region loading data
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
#endregion

#region weights and normalize
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
normalization.adapt(training_data[0] + training_data[1])
#endregion


#region model and first training
def make_separate_model_part():

    separate_layers = keras.Sequential([
        layers.Input(shape=(128, 128)),

        normalization,

        layers.Conv1D(16, 3, padding='same', activation='relu'),
        layers.MaxPool1D(),
        layers.Conv1D(32, 3, padding='same', activation='relu'),
        layers.MaxPool1D(),
        layers.Conv1D(64, 3, padding='same', activation='relu'),
        layers.MaxPool1D(),
        layers.Flatten()
    ])

    return separate_layers

radar1_input = layers.Input(shape=(128,128),name="radar1")
radar2_input = layers.Input(shape=(128,128),name="radar2")

radar1_model = make_separate_model_part()
radar2_model = make_separate_model_part()

y1 = radar1_model(radar1_input)
y2 = radar2_model(radar2_input)

concatenate = layers.concatenate([y1, y2])
dense1 = layers.Dense(128, activation='relu')(concatenate)
drop1 = layers.Dropout(0.5)(dense1)
dense2 = layers.Dense(2)(drop1)
output = layers.Softmax(name="output")(dense2)

model = keras.Model(
    inputs=[radar1_input, radar2_input],
    outputs=output
)

keras.utils.plot_model(model)

model.compile(optimizer='adam',
              loss=keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])

history = model.fit(
    # oddly I think I have to do this to make it a 'list of arrays' rather than a array of arrays
    x=[training_data[0], training_data[1]],
    y=training_labels,
    validation_data=([testing_data[0], testing_data[1]], testing_labels),
    epochs=100,
    batch_size=10,
    shuffle=True,
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
#endregion



model.save(SAVED_MODEL_PATH)
