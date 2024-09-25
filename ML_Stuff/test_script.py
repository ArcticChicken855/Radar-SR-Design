import pathlib as p
import matplotlib.pyplot as plt
from data_utils import *
from data_parsing import *
from spectrogram_stuff import *

datapath = p.Path().home() / "RadarData" / "2RadarData" / "IQpickles"
data_array = get_all_data_from_path(datapath)
test_data = data_array[10]

radar1_frames = get_radar1_frames(test_data)
radar2_frames = get_radar2_frames(test_data)

radar1_spectrogram = build_spectrogram_matrix(radar1_frames)
radar2_spectrogram = build_spectrogram_matrix(radar2_frames)

plt.ioff()

fig, ax = plt.subplots()
ax.imshow(radar1_spectrogram, aspect='auto')
plt.show()


