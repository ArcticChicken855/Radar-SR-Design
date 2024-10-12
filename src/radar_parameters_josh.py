"""
This is just a file to store the radar parameters. 
The parameters of the first and second radar are stored inependently.
To change the parameters, make a copy of this file and give it a nickname.
To use the radar params, do 'import radar_parameters_josh as rp'.
To use the functions, just pass in the device, and it will set the parameters. It returns the sequence and the metrics associated with the parameters.
"""

from ifxradarsdk.fmcw import DeviceFmcw
from ifxradarsdk.fmcw.types import FmcwSimpleSequenceConfig, FmcwSequenceChirp

def set_up_parameters_R1(device):

    num_rx_antennas = 3
    bandwidth = 1250E6
    center_frequency = 59100E6
    start_freq = center_frequency - bandwidth//2
    end_freq = center_frequency + bandwidth//2

    radar_config = FmcwSimpleSequenceConfig(
        frame_repetition_time_s=0.025, 
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

def set_up_parameters_R2(device):

    num_rx_antennas = 3
    bandwidth = 1250E6
    center_frequency = 60350E6
    start_freq = center_frequency - bandwidth//2
    end_freq = center_frequency + bandwidth//2

    radar_config = FmcwSimpleSequenceConfig(
        frame_repetition_time_s=0.025, 
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