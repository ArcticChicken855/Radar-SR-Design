from ifxradarsdk.fmcw import DeviceFmcw
from ifxradarsdk.fmcw.types import FmcwSimpleSequenceConfig, FmcwSequenceChirp, create_dict_from_sequence
import numpy as np
import time

from scipy.signal import spectrogram

from radar_parameter_assigner import assign_radar_parameters
import spectrogram_stuff
import spectogram_plotting
from decider import Decider
from data_manipulation import full_process_frames

from radar_parameters_oldie import R1_params, R2_params # TO CHANGE PARAMS MAKE A COPY OF JOSH AND CHANGE
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
frames_per_segment = 32 # must be divisible by 4

segment_shape = (frames_per_segment, R1_params.num_rx_antennas, R1_params.num_chirps, R1_params.num_samples) # assuming that these parameters are the same for R1 and R2

segment_R1 = np.zeros(segment_shape, dtype=complex)
segment_R2 = np.zeros(segment_shape, dtype=complex)
R1_idx = 0
R2_idx = 0

# make a function to handle all operations when a segment gets filled up
def full_segment_actions(segment1, segment2, frames_per_segment, metrics, radar_params, processing_params, plot=False):
    """
    This function defines what happens whenever a sement gets filled.
    First, the sement is subjected to some postprocessing to get the completed spectogram.
    This is then optionally plotted.
    Then, the completed spectogram is passed to the AI.
    Finally, the front half of the segment is sent to the back half, and the segment index is set to the midpoint.
    """
    processed_spectogram1 = full_process_frames(segment1)
    processed_spectogram2 = full_process_frames(segment2)
    
    decision = myDecider.make_decision(processed_spectogram1, processed_spectogram2)

    if decision:
        print("Fall Detected!!")
        device1.stop_acquisition()
        device2.stop_acquisition()
        spectogram_plotting.plot_spectogram(processed_spectogram1, "radar1", radar_params, metrics)
        spectogram_plotting.plot_spectogram(processed_spectogram2, "radar2", radar_params, metrics)
        device1.start_acquisition()
        device2.start_acquisition()

    segment1[0:(frames_per_segment // 2)] = segment1[frames_per_segment // 2 : frames_per_segment]
    segment2[0:(frames_per_segment // 2)] = segment2[frames_per_segment // 2: frames_per_segment]
    segment_idx = (frames_per_segment // 2) - 1

    return segment1, segment2, segment_idx

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
    segment_R1[R1_idx] = frame1
    segment_R2[R2_idx] = frame2

    if R1_idx == frames_per_segment - 1:
        segment_R1, segment_R2, idx = full_segment_actions(segment_R1, segment_R2, frames_per_segment, metrics1, R1_params, processing_params)
        R1_idx = idx
        R2_idx = idx


    R1_idx += 1
    R2_idx += 1

    

    


    