"""
Hi, I'm Bob, I am a saved version of a specific set of processing parameters.
To make new paramters, save a copy of me and rename me!
To import, use 'from processing_parameters_bob import processing_params'.
"""

from processing_params_def import ProcessingParameters

processing_params = ProcessingParameters(
    range_fft_res=1, 
    velocity_fft_res=1, 
    range_window_type='blackman', 
    velocity_window_type='blackman', 
    range_minimum_m = 0.1, 
    amplitude_cutoff_factor = 0.7, 
    time_filter_coefficients=None, 
    ground_filter_method=None, 
    ground_filter_params=dict(),
    range_binning_method=None, 
    range_binning_params=dict()
)

