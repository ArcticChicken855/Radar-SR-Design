from ifxradarsdk.fmcw import DeviceFmcw
from ifxradarsdk.fmcw.types import FmcwSimpleSequenceConfig, FmcwSequenceChirp, create_dict_from_sequence
import numpy as np
import time

from radar_parameter_assigner import assign_radar_parameters
import spectrogram_stuff
import spectogram_plotting
from decider import Decider

from radar_parameters_josh import R1_params, R2_params # TO CHANGE PARAMS MAKE A COPY OF JOSH AND CHANGE
from processing_parameters_bob import processing_params # TO CHANGE PARAMS MAKE A COPY OF BOB AND CHANGE

first_UUID =  "00323253-4335-4851-3036-303439303531"
second_UUID = "00323353-5334-4841-3131-303432303631"
    
device1 = DeviceFmcw(uuid=first_UUID)
device2 = DeviceFmcw(uuid=second_UUID)

# print out this info to make sure the devices are connected
print("UUID of board: " + device1.get_board_uuid())
print("Sensor: " + str(device1.get_sensor_type()))
print("UUID of board: " + device2.get_board_uuid())
print("Sensor: " + str(device2.get_sensor_type()))

# assign the parameters to each device and get the associated metrics
metrics1 = assign_radar_parameters(device1, R1_params)
metrics2 = assign_radar_parameters(device2, R2_params)

# initiate the ML decider class
myDecider = Decider()

# define how many frames to use in a segment
frames_per_segment = 128 # must be divisible by 4

segment_shape = (frames_per_segment, R1_params.num_chirps * processing_params.velocity_dft_res) # assuming that these parameters are the same for R1 and R2

segment_R1 = np.zeros(segment_shape, dtype=float)
segment_R2 = np.zeros(segment_shape, dtype=float)
R1_idx = 0
R2_idx = (frames_per_segment // 4) - 1

# make a function to handle all operations when a segment gets filled up
def full_segment_actions(segment, frames_per_segment, metrics, radar_params, processing_params, plot=False):
    """
    This function defines what happens whenever a sement gets filled.
    First, the sement is subjected to some postprocessing to get the completed spectogram.
    This is then optionally plotted.
    Then, the completed spectogram is passed to the AI.
    Finally, the front half of the segment is sent to the back half, and the segment index is set to the midpoint.
    """
    processed_spectogram = spectrogram_stuff.spectrogram_postprocessing(segment, processing_params)

    if plot == 'static':
        device1.stop_acquisition()
        device2.stop_acquisition()
        spectogram_plotting.plot_spectogram(processed_spectogram, 'Title', radar_params, metrics)
        device1.start_acquisition()
        device2.start_acquisition()
    
    decision = myDecider.make_decision(processed_spectogram)
    print(f'Radar 1: {decision}')

    segment[0:(frames_per_segment // 2) - 1] = segment[frames_per_segment // 2 : frames_per_segment - 1]
    segment_idx = (frames_per_segment // 2) - 1

    return segment, segment_idx

loop_start_time = time.time()
device1.start_acquisition()
device2.start_acquisition()

while True: # main loop
    """
    First, get a frame of data from each radar.
    Immediately process those frames into a slice of the spectogram.
    Each slice gets placed into the segment. Once a segment is full, send it to the AI for classification.
    After that, move the front half of the segment to the back half and keep filling from the middle up.
    """
    # get the next available frames from each radar
    frame1 = device1.get_next_frame()[0]
    frame2 = device2.get_next_frame()[0]

    # immediately do the processing on the acquired frames, giving a single slice of the spectogram
    segment_R1[R1_idx] = spectrogram_stuff.get_spectogram_slice_from_raw(frame1, processing_params, metrics1)
    segment_R2[R2_idx] = spectrogram_stuff.get_spectogram_slice_from_raw(frame2, processing_params, metrics2)


    if R1_idx == frames_per_segment - 1:
        segment_R1, R1_idx = full_segment_actions(segment_R1, frames_per_segment, metrics1, R1_params, processing_params, plot='static')

    if R2_idx == frames_per_segment - 1:
        segment_R2, R2_idx = full_segment_actions(segment_R2, frames_per_segment, metrics2, R2_params, processing_params, plot='static')

    R1_idx += 1
    R2_idx += 1

    

    


    