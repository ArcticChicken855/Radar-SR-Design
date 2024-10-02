# py .\src\fall_data_processing.py FALL1_9_3_2024 [1,2,3]


import numpy as np
import os
import pickle
import matplotlib.pyplot as plt
import matplotlib.animation
import scipy.ndimage
from time import time
from pathlib import Path
import sys
import scipy.signal as signal

# set up the timing stuff
global pkl_load_time
pkl_load_time = 0
global range_dft_function_time
range_dft_function_time = 0
global doppler_dft_function_time
doppler_dft_function_time = 0
global range_dft_time
range_dft_time = 0
global doppler_dft_time
doppler_dft_time = 0
global window_multi_time
window_multi_time = 0
#global heatmap_drawing_time
#heatmap_drawing_time = 0
#global heatmap_animation_generation_time
#heatmap_animation_generation_time = 0
global figure_view_time
figure_view_time = 0
global convolve_time
convolve_time = 0
global spectogram_creation_time
spectogram_creation_time = 0

global dummy_timer
dummy_timer = 0

global record_time_sum
record_time_sum = 0
global total_time
total_time = 0
global time_start
time_start = time()


def compute_doppler_DFT(range_chirp_tensor, config, dft_resolution_factor, window_type, fftshift):
    # get a few bits of information to make it easier
    num_frames, num_antennas, chirps_per_frame, range_dft_length = np.shape(range_chirp_tensor)

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
        shaped_window = window[None, None, :, None]

        # get the product
        dummy_timer = time()
        product = range_chirp_tensor * shaped_window
        global window_multi_time
        window_multi_time += time() - dummy_timer

    elif window_type == 'none':
        product = range_chirp_tensor

    # main DFT computation
    dummy_timer = time()
    if fftshift is True:
        output_array = np.fft.fftshift(np.fft.fft(product, n=doppler_dft_length, axis=2), axes=2)
    else:
        output_array = np.fft.fft(product, n=doppler_dft_length, axis=2)
    global doppler_dft_time
    doppler_dft_time += time() - dummy_timer

    # now return the shit
    return output_array

def compute_range_DFT(config, frames, dft_resolution_factor, window_type, positive_frequencies_only):
    # get a few bits of information to make it easier
    num_frames, num_antennas, chirps_per_frame, samples_per_chirp = np.shape(frames)

    # use the resolution factor to find the length of the DFT
    dft_length = dft_resolution_factor * samples_per_chirp

    # get the associated frequency bins to go along with the transform
    freqs = np.fft.fftfreq(n=dft_length, d=1/config['sample_rate_Hz']) #this is the other output

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
        shaped_window = window[None, None, None, :]

        # get the product
        dummy_timer = time()
        product = frames * shaped_window
        global window_multi_time
        window_multi_time += time() - dummy_timer

    elif window_type == 'none':
        product = frames

    # main DFT computaton
    dummy_timer = time()
    output_array = np.fft.fft(product, n=dft_length, axis=3)
    global range_dft_time
    range_dft_time += time() - dummy_timer

    # if requested, only return the positive frequencies of the DFT
    if positive_frequencies_only:
        output_array = output_array[:, :, :, 0:int(dft_length/2)]
        freqs = freqs[0:int(dft_length/2)]

    # now return the shit
    return [freqs, output_array]
            
def get_average_ranges(range_dft_frames):

    # this function takes in the range-chirp tensor and averages over all of the chirps in the frame, and over all of the antennas
    # get the output
    num_frames, num_antennas, chirps_per_frame, dft_size = np.shape(range_dft_frames)
    output_array = np.zeros((num_frames, dft_size))

    # do the abs
    frames_abs = np.abs(range_dft_frames)

    # then, for each frame, average over the antenna and chirp dimensions
    output_array = np.mean(frames_abs, axis=(1, 2))

    return output_array

def plot_avg_dist(freqs_normalized_to_distance, dist_frames, max_range, notes, window_type):
    # this function will plot the distance, as an average for the whole recording
    avg_distance = np.mean(dist_frames, axis=0)
    plt.plot(freqs_normalized_to_distance, avg_distance)
    plt.xlim((0.15, max_range))
    plt.xlabel('Distance (m)')
    plt.title(notes + f', window={window_type}')

    dummy_timer = time()
    plt.show()
    figure_view_time += time() - dummy_timer
    return

def plot_range_velocity_heatmap(input_matrix, max_range, max_velocity, notes, num_antennas, range_win, velocity_win, r_dft_res, v_dft_res, nfrms, cutoff_factor): # input matrix must be abs val
    # use log scale, and cut off vals near zero
    matrix_to_plot = np.log10(np.where(input_matrix < 1E-6, 1E-6, input_matrix))

    # clip out the most extreme values
    matrix_to_plot = np.where(matrix_to_plot > cutoff_factor * np.max(matrix_to_plot), cutoff_factor * np.max(matrix_to_plot), matrix_to_plot)

    # get the title string
    title_str = f'{notes} ant={num_antennas} win_r={range_win} win_v={velocity_win}\n r_dft={r_dft_res} v_dft={v_dft_res} nfrms={nfrms} cut={cutoff_factor}'
    
    # make the figure and axis obj
    fig, ax = plt.subplots()

    # set title
    ax.set_title(title_str)

    # get the heatmap
    ax = plt.imshow(matrix_to_plot, cmap='hot', interpolation='nearest', aspect='auto')

    # set labels and axis scaling
    num_xticks = 10
    num_yticks = 9 # use an odd number to make a tick for v=0
    plt_axes = ax.axes
    plt_axes.set_xlabel('range (m)')
    plt_axes.set_ylabel('velocity (m/s)')

    xtickvals = np.ndarray.tolist(np.linspace(0, max_range, num_xticks))
    xlabels = list()
    for fp in xtickvals:
        xlabels.append('%.1f' % fp)
    plt_axes.set_xticks(np.linspace(0, np.shape(matrix_to_plot)[1]-1, num_xticks), xlabels)

    ytickvals = np.ndarray.tolist(np.linspace(max_velocity, -max_velocity, num_yticks))
    ylabels = list()
    for fp in ytickvals:
        ylabels.append('%.1f' % fp)
    plt_axes.set_yticks(np.linspace(0, np.shape(matrix_to_plot)[0]-1, num_yticks), ylabels)

    # show the plot
    dummy_timer = time()
    global figure_view_time
    plt.show()
    figure_view_time += time() - dummy_timer

    # allow saving by returning the fig
    return fig

def save_RVheatmap(fig, pkl_num, directory):
    # this function saves the range-doppler heatmaps as a PNG
    RV_directory = directory + "\\RVheat"

    # create the directory if it doesnt exist
    if not os.path.exists(RV_directory):
        os.mkdir(RV_directory)

    # go to the folder and find what file number to create by looping over each number until a file is found
    i=0
    output_filename = False
    while output_filename is False:
        if not os.path.isfile(RV_directory + "\\RVheat_pkl=" + str(pkl_num) + "_im=" + str(i) + ".png"):
            output_filename = RV_directory + "\\RVheat_pkl=" + str(pkl_num) + "_im=" + str(i) + ".png"
        else:
            i += 1

    # now save it using the filename
    fig.savefig(output_filename)

def RV_time_filter(input_tensor, filter_coefficients):
    # this function takes in the full list of range-velocity frames and performs a low-pass filter using convolution
    
    # start by re-shaping the filter coefficients
    #shp = np.shape(input_tensor)
    #shaped_coefficients = np.zeros((np.size(filter_coefficients), shp[1], shp[2]))

    #  now, do the convolution
    filtered_tensor = scipy.ndimage.convolve1d(input_tensor, filter_coefficients, axis=0)

    return filtered_tensor

def animate_range_velocity_heatmap(input_tensor, recording, config, num_antennas, samples_window_type, chirps_window_type, r_dft_res, v_dft_res, playback_speed_multiplier, cutoff_factor, filter_coefficients):
    # use log scale, and cut off vals near zero
    tensor_to_animate = np.log10(np.where(input_tensor < 1E-6, 1E-6, input_tensor))

    # clip out the most extreme values
    tensor_to_animate = np.where(tensor_to_animate > cutoff_factor * np.max(tensor_to_animate), cutoff_factor * np.max(tensor_to_animate), tensor_to_animate)

    # get the title string
    title_str = f'{recording['notes']} ant={num_antennas} win_r={samples_window_type} win_v={chirps_window_type}\n r_dft={r_dft_res} v_dft={v_dft_res} playspeed={playback_speed_multiplier}x cut={cutoff_factor}\n coeffs={filter_coefficients}'
    
    # make the figure and axis obj
    fig, ax = plt.subplots()

    # set title
    ax.set_title(title_str)

    # create the initial heatmap
    heatmap = ax.imshow(tensor_to_animate[0], cmap='hot', interpolation='nearest', aspect='auto')

    # set labels and axis scaling
    num_xticks = 10
    num_yticks = 9 # use an odd number to vet a tick for v=0
    plt_axes = ax.axes
    plt_axes.set_xlabel('range (m)')
    plt_axes.set_ylabel('velocity (m/s)')

    xtickvals = np.ndarray.tolist(np.linspace(0, config['metrics']['max_range_m'], num_xticks))
    xlabels = list()
    for fp in xtickvals:
        xlabels.append('%.1f' % fp)
    plt_axes.set_xticks(np.linspace(0, np.shape(tensor_to_animate[0])[1]-1, num_xticks), xlabels)

    ytickvals = np.ndarray.tolist(np.linspace(config['metrics']['max_speed_m_s'], -config['metrics']['max_speed_m_s'], num_yticks))
    ylabels = list()
    for fp in ytickvals:
        ylabels.append('%.1f' % fp)
    plt_axes.set_yticks(np.linspace(0, np.shape(tensor_to_animate[0])[0]-1, num_yticks), ylabels)

    # make a function to update the frames
    def update(frame):
        heatmap.set_array(tensor_to_animate[frame])
        return heatmap

    anim = matplotlib.animation.FuncAnimation(fig, update, frames=range(np.shape(tensor_to_animate)[0]), interval = config['frame_repetition_time_s'] * 1000 * playback_speed_multiplier)
    
    dummy_timer = time()
    fig.show()
    global figure_view_time
    figure_view_time += time() - dummy_timer

    return anim

def save_range_velocity_animation(anim, pkl_num, directory):
    # this function saves the range-doppler heatmaps as a PNG
    RV_anim_directory = directory + "\\RVheat_anim"

    # create the directory if it doesnt exist
    if not os.path.exists(RV_anim_directory):
        os.mkdir(RV_anim_directory)

    # go to the folder and find what file number to create by looping over each number until a file is found
    i=0
    output_filename = False
    while output_filename is False:
        if not os.path.isfile(RV_anim_directory + "\\RVheat_anim_pkl=" + str(pkl_num) + "_im=" + str(i) + ".gif"):
            output_filename = RV_anim_directory + "\\RVheat_anim_pkl=" + str(pkl_num) + "_im=" + str(i) + ".gif"
        else:
            i += 1

    # now save it using the filename
    anim.save(output_filename, bitrate='10')

def plot_spectorgam_sum(spectogram, cutoff_factor, notes, num_antennas, range_win, velocity_win, r_dft_res, v_dft_res, cut_length_factor, filter_coefficients, framerate, max_velocity):
    # use log scale, and cut off vals near zero
    matrix_to_plot = np.log10(np.where(spectogram < 1E-6, 1E-6, spectogram))

    # clip out the most extreme values and rotate
    highest_point = cutoff_factor * np.max(matrix_to_plot)
    matrix_to_plot = np.transpose(np.where(matrix_to_plot > highest_point, highest_point, matrix_to_plot)) # the transpose rotates the image so that time is on x

    # get the title string
    title_str = f'{notes} ant={num_antennas} win_r={range_win} win_v={velocity_win}\n r_dft={r_dft_res} v_dft={v_dft_res} cutfac={cutoff_factor} cutlen={cut_length_factor}\ncoeffs={filter_coefficients}'
    
    # make the figure and axis obj
    fig, ax = plt.subplots()

    # set title
    ax.set_title(title_str)

    # get the heatmap
    ax = plt.imshow(matrix_to_plot, cmap='hot', interpolation='nearest', aspect='auto')

    
    # set labels and axis scaling
    num_xticks = 10
    num_yticks = 9 # use an odd number to make a tick for v=0
    plt_axes = ax.axes
    plt_axes.set_xlabel('time (sec)')
    plt_axes.set_ylabel('velocity (m/s)')

    num_frames = np.size(matrix_to_plot[0])
    xtickvals = np.ndarray.tolist(np.linspace(0, framerate * num_frames, num_xticks))
    xlabels = list()
    for fp in xtickvals:
        xlabels.append('%.1f' % fp)
    plt_axes.set_xticks(np.linspace(0, np.shape(matrix_to_plot)[1]-1, num_xticks), xlabels)

    ytickvals = np.ndarray.tolist(np.linspace(max_velocity, -max_velocity, num_yticks))
    ylabels = list()
    for fp in ytickvals:
        ylabels.append('%.1f' % fp)
    plt_axes.set_yticks(np.linspace(0, np.shape(matrix_to_plot)[0]-1, num_yticks), ylabels)

    # show the plot
    dummy_timer = time()
    fig.show()
    global figure_view_time
    figure_view_time += time() - dummy_timer

    # allow saving by returning the fig
    return fig

def save_spectogram_plot(fig, pkl_num, directory):
    # this function saves the range-doppler heatmaps as a PNG
    RV_directory = directory + "\\SpectorgamSum"

    # create the directory if it doesnt exist
    if not os.path.exists(RV_directory):
        os.mkdir(RV_directory)

    # go to the folder and find what file number to create by looping over each number until a file is found
    i=0
    output_filename = False
    while output_filename is False:
        if not os.path.isfile(RV_directory + "\\SpectoSum_pkl=" + str(pkl_num) + "_im=" + str(i) + ".png"):
            output_filename = RV_directory + "\\SpectoSum_pkl=" + str(pkl_num) + "_im=" + str(i) + ".png"
        else:
            i += 1

    # now save it using the filename
    fig.savefig(output_filename)

def import_recording(file_num, directory):
    # this function opens up the pickle file and returns the recording
    pkl_directory = directory + "\\IQ pickles"
    pkl_file = open("C:\\Users\\natha\\Alabama\\Senior Design\\Scnd-Radar-SR-Design\\Fall_Data\\FALL_9_23_2024\\IQ pickles\\IQpickle_3.pkl", 'rb')
    recording = pickle.load(pkl_file)
    pkl_file.close()
    return recording

def filter_clutter(range_doppler_tensor, config, order, cutoff_freq):
    """
    This algorithm filters out ground clutter by using a butterworth filter.
    """
    sampling_period = config['repetition_time_s']
    sampling_frequency = 1/sampling_period
    
    nyquist = 0.5 * sampling_frequency

    normalized_cutoff = cutoff_freq / nyquist

    b, a = signal.butter(order, normalized_cutoff, btype='high', analog=False)
    w, h = signal.freqz(b, a, worN=np.shape(range_doppler_tensor)[1], fs=sampling_frequency)

    H_freq = np.abs(h)
    
    half_H = H_freq[0:len(H_freq)//2]
    fixed = np.append(np.flip(half_H), half_H)
    fixed[fixed < 0.001] = np.min(fixed[fixed > 0.001]) / order / 2

    #print(fixed)

    shaped_H = fixed[None, :, None]
    filtered_data_freq = range_doppler_tensor * shaped_H

    return filtered_data_freq

def declutter_algo2(range_doppler_tensor, include_range_info=False, num_frames_to_include=1):

    if include_range_info is True:
        average_ground_clutter = np.sum(range_doppler_tensor[0:num_frames_to_include-1], axis=0)
        return range_doppler_tensor / average_ground_clutter[None, :, :]
    else:
        average_ground_clutter = np.sum(range_doppler_tensor[0:num_frames_to_include-1], axis=(0, 2))
        return range_doppler_tensor / average_ground_clutter[None, :, None]

# get the directory in the second positional argument (after the execution command)
project_dir = Path(__file__).parent.parent
directory = str(project_dir / 'Fall_Data' / sys.argv[1])

# use the third positional argument to specify what IQ pickles to process
files_to_process = sys.argv[2]

# if want to process all files, count how many files there are in the directory
if files_to_process == 'all':
    file_nums = list(range(len(next(os.walk(directory + "\\IQ pickles"))[2]))) # forbidden line of code gifted by the stack overflow gods
else:
    file_nums = sys.argv[2].translate(str.maketrans("", "", "[]")).split(',')

# now, make the main logic that loops over each file that was specified
for filenum in file_nums:
    # import the specified recording from the pickle file
    dummy_timer = time()
    recording = import_recording(filenum, directory)
    pkl_load_time += time() - dummy_timer

    # add the record time to the counter
    record_time_sum += recording['duration']

    # process data from both radars
    radars = ['1', '2']
    for radarnum in radars:
        # specify how many antennas are used in the computation
        num_antennas = 3

        # get the IQ frames, and splice in how many antennas to use
        frames = recording[f'frames_R{radarnum}'][:, 0:num_antennas, :, :]
        print(np.shape(frames))
        # get a few bits of information to make it easier
        if "config" in recording.keys():
            config = recording['config'] # for old recordings
        else:
            config = recording[f'config{radarnum}']
        metrics = config['metrics']
        num_frames, num_antennas, chirps_per_frame, samples_per_chirp = np.shape(frames)

        # get the DFT across the range axis
        range_dft_resolution_factor = 4 # resolution factor, where a val of 1 means that there is not any cutoff or zero padding
        samples_window_type = 'blackman'
        positive_frequencies_only = True

        dummy_timer = time()
        range_freqs, range_chirp_tensor = compute_range_DFT(config, frames, range_dft_resolution_factor, samples_window_type, positive_frequencies_only)
        range_dft_function_time += time() - dummy_timer

        # plot the average distance over the whole recording
        plot_dist = False
        if plot_dist is True:
            # re-normalize the frequency terms into distances
            range_freqs_normalized_to_distance = range_freqs / np.max(range_freqs) * metrics['max_range_m']

            # find the abs, then average over all of the antennas and all of the chirps to get the ranges
            distance_frames = get_average_ranges(range_chirp_tensor)
            plot_avg_dist(range_freqs_normalized_to_distance, distance_frames, metrics['max_range_m'], recording['notes'], samples_window_type)

        # now, get the range-doppler tensor
        doppler_dft_resolution_factor = 4 # resolution factor, where a val of 1 means that there is not any cutoff or zero padding
        chirps_window_type = 'blackman'
        fftshift = True

        dummy_timer = time()
        range_doppler_tensor = compute_doppler_DFT(range_chirp_tensor, config, doppler_dft_resolution_factor, chirps_window_type, fftshift)
        doppler_dft_function_time += time() - dummy_timer

        # get the abs val of the tensor
        abs_range_doppler_tensor = np.abs(range_doppler_tensor)

        # average over all of the antennas used
        avg_abs_range_doppler_tensor = np.sum(abs_range_doppler_tensor, axis=1)

        # try using a butterworth filter to get rid of the ground clutter
        ground_filter_method = 'butterworth'
        if ground_filter_method == "butterworth":
            avg_abs_range_doppler_tensor = filter_clutter(avg_abs_range_doppler_tensor, config, order=3, cutoff_freq=70)
        elif ground_filter_method == "averaging":
            avg_abs_range_doppler_tensor = declutter_algo2(avg_abs_range_doppler_tensor, include_range_info=False, num_frames_to_include=5)
        else:
            pass

        # try plotting the range-velocity heatmap for the average of n frames
        plot_heatmap_single_image = False
        if plot_heatmap_single_image is True:
            frm_start = 20
            nfrms = 5
            matrix_to_plot = np.zeros(np.shape(avg_abs_range_doppler_tensor[0]))
            for k in range(nfrms):
                matrix_to_plot = np.add(matrix_to_plot, avg_abs_range_doppler_tensor[frm_start + k])
            RV_cutoff_factor = 0.5

            fig = plot_range_velocity_heatmap(matrix_to_plot, metrics['max_range_m'], metrics['max_speed_m_s'], recording['notes'], num_antennas, samples_window_type, chirps_window_type, range_dft_resolution_factor, doppler_dft_resolution_factor, nfrms, RV_cutoff_factor)
            
            # save the image
            save_RV_picture = False
            if save_RV_picture is True:
                save_RVheatmap(fig, filenum, directory)

        # now, make an animation of the range-velocity heatmap over the whole recording
        # start by implimenting the time-domain filter across the framenumber
        filter_coefficients = np.array([0.2, 0.4, 0.6, 0.8, 1]) ** 1.5
        #filter_coefficients = np.array([1])
        use_a_filter = False
        if use_a_filter is True:
            dummy_timer = time()
            filtered_range_doppler_tensor = RV_time_filter(avg_abs_range_doppler_tensor, filter_coefficients)
            convolve_time += time() - dummy_timer
        else:
            filtered_range_doppler_tensor = avg_abs_range_doppler_tensor
            filter_coefficients = [1]

        animate_heatmap = False
        if animate_heatmap is True:

            # now, animate it
            playback_speed_multiplier = 0.1
            RV_cutoff_factor = 0.5
            anim = animate_range_velocity_heatmap(filtered_range_doppler_tensor, recording, config, num_antennas, samples_window_type, chirps_window_type, range_dft_resolution_factor, doppler_dft_resolution_factor, playback_speed_multiplier, RV_cutoff_factor, filter_coefficients)

            save_animation = False
            if save_animation is True:
                save_range_velocity_animation(anim, filenum, directory)
        
        plot_spectogram = True
        if plot_spectogram == True:
            # now, try to make a spectogram by summing along range axis
            # only sum across the range vals past a certain point, to avoid the vertical line at x=0
            dummy_timer = time()
            cut_distance_factor = 0.01
            cut_length = round(np.size(filtered_range_doppler_tensor[0, 0]) * cut_distance_factor)
            spectogram_sum = np.sum(filtered_range_doppler_tensor[:, :, cut_length:], axis=2)
            spectogram_creation_time = time() - dummy_timer
            spectogram_cutoff_factor = 1
            spectogram_sum = spectogram_sum[:, 0:round(np.size(spectogram_sum[0, :])/2)] # comment out this line if u want to use full processing
            spectogram_sum_fig = plot_spectorgam_sum(spectogram_sum, spectogram_cutoff_factor, recording['notes'], num_antennas, samples_window_type, chirps_window_type, range_dft_resolution_factor, doppler_dft_resolution_factor, cut_distance_factor, filter_coefficients, config['frame_repetition_time_s'], metrics['max_speed_m_s'])
            plt.show()
            save_spectogram = False
            if save_spectogram is True:
                save_spectogram_plot(spectogram_sum_fig, filenum, directory)
        

# todo: impliment range binning
# todo: impliment microdoppler with STFT

show_time = False
if show_time is True:
    total_time = time() - time_start
    print(f'Total Time={total_time}\npkl_load={pkl_load_time}\nrange_dft_function={range_dft_function_time}\nrange_dft={range_dft_time}\ndoppler_dft_function={doppler_dft_function_time}\ndoppler_dft={doppler_dft_time}\nwindow_multi={window_multi_time}\nfigure_view={figure_view_time}\nconvolve={convolve_time}\nspecto_creation={spectogram_creation_time}')
    unaccounted_time = total_time - pkl_load_time - range_dft_function_time - doppler_dft_function_time - figure_view_time - convolve_time - spectogram_creation_time
    print(f'unaccounted_time={unaccounted_time}')
    print(f'    record_time={record_time_sum}')
    print(f'    efficiency_metric={record_time_sum/total_time}')