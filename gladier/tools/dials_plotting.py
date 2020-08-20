#!/usr/bin/env python

import sys
import json
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.cm as cm

import sys
import json
import numpy as np
from matplotlib import pyplot as plt

def get_dims(beam_json_fname):
    with open(beam_json_fname, 'r') as f:
        beam_json = json.load(f)
        xdim = beam_json['user_input']['x_num_steps']
        ydim = beam_json['user_input']['y_num_steps']
    return xdim, ydim

def get_lattice_counts(xdim, ydim, int_files):
    lattice_counts = np.zeros(xdim*ydim, dtype=np.dtype(int))
    for int_file in int_files:
        int_file = int_file.rstrip('.pickle\n')
        index = int(int_file.split('_')[2])
        lattice_counts[index] += 1
    lattice_counts = lattice_counts.reshape((ydim, xdim))
    # reverse the order of alternating rows
    lattice_counts[1::2, :] = lattice_counts[1::2, ::-1]
    return lattice_counts

def plot_lattice_counts(xdim, ydim, lattice_counts, plot_name, batch=False):
    fig = plt.figure(figsize=(xdim/10., ydim/10.))
    plt.axes([0, 0, 1, 1])  # Make the plot occupy the whole canvas
    plt.axis('off')
    if batch:
        lattice_counts = np.ma.masked_where(lattice_counts == 0, lattice_counts)
        plt.imshow(lattice_counts, cmap='hot', interpolation=None, vmin=0, vmax=4)
        plt.savefig(plot_name, transparent=True)
    else:
        plt.imshow(lattice_counts, cmap='hot', interpolation=None, vmax=4)
        plt.savefig(plot_name)

if __name__ == '__main__':
    try:
        beam_json_filename = sys.argv[1]
        int_list_filename = sys.argv[2]
    except:
        print('Usage: ./batch_int_files.py beamline_input.json <file with list of int files>')
        sys.exit(1)
    xdim, ydim = get_dims(beam_json_filename)
    lattice_counts = get_lattice_counts(xdim, ydim,
                                            int_list_filename)
    plot_lattice_counts(xdim, ydim, lattice_counts)

