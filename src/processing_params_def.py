class ProcessingParameters:

    def __init__(self, 
                 range_fft_res=1, 
                 velocity_fft_res=1, 
                 range_window_type='none', 
                 velocity_window_type='none', 
                 range_minimum_m = 0.1, 
                 amplitude_cutoff_factor = 1, 
                 time_filter_coefficients=None, 
                 ground_filter_method=None, 
                 ground_filter_params=dict(),
                 range_binning_method=None, 
                 range_binning_params=dict()):
        
        self.range_fft_res = range_fft_res
        self.velocity_fft_res = velocity_fft_res
        self.range_window_type = range_window_type
        self.velocity_window_type = velocity_window_type
        self.range_minimum_m = range_minimum_m
        self.amplitude_cutoff_factor = amplitude_cutoff_factor
        self.time_filter_coefficients = time_filter_coefficients
        self.ground_filter_method = ground_filter_method
        self.ground_filter_params = ground_filter_params
        self.range_binning_method = range_binning_method
        self.range_binning_params = range_binning_params