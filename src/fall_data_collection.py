
# This program is used for fall data collection. It stores all data in a
# dictionary which also has the recording parameters.

# The program will store the output into a file under the "Fall Data" directory.
# In this directory, it needs a sub-directory. Give the name of the desired
# sub-directory as a system argument when running the program.

# EXECUTION COMMAND:
# py .\src\fall_data_collection.py <sub-directory name>

from ifxradarsdk import get_version_full
from ifxradarsdk.fmcw import DeviceFmcw
from ifxradarsdk.fmcw.types import FmcwSimpleSequenceConfig, FmcwSequenceChirp, create_dict_from_sequence
import numpy as np
import keyboard
import time
import pickle
import os
import re
import sys
from pathlib import Path
    
with DeviceFmcw() as device:
    # print some basic info
    print("Radar SDK Version: " + get_version_full())
    print("UUID of board: " + device.get_board_uuid())
    print("Sensor: " + str(device.get_sensor_type()))

    # set up the radar configs
    # use all available antennas
    num_rx_antennas = device.get_sensor_information()["num_rx_antennas"]

    frame_rep_time = 0.1

    radar_config = FmcwSimpleSequenceConfig(
        frame_repetition_time_s=frame_rep_time, 
        chirp_repetition_time_s=0.17e-3,    
        num_chirps=128,                          
        tdm_mimo=False,                      
        chirp=FmcwSequenceChirp(
            start_frequency_Hz=59_100_000_000,
            end_frequency_Hz=60_350_000_000,  
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
                
    # get the directory for outputting the data
    project_dir = Path(__file__).parent.parent
    directory = str(project_dir / 'Fall_Data' / sys.argv[1])

    # main loop
    while True:

        user_control = input('Press enter to start recording, press s to stop recording, press c to end prgm:')
        if (user_control == 'c'):
            break        
        
        # make a 'Recording' dictionary to store this loop's record
        thisRecording = dict()
        thisRecording['directory'] = directory
        thisRecording['date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        # dchange this to a numpy array
        thisRecording['frames_R1'] = list() # we will append to this list as we gather radar data

        # get the configs in a properly formatted way. Store configs in a dict within the larger recording dict
        thisRecording['config'] = dict()

        semi_formatted = create_dict_from_sequence(sequence)[0]['loop']['sub_sequence'][0]['loop']

        thisRecording['config']['num_chirps'] = semi_formatted['num_repetitions']
        thisRecording['config']['repetition_time_s'] = semi_formatted['repetition_time_s']
        thisRecording['config']['num_rx_antennas'] = num_rx_antennas
        thisRecording['config']['frame_repetition_time_s'] = frame_rep_time
        thisRecording['config'].update(semi_formatted['sub_sequence'][0]['chirp'])

        # add in metrics to config as a sub-dictionary
        met_vals = re.findall(r"\d+\.\d+", str(metrics)) # godsend from GPT
        thisRecording['config']['metrics'] = dict()
        thisRecording['config']['metrics']['range_resolution_m'] = float(met_vals[0])
        thisRecording['config']['metrics']['max_range_m'] = float(met_vals[1])
        thisRecording['config']['metrics']['max_speed_m_s'] = float(met_vals[2])
        thisRecording['config']['metrics']['speed_resolution_m_s'] = float(met_vals[3])
        thisRecording['config']['metrics']['center_frequency_Hz'] = float(met_vals[4])

        # start a timer for the recording duration
        time_record_start = time.time()

        # AQUISITION SEQUENCE
        device.start_acquisition()
        while not keyboard.is_pressed('s'):
            # the recording has been started. On each loop, collect a single frame of data.
            frame_shell = device.get_next_frame()
            frame = frame_shell[0]
            thisRecording['frames_R1'].append(frame) # frames_R1 means that the frames are for the first radar

        device.stop_acquisition()

        thisRecording['duration'] = time.time() - time_record_start
        thisRecording['notes'] = input("Enter notes about the recording, or enter skip: ") # add notes here about recording errors, info about recording, etc

        # switch the frame storage from a list to a numpy array for easier and faster use
        num_array = np.array(thisRecording['frames_R1'])
        thisRecording['frames_R1'] = num_array
        
        
        # pickle the recording dictionary and store it
        pkl_directory = thisRecording['directory'] + "\\IQ pickles"
        #check if the "IQ pickle" folder exists, if not, create it
        if not os.path.exists(pkl_directory):
            os.mkdir(pkl_directory)
        # go to the folder and find what file number to create by looping over each number until a file is found
        i=0
        output_file = False
        while output_file is False:
            if not os.path.isfile(pkl_directory + "\\IQpickle_" + str(i) + ".pkl"):
                output_file = open(pkl_directory + "\\IQpickle_" + str(i) + ".pkl", "wb")
            else:
                i += 1
        # write to the file 
        pickle.dump(thisRecording, output_file)