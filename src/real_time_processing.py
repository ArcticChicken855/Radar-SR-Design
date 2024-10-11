from decider import Decider
from ifxradarsdk.fmcw import DeviceFmcw
from ifxradarsdk.fmcw.types import FmcwSimpleSequenceConfig, FmcwSequenceChirp, create_dict_from_sequence
import numpy as np

first_UUID =  "00323253-4335-4851-3036-303439303531"
second_UUID = "00323353-5334-4841-3131-303432303631"
    
device1 = DeviceFmcw(uuid=first_UUID)
device2 = DeviceFmcw(uuid=second_UUID)

# print out this info to make sure the devices are connected
print("UUID of board: " + device1.get_board_uuid())
print("Sensor: " + str(device1.get_sensor_type()))
print("UUID of board: " + device2.get_board_uuid())
print("Sensor: " + str(device2.get_sensor_type()))

frame_rep_time = 0.1
num_rx_antennas = num_rx_antennas = device1.get_sensor_information()["num_rx_antennas"]

def set_up_radar_parameters(device, frame_rep_time, num_rx_antennas, center_frequency, bandwidth):
    """
    This function simply sets up the radar device with the necessary parameters,
    and also returns the metrics of the radar for the given params.
    """
    start_freq = center_frequency - bandwidth//2
    end_freq = center_frequency + bandwidth//2

    radar_config = FmcwSimpleSequenceConfig(
        frame_repetition_time_s=frame_rep_time, 
        chirp_repetition_time_s=0.17e-3,    
        num_chirps=128,                          
        tdm_mimo=False,                      
        chirp=FmcwSequenceChirp(
            start_frequency_Hz=start_freq,
            end_frequency_Hz=end_freq,  
            sample_rate_Hz=1e6, # max                
            num_samples=128,               
            rx_mask=(1 << num_rx_antennas) - 1,                    
            tx_mask=1,               
            tx_power_level=31, # max  
            lp_cutoff_Hz=500000,               
            hp_cutoff_Hz=80000,           
            if_gain_dB=33,                      
        )
    )

    # give the parameters to the device
    sequence = device.create_simple_sequence(radar_config)
    device.set_acquisition_sequence(sequence)    

    # find the metrics from the params
    metrics = device.metrics_from_sequence(sequence.loop.sub_sequence.contents)

    return metrics, sequence

bandwidth = 1250E6
fc1 = 59100E6
fc2 = 60350E6

metrics1, sequence1 = set_up_radar_parameters(device1, frame_rep_time, num_rx_antennas, fc1, bandwidth)
metrics2, sequence2 = set_up_radar_parameters(device2, frame_rep_time, num_rx_antennas, fc2, bandwidth)

# define how many frames to use in a segment
frames_per_segment = 12 # must be divisible by 4

semi_formatted = create_dict_from_sequence(sequence1)[0]['loop']['sub_sequence'][0]['loop']
segment_shape = (frames_per_segment, num_rx_antennas, semi_formatted['num_repetitions'], semi_formatted['sub_sequence'][0]['chirp']['num_samples'])

segment_R1 = np.zeros(segment_shape, dtype=complex)
segment_R2 = np.zeros(segment_shape, dtype = complex)
R1_idx = 0
R2_idx = (frames_per_segment // 4) - 1

myDecider = Decider()

while True: # main loop
    """
    First, get a frame of data from each radar. Insert the frame into the corresponding segment at the index.
    Then, once a segment is full, send the whole segment to the decider function.
    After that, move the front half of the segment to the back half and keep filling from the middle up.
    """
    segment_R1[R1_idx] = device1.get_next_frame()[0]
    segment_R2[R2_idx] = device2.get_next_frame()[0]

    if R1_idx == frames_per_segment - 1:
        decision1 = myDecider.make_decision(segment_R1)

        print(f'Radar 1: {decision1}')

        segment_R1[0:(frames_per_segment // 2) - 1] = segment_R1[(frames_per_segment // 2) - 1 : frames_per_segment - 1]
        R1_idx = (frames_per_segment // 2) - 1 

    

    


    