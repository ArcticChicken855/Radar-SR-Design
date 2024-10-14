
# This program is used for fall data collection. It stores all data in a
# dictionary which also has the recording parameters.

# The program will store the output into a file under the "Fall Data" directory.
# In this directory, it needs a sub-directory. Give the name of the desired
# sub-directory as a system argument when running the program.

# EXECUTION COMMAND:
# py .\src\fall_data_collection_2radar.py <sub-directory name>

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

from radar_parameter_assigner import assign_radar_parameters

from radar_parameters_josh import R1_params, R2_params # TO CHANGE PARAMS MAKE A COPY OF JOSH AND CHANGE

first_UUID =  "00323253-4335-4851-3036-303439303531"
second_UUID = "00323353-5334-4841-3131-303432303631"
    
device1 = DeviceFmcw(uuid=first_UUID)
device2 = DeviceFmcw(uuid=second_UUID)

# print out this info to make sure the devices are connected
print("UUID of board: " + device1.get_board_uuid())
print("Sensor: " + str(device1.get_sensor_type()))
print("UUID of board: " + device2.get_board_uuid())
print("Sensor: " + str(device2.get_sensor_type()))

# assign the specified parameters to each radar, and get the corresponding metrics
metrics1 = assign_radar_parameters(device1, R1_params)
metrics2 = assign_radar_parameters(device2, R2_params)

def make_recording(R1_params, R2_params, metrics1, metrics2):
    """
    This makes a dictionary with the recorded data as well as the necessary info about the radar.
    It stores the dict as a pickle in the file that is specified in the run command.
    """
    project_dir = Path(__file__).parent.parent
    directory = str(project_dir / 'Fall_Data' / sys.argv[1])

    # make a 'Recording' dictionary to store this loop's record
    thisRecording = dict()
    thisRecording['directory'] = directory
    thisRecording['date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

    thisRecording['frames_R1'] = list() # we will append to this list as we gather radar data
    thisRecording['frames_R2'] = list()

    thisRecording['metrics_R1'] = metrics1
    thisRecording['metrics_R2'] = metrics2

    thisRecording['radar_parameters_R1'] = R1_params
    thisRecording['radar_parameters_R2'] = R2_params

    return thisRecording

def make_recording_old(sequence1, sequence2, metrics1, metrics2, frame_rep_time, num_rx_antennas): # OLD FUNCTION, DO NOT USE THIS
    """
    This makes a dictionary with the recorded data as well as the necessary info about the radar.
    It stores the dict as a pickle in the file that is specified in the run command.
    """
    project_dir = Path(__file__).parent.parent
    directory = str(project_dir / 'Fall_Data' / sys.argv[1])

    # make a 'Recording' dictionary to store this loop's record
    thisRecording = dict()
    thisRecording['directory'] = directory
    thisRecording['date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    # change this to a numpy array
    thisRecording['frames_R1'] = list() # we will append to this list as we gather radar data
    thisRecording['frames_R2'] = list()

    # get the configs in a properly formatted way. Store configs in a dict within the larger recording dict
    thisRecording['config1'] = dict()
    thisRecording['config2'] = dict()

    semi_formatted1 = create_dict_from_sequence(sequence1)[0]['loop']['sub_sequence'][0]['loop']
    thisRecording['config1']['num_chirps'] = semi_formatted1['num_repetitions']
    thisRecording['config1']['repetition_time_s'] = semi_formatted1['repetition_time_s']
    thisRecording['config1']['num_rx_antennas'] = num_rx_antennas
    thisRecording['config1']['frame_repetition_time_s'] = frame_rep_time
    thisRecording['config1'].update(semi_formatted1['sub_sequence'][0]['chirp'])

    semi_formatted2 = create_dict_from_sequence(sequence2)[0]['loop']['sub_sequence'][0]['loop']
    thisRecording['config2']['num_chirps'] = semi_formatted2['num_repetitions']
    thisRecording['config2']['repetition_time_s'] = semi_formatted2['repetition_time_s']
    thisRecording['config2']['num_rx_antennas'] = num_rx_antennas
    thisRecording['config2']['frame_repetition_time_s'] = frame_rep_time
    thisRecording['config2'].update(semi_formatted2['sub_sequence'][0]['chirp'])

    # add in metrics to config as a sub-dictionary
    met_vals1 = re.findall(r"\d+\.\d+", str(metrics1)) # godsend from GPT
    thisRecording['config1']['metrics'] = dict()
    thisRecording['config1']['metrics']['range_resolution_m'] = float(met_vals1[0])
    thisRecording['config1']['metrics']['max_range_m'] = float(met_vals1[1])
    thisRecording['config1']['metrics']['max_speed_m_s'] = float(met_vals1[2])
    thisRecording['config1']['metrics']['speed_resolution_m_s'] = float(met_vals1[3])
    thisRecording['config1']['metrics']['center_frequency_Hz'] = float(met_vals1[4])

    met_vals2 = re.findall(r"\d+\.\d+", str(metrics2)) # godsend from GPT
    thisRecording['config2']['metrics'] = dict()
    thisRecording['config2']['metrics']['range_resolution_m'] = float(met_vals2[0])
    thisRecording['config2']['metrics']['max_range_m'] = float(met_vals2[1])
    thisRecording['config2']['metrics']['max_speed_m_s'] = float(met_vals2[2])
    thisRecording['config2']['metrics']['speed_resolution_m_s'] = float(met_vals2[3])
    thisRecording['config2']['metrics']['center_frequency_Hz'] = float(met_vals2[4])

    return thisRecording

# main loop
while True:
    
    Recording = make_recording(R1_params, R2_params, metrics1, metrics2)

    user_control = input('Press enter to start recording, press s to stop recording, press c to end prgm:')
    if (user_control == 'c'):
        break        
    
    # start a timer for the recording duration
    time_record_start = time.time()

    # AQUISITION SEQUENCE
    device1.start_acquisition()
    device2.start_acquisition()
    while not keyboard.is_pressed('s'):
        # the recording has been started. On each loop, collect a single frame of data.
        frame_shell = device1.get_next_frame()
        frame = frame_shell[0]
        Recording['frames_R1'].append(frame) # frames_R1 means that the frames are for the first radar

        frame_shell = device2.get_next_frame()
        frame = frame_shell[0]
        Recording['frames_R2'].append(frame)

    device1.stop_acquisition()
    device2.stop_acquisition()

    Recording['duration'] = time.time() - time_record_start
    Recording['notes'] = input("Enter notes about the recording, or enter skip: ") # add notes here about recording errors, info about recording, etc

    # switch the frame storage from a list to a numpy array for easier and faster use
    num_array = np.array(Recording['frames_R1'])
    Recording['frames_R1'] = num_array

    num_array = np.array(Recording['frames_R2'])
    Recording['frames_R2'] = num_array
    
    
    # pickle the recording dictionary and store it
    pkl_directory = Recording['directory'] + "\\IQ pickles"
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
    pickle.dump(Recording, output_file)