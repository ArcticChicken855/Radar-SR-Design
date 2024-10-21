"""
Functions for computing the spectrogram from raw radar frames.
Primarily use build_spectrogram_matrix

Functions by Nathan
Stripped Down and Repurposed by William
"""

import numpy as np

import scipy.ndimage

def compute_range_dft(frames, range_axis=3, dft_resolution_factor=1, window_type='none', positive_frequencies_only=True):
    # get a few bits of information to make it easier
    samples_per_chirp = np.shape(frames)[range_axis]


    # use the resolution factor to find the length of the DFT
    dft_length = dft_resolution_factor * samples_per_chirp

    # if there is a window, multiply the window with the tensor along each chirp
    # start by getting the 1d array window
    if window_type != 'none':
        if window_type == 'blackman':
            window = np.blackman(samples_per_chirp)
        elif window_type == 'hamming':
            window = np.hamming(samples_per_chirp)
        elif window_type == 'hanning':
            window = np.hanning(samples_per_chirp)
        elif window_type == 'bartlett':
            window = np.bartlett(samples_per_chirp)

        # shape the window into the same form as the input matrix
        # Todo: what is happening here?

        if range_axis == 3:
            shaped_window = window[None, None, None, :]
        elif range_axis == 2:
            shaped_window = window[None, None, :]
        elif range_axis == 1:
            shaped_window = window[None, :]


        # get the product
        product = frames * shaped_window

    elif window_type == 'none':
        product = frames

    # main DFT computation
    output_array = np.fft.fft(product, n=dft_length, axis=range_axis)

    # if requested, only return the positive frequencies of the DFT
    if positive_frequencies_only:
        if range_axis == 3:
            output_array = output_array[:, :, :, 0:int(dft_length / 2)]
        elif range_axis == 2:
            output_array = output_array[:, :, 0:int(dft_length / 2)]

    # now return the stuff
    return output_array

def compute_doppler_dft(range_chirp_tensor, velocity_axis=2, dft_resolution_factor=1, window_type='none', fftshift=True):
    # get a few bits of information to make it easier
    chirps_per_frame = np.shape(range_chirp_tensor)[velocity_axis]


    # use the resolution factor to find the length of the DFT
    doppler_dft_length = dft_resolution_factor * chirps_per_frame

    # compute the DFT with the window function if specified
    if window_type != 'none':
        if window_type == 'blackman':
            window = np.blackman(chirps_per_frame)
        elif window_type == 'hamming':
            window = np.hamming(chirps_per_frame)
        elif window_type == 'hanning':
            window = np.hanning(chirps_per_frame)
        elif window_type == 'bartlett':
            window = np.bartlett(chirps_per_frame)

        # shape the window into the same form as the input matrix

        if velocity_axis == 2:
            shaped_window = window[None, None, :, None]
        elif velocity_axis == 1:
            shaped_window = window[None, :, None]
        elif velocity_axis == 0:
            shaped_window = window[:, None]


        # get the product
        product = range_chirp_tensor * shaped_window

    elif window_type == 'none':
        product = range_chirp_tensor

    # main DFT computation
    if fftshift is True:

        output_array = np.fft.fftshift(np.fft.fft(product, n=doppler_dft_length, axis=velocity_axis), axes=velocity_axis)
    else:
        output_array = np.fft.fft(product, n=doppler_dft_length, axis=velocity_axis)


    # now return the shit
    return output_array


def butterworth_ground_filter():
    pass
    
def range_binning():
    pass

def get_spectogram_slice_from_raw(raw_frame, processing_params, metrics):
    """
    This function computes a single slice of the spectogram.
    """
    #print(f'raw frame:{np.shape(raw_frame)}')
    # first, sum across all antennas
    summed_radar_frame = np.sum(raw_frame, axis=0)
    #print(f'summed frame:{np.shape(summed_radar_frame)}')

    # compute the range DFT
    range_chirp_matrix = compute_range_dft(summed_radar_frame, 
                                           range_axis=1, 
                                           window_type=processing_params.range_window_type, 
                                           dft_resolution_factor=processing_params.range_dft_res)
    #print(f'rcm:{np.shape(range_chirp_matrix)}')
    
    # sum across the ranges greater than the specified minimum range
    range_per_step = np.shape(range_chirp_matrix)[1] / metrics['max_range_m']
    starting_idx = int(np.ceil(processing_params.range_minimum_m / range_per_step))
    summed_slice = np.sum(range_chirp_matrix[:, starting_idx:], axis=1)

    #print(f'summed slice:{np.shape(summed_slice)}')
                                        
    # compute the doppler DFT
    doppler_slice = compute_doppler_dft(summed_slice, 
                                        velocity_axis=0, 
                                        window_type=processing_params.velocity_window_type, 
                                        dft_resolution_factor=processing_params.velocity_dft_res)
    
    # compute the absolute val
    abs_doppler_slice = np.abs(doppler_slice)

    print(f'spectogram slice:{np.shape(abs_doppler_slice)}')
    return abs_doppler_slice

def spectrogram_postprocessing(spectrogram, processing_params):
    """
    This function takes the transpose, so that time is on the x-axis.
    It also applies the clipping operation using the specified clipping factors.
    It also takes the logarithm.
    Also, if there are any coefficients specified for the time-domain filter, it applies those here.
    """
    print(f'unprocessed spectrogram:{np.shape(spectrogram)}')
    # take the transpose, so that time is on the x-axis
    flipped_spectogram = np.transpose(spectrogram)
    print(f'flipped_spectrogram:{np.shape(flipped_spectogram)}')

    # perform the clipping
    max_amplitude = np.max(flipped_spectogram) * processing_params.amplitude_cutoff_factor_max
    min_amplitude = np.max(flipped_spectogram) * processing_params.amplitude_cutoff_factor_min
    clipped_spectogram = np.clip(flipped_spectogram, min_amplitude, max_amplitude)

    # change to a logarithmic scaling of the amplitude
    log_spectogram = np.log10(clipped_spectogram)

    # perform the time-domain filtering if specified in the processing_params
    if processing_params.time_filter_coefficients is not None:
        final_spectogram = scipy.ndimage.convolve1d(log_spectogram, processing_params.time_filter_coefficients, axis=0)
    else:
        final_spectogram = log_spectogram

    print(f'final spectrogram:{np.shape(final_spectogram)}')
    return final_spectogram

def build_spectrogram_matrix(radar_frames, params, metrics):
    """
    Construct the spectrogram matrix from raw radar frames.
    """
    # average over all of the antennas used
    print(np.shape(radar_frames))
    raw_sum = np.sum(radar_frames, axis=1)
    print(np.shape(raw_sum))

    range_chirp_tensor = compute_range_dft(raw_sum, range_axis=2, dft_resolution_factor=params.range_dft_res, window_type=params.range_window_type)
    print(np.shape(range_chirp_tensor))
    
    range_doppler_tensor = compute_doppler_dft(range_chirp_tensor, velocity_axis=1, dft_resolution_factor=params.velocity_dft_res, window_type=params.velocity_window_type)

    # get the abs val of the tensor
    abs_range_doppler_tensor = np.abs(range_doppler_tensor)

    # TODO: I'm skipping the filter stage for now
    filtered_range_doppler_tensor = abs_range_doppler_tensor

    range_per_step = np.shape(filtered_range_doppler_tensor)[2] / metrics['max_range_m']
    starting_idx = int(np.ceil(params.range_minimum_m / range_per_step))
    unprocessed_spectrogram = np.sum(filtered_range_doppler_tensor[:, :, starting_idx:], axis=2)
    """
    # trim using the given params
    matrix_to_plot = np.log10(np.where(unprocessed_spectrogram < 1E-6, 1E-6, unprocessed_spectrogram))

    # clip out the most extreme values and rotate
    cutoff_factor = 1
    highest_point = cutoff_factor * np.max(matrix_to_plot)
    matrix_to_plot = np.transpose(np.where(matrix_to_plot > highest_point, highest_point, matrix_to_plot)) # the transpose rotates the image so that time is on x
    """
    matrix_to_plot = spectrogram_postprocessing(unprocessed_spectrogram, processing_params=params)
    return matrix_to_plot