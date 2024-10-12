from decider import Decider
from ifxradarsdk.fmcw import DeviceFmcw
from ifxradarsdk.fmcw.types import FmcwSimpleSequenceConfig, FmcwSequenceChirp, create_dict_from_sequence
import numpy as np
import time

import radar_parameters_josh as rp # TO CHANGE PARAMS MAKE A COPY OF JOSH AND CHANGE
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

metrics1, sequence1 = rp.set_up_parameters_R1(device1)
metrics2, sequence2 = rp.set_up_parameters_R2(device2)

# define how many frames to use in a ML segment
frames_per_segment = 128 # must be divisible by 4

sequence_info = create_dict_from_sequence(sequence1)[0]['loop']['sub_sequence'][0]['loop']
num_chirps = sequence_info['num_repetitions']
num_samples = sequence_info['sub_sequence'][0]['chirp']['num_samples']
num_rx_antennas = 3

segment_shape = (frames_per_segment, num_rx_antennas, num_chirps, num_samples)

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
        
        decision1 = myDecider.make_decision(segment_R1, plot=True)

        print(f'Radar 1: {decision1}')

        segment_R1[0:(frames_per_segment // 2) - 1] = segment_R1[frames_per_segment // 2 : frames_per_segment - 1]
        R1_idx = (frames_per_segment // 2)

        print(R1_idx)

    if R2_idx == frames_per_segment - 1:
        decision2 = myDecider.make_decision(segment_R2, plot=False)

        print(f'Radar 2: {decision2}')

        segment_R2[0:(frames_per_segment // 2) - 1] = segment_R2[frames_per_segment // 2 : frames_per_segment - 1]
        R2_idx = (frames_per_segment // 2)


    R1_idx += 1
    R2_idx += 1

    


    