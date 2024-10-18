from ifxradarsdk.fmcw import DeviceFmcw
from ifxradarsdk.fmcw.types import FmcwSimpleSequenceConfig, FmcwSequenceChirp
import re

def assign_radar_parameters(device, radar_params):
    """
    This function uses the RadarParameters class to assign specific parameters to a device.
    It also returns the device metrics as a dictionary.
    """

    start_freq = radar_params.center_frequency - radar_params.bandwidth//2
    end_freq = radar_params.center_frequency + radar_params.bandwidth//2

    radar_config = FmcwSimpleSequenceConfig(
        frame_repetition_time_s=radar_params.frame_repitition_time_s,
        chirp_repetition_time_s=radar_params.chirp_repitition_time_s,    
        num_chirps=radar_params.num_chirps,                          
        tdm_mimo=False,                      
        chirp=FmcwSequenceChirp(
            start_frequency_Hz=start_freq,
            end_frequency_Hz=end_freq,  
            sample_rate_Hz=radar_params.sample_rate_Hz,              
            num_samples=radar_params.num_samples,               
            rx_mask=(1 << radar_params.num_rx_antennas) - 1,                    
            tx_mask=1,               
            tx_power_level=radar_params.tx_power_level,
            lp_cutoff_Hz=radar_params.lp_cutoff_Hz,               
            hp_cutoff_Hz=radar_params.hp_cutoff_Hz,           
            if_gain_dB=radar_params.if_gain_dB,                      
        )
    )

    # give the parameters to the device
    sequence = device.create_simple_sequence(radar_config)
    device.set_acquisition_sequence(sequence)    

    # find the metrics from the params
    unformatted_metrics = device.metrics_from_sequence(sequence.loop.sub_sequence.contents)

    # add in metrics to dictionary
    metrics = dict()
    met_vals1 = re.findall(r"\d+\.\d+", str(unformatted_metrics))
    metrics['range_resolution_m'] = float(met_vals1[0])
    metrics['max_range_m'] = float(met_vals1[1])
    metrics['max_speed_m_s'] = float(met_vals1[2])
    metrics['speed_resolution_m_s'] = float(met_vals1[3])
    metrics['center_frequency_Hz'] = float(met_vals1[4])

    return metrics