import numpy as np
import matplotlib.pyplot as plt
from parameter_defs import ProcessingParameters, RadarParameters

def generate_title_string(processing_params):
    return "Title"

def plot_spectogram(processed_spectogram, title_string, radar_parameters=None, metrics=None): # the other method wasn't working
    """
    This function simply generates a single image for the spectrogram.
    It does not apply any additional processing.
    """
    max_velocity = metrics['max_speed_m_s']

    # make the figure and axis obj
    fig, ax = plt.subplots()

    # set title
    ax.set_title(title_string)

    # get the heatmap
    ax = plt.imshow(processed_spectogram, cmap='hot', interpolation='nearest', aspect='auto')

    if (radar_parameters is not False) and (metrics is not None): # only make the axes if these bits of info are available
        # set labels and axis scaling
        num_xticks = 10
        num_yticks = 9 # use an odd number to make a tick for v=0
        plt_axes = ax.axes
        plt_axes.set_xlabel('time (sec)')
        plt_axes.set_ylabel('velocity (m/s)')

        num_frames = np.shape(processed_spectogram)[1]
        duration_of_spectogram = num_frames * radar_parameters.frame_repitition_time_s
        xtickvals = np.ndarray.tolist(np.linspace(0, duration_of_spectogram, num_xticks))
        xlabels = list()
        for fp in xtickvals:
            xlabels.append('%.1f' % fp)
        plt_axes.set_xticks(np.linspace(0, np.shape(processed_spectogram)[1]-1, num_xticks), xlabels)

        ytickvals = np.ndarray.tolist(np.linspace(max_velocity, -max_velocity, num_yticks))
        ylabels = list()
        for fp in ytickvals:
            ylabels.append('%.1f' % fp)
        plt_axes.set_yticks(np.linspace(0, np.shape(processed_spectogram)[0]-1, num_yticks), ylabels)

    # show the plot
    plt.show()

    # allow saving by returning the fig
    return fig
