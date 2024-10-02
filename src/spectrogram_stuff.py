"""
Functions for computing the spectrogram from raw radar frames.
Primarily use build_spectrogram_matrix

Functions by Nathan
Stripped Down and Repurposed by William
"""

import numpy as np


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


def build_spectrogram_matrix(radar_frames):
    """
    Construct the spectrogram matrix from raw radar frames.
    """

    range_chirp_tensor = compute_range_dft(radar_frames)
    range_doppler_tensor = compute_doppler_dft(range_chirp_tensor)

    # get the abs val of the tensor
    abs_range_doppler_tensor = np.abs(range_doppler_tensor)

    # average over all of the antennas used
    avg_abs_range_doppler_tensor = np.sum(abs_range_doppler_tensor, axis=1)

    # TODO: I'm skipping the filter stage for now
    filtered_range_doppler_tensor = avg_abs_range_doppler_tensor

    cut_distance_factor = 0.01
    cut_length = round(np.size(filtered_range_doppler_tensor[0, 0]) * cut_distance_factor)
    spectrogram = np.sum(filtered_range_doppler_tensor[:, :, cut_length:], axis=2)

    # use log scale, and cut off vals near zero
    matrix_to_plot = np.log10(np.where(spectrogram < 1E-6, 1E-6, spectrogram))

    # clip out the most extreme values and rotate
    cutoff_factor = 1
    highest_point = cutoff_factor * np.max(matrix_to_plot)
    matrix_to_plot = np.transpose(np.where(matrix_to_plot > highest_point, highest_point, matrix_to_plot)) # the transpose rotates the image so that time is on x

    return matrix_to_plot

def build_spectrogram_matrix_efficient(radar_frames):
    """
    Construct the spectrogram matrix from raw radar frames.
    """
    summed_radar_frames = np.sum(radar_frames, axis=1) # sub before the fft

    range_chirp_tensor = compute_range_dft(summed_radar_frames, range_axis=2)
    range_doppler_tensor = compute_doppler_dft(range_chirp_tensor, velocity_axis=1)

    # get the abs val of the tensor
    abs_range_doppler_tensor = np.abs(range_doppler_tensor)

    # TODO: I'm skipping the filter stage for now
    filtered_range_doppler_tensor = abs_range_doppler_tensor

    cut_distance_factor = 0.01
    cut_length = round(np.size(filtered_range_doppler_tensor[0, 0]) * cut_distance_factor)
    spectrogram = np.sum(filtered_range_doppler_tensor[:, :, cut_length:], axis=2)

    # use log scale, and cut off vals near zero
    matrix_to_plot = np.log10(np.where(spectrogram < 1E-6, 1E-6, spectrogram))

    # clip out the most extreme values and rotate
    cutoff_factor = 1
    highest_point = cutoff_factor * np.max(matrix_to_plot)
    matrix_to_plot = np.transpose(np.where(matrix_to_plot > highest_point, highest_point, matrix_to_plot)) # the transpose rotates the image so that time is on x

    return matrix_to_plot
