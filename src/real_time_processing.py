from decider import Decider
from ifxradarsdk.fmcw import DeviceFmcw
from ifxradarsdk.fmcw.types import FmcwSimpleSequenceConfig, FmcwSequenceChirp, create_dict_from_sequence
import numpy as np
import time

from radar_parameter_assigner import assign_radar_parameters

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

# define how many frames to use in a ML segment
frames_per_segment = 128 # must be divisible by 4

segment_shape = (frames_per_segment, R1_params.num_rx_antennas, R1_params.num_chirps, R1_params.num_samples) # assuming that these parameters are the same for R1 and R2

segment_R1 = np.zeros(segment_shape, dtype=complex)
segment_R2 = np.zeros(segment_shape, dtype = complex)
R1_idx = 0
R2_idx = (frames_per_segment // 4) - 1

myDecider = Decider()

loop_start_time = time.time()
device1.start_acquisition()
device2.start_acquisition()

while True: # main loop

    """
    First, get a frame of data from each radar. Insert the frame into the corresponding segment at the index.
    Then, once a segment is full, send the whole segment to the decider function.
    After that, move the front half of the segment to the back half and keep filling from the middle up.
    """
    device1.start_acquisition()
    device2.start_acquisition()

    segment_R1[R1_idx] = device1.get_next_frame()[0]
    segment_R2[R2_idx] = device2.get_next_frame()[0]

    if R1_idx == frames_per_segment - 1:
        
        device1.stop_acquisition()
        device2.stop_acquisition()

        decision1 = myDecider.make_decision(segment_R1, plot=False)

        print(f'Radar 1: {decision1}')

        segment_R1[0:(frames_per_segment // 2) - 1] = segment_R1[frames_per_segment // 2 : frames_per_segment - 1]
        R1_idx = (frames_per_segment // 2)

        print(R1_idx)
        device1.start_acquisition()
        device2.start_acquisition()

    if R2_idx == frames_per_segment - 1:
        decision2 = myDecider.make_decision(segment_R2, plot=False)

        print(f'Radar 2: {decision2}')

        segment_R2[0:(frames_per_segment // 2) - 1] = segment_R2[frames_per_segment // 2 : frames_per_segment - 1]
        R2_idx = (frames_per_segment // 2)


    R1_idx += 1
    R2_idx += 1

    


    