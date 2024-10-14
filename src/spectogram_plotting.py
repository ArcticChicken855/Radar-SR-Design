import numpy as np
import matplotlib.pyplot as plt
from parameter_defs import ProcessingParameters, RadarParameters

def generate_title_string(p_params):
    return "Title"

def plot_spectorgam(processed_spectogram, title_string):
    """
    This function simply generates a single image for the spectrogram.
    It does not apply any additional processing.
    """

    # make the figure and axis obj
    fig, ax = plt.subplots()

    # set title
    ax.set_title(title_string)

    # get the heatmap
    ax = plt.imshow(processed_spectogram, cmap='hot', interpolation='nearest', aspect='auto')

    # show the plot
    fig.show()

    # allow saving by returning the fig
    return fig

def plot_spectorgam(processed_spectogram, title_string, metrics):
    """
    This function simply generates a single image for the spectrogram.
    It does not apply any additional processing.
    """
    max_velocity = metrics['max_velocity']

    # make the figure and axis obj
    fig, ax = plt.subplots()

    # set title
    ax.set_title(title_string)

    # get the heatmap
    ax = plt.imshow(processed_spectogram, cmap='hot', interpolation='nearest', aspect='auto')

    
    # set labels and axis scaling
    num_xticks = 10
    num_yticks = 9 # use an odd number to make a tick for v=0
    plt_axes = ax.axes
    plt_axes.set_xlabel('time (sec)')
    plt_axes.set_ylabel('velocity (m/s)')

    num_frames = np.size(processed_spectogram[0])
    xtickvals = np.ndarray.tolist(np.linspace(0, max_velocity * num_frames, num_xticks))
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
    fig.show()

    # allow saving by returning the fig
    return fig
