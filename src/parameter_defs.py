class ProcessingParameters:

    def __init__(self, 
                 range_dft_res=1, 
                 velocity_dft_res=1, 
                 range_window_type='none', 
                 velocity_window_type='none', 
                 range_minimum_m = 0.1, 
                 amplitude_cutoff_factor_max = 1, 
                 amplitude_cutoff_factor_min = 0,
                 time_filter_coefficients=None, 
                 ground_filter_method=None, 
                 ground_filter_params=dict(),
                 range_binning_method=None, 
                 range_binning_params=dict()):
        
        self.range_dft_res = range_dft_res
        self.velocity_dft_res = velocity_dft_res
        self.range_window_type = range_window_type
        self.velocity_window_type = velocity_window_type
        self.range_minimum_m = range_minimum_m
        self.amplitude_cutoff_factor_max = amplitude_cutoff_factor_max
        self.amplitude_cutoff_factor_min = amplitude_cutoff_factor_min
        self.time_filter_coefficients = time_filter_coefficients
        self.ground_filter_method = ground_filter_method
        self.ground_filter_params = ground_filter_params
        self.range_binning_method = range_binning_method
        self.range_binning_params = range_binning_params

class RadarParameters:

    def __init__(self,
                 num_rx_antennas = 3,
                 bandwidth = 1250E6,
                 center_frequency = 59100E6,    
                 frame_repetition_time_s=0.025, 
                 chirp_repetition_time_s=0.17e-3,    
                 num_chirps=128,                           
                 sample_rate_Hz=1e6,               
                 num_samples=128,                                                  
                 tx_power_level=31, 
                 lp_cutoff_Hz=500000,               
                 hp_cutoff_Hz=80000,           
                 if_gain_dB=33):
        
        self.num_rx_antennas = num_rx_antennas
        self.bandwidth = bandwidth
        self.center_frequency = center_frequency
        self.frame_repitition_time_s = frame_repetition_time_s
        self.chirp_repitition_time_s = chirp_repetition_time_s
        self.num_chirps = num_chirps
        self.sample_rate_Hz = sample_rate_Hz
        self.num_samples = num_samples
        self.tx_power_level = tx_power_level
        self.lp_cutoff_Hz = lp_cutoff_Hz
        self.hp_cutoff_Hz = hp_cutoff_Hz
        self.if_gain_dB = if_gain_dB