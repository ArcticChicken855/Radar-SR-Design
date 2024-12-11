
import numpy as np

import tensorflow as tf
import keras
from keras import layers

import pathlib as p
import matplotlib.pyplot as plt


from pickle_utils import *



#region loading data

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

#endregion


#region model and first training
def make_separate_model_part():

    separate_layers = keras.Sequential([
        layers.Input(shape=(128, 160)),
        layers.Conv1D(16, 3, padding='same', activation='relu'),
        layers.MaxPool1D(),
        layers.Conv1D(32, 3, padding='same', activation='relu'),
        layers.MaxPool1D(),
        layers.Conv1D(64, 3, padding='same', activation='relu'),
        layers.MaxPool1D(),
        layers.Flatten()
    ])

    return separate_layers

radar1_input = layers.Input(shape=(128,160),name="radar1")
radar2_input = layers.Input(shape=(128,160),name="radar2")

normalization1 = layers.Normalization(axis=None, name="normalization1")
normalization1.adapt(training_data[0])

normalization2 = layers.Normalization(axis=None, name="normalization2")
normalization2.adapt(training_data[1])

n1 = normalization1(radar1_input)
n2 = normalization2(radar2_input)

radar1_model = make_separate_model_part()
radar2_model = make_separate_model_part()

y1 = radar1_model(n1)
y2 = radar2_model(n2)

concatenate = layers.concatenate([y1, y2])
dense1 = layers.Dense(128, activation='relu')(concatenate)
drop1 = layers.Dropout(0.5)(dense1)
dense2 = layers.Dense(32)(drop1)
drop2 = layers.Dropout(0.5)(dense2)
dense3 = layers.Dense(2)(drop2)

output = layers.Softmax(name="output")(dense3)

model = keras.Model(
    inputs=[radar1_input, radar2_input],
    outputs=output
)

#keras.utils.plot_model(model)

# now, I'm going to try freezing the layers
for layer in model.layers[7:]:
    layer.trainable = False


model.compile(optimizer='adam',
              loss=keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])

history = model.fit(
    # oddly I think I have to do this to make it a 'list of arrays' rather than an array of arrays
    x=[training_data[0], training_data[1]],
    y=training_labels,
    validation_data=([testing_data[0], testing_data[1]], testing_labels),
    epochs=50,
    batch_size=10,
    shuffle=True,
    class_weight=class_weight
)

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']


# unfreeze those layers
for layer in model.layers[7:]:
    layer.trainable = True

# recompile
model.compile(optimizer='adam',
              loss=keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])

# and continue training
history = model.fit(
    # oddly I think I have to do this to make it a 'list of arrays' rather than an array of arrays
    x=[training_data[0], training_data[1]],
    y=training_labels,
    validation_data=([testing_data[0], testing_data[1]], testing_labels),
    epochs=30,
    batch_size=10,
    shuffle=True,
    class_weight=class_weight
)

acc += history.history['accuracy']
val_acc += history.history['val_accuracy']

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
