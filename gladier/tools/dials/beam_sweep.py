#!/usr/bin/env python

import argparse
import copy
import glob
import json
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import seaborn as sb
import time
import tempfile

from configobj import ConfigObj
from time import sleep
from funcx.sdk.client import FuncXClient
from funcx_functions import funcx_create_phil, funcx_stills_process, funcx_count_ints


def get_random_str():
    random_str = next(tempfile._get_candidate_names())
    while "_" in random_str:
        random_str = next(tempfile._get_candidate_names())  
    return random_str


def get_batch_results(fxc, batch_id):
    tasks = fxc.get_batch_status(batch_id)
    results = []
    for task in tasks.keys():
        result = fxc.get_result(task)
        results.append(result)
    return results


def wait(fxc, job_id):
    start = time.time()
    task = fxc.get_task(job_id)
    while task['pending']:
        time.sleep(3)
        task = fxc.get_task(job_id)
    end = time.time()
    elapsed = end - start
    print("Finished processing job in %d seconds" % elapsed)
    return fxc.get_result(job_id)


def wait_batch(fxc, batch_id):
    start = time.time()
    tasks = fxc.get_batch_status(batch_id)

    for task in tasks:
        print(tasks[task])
        while tasks[task]['pending']:
            time.sleep(3)
            tasks = fxc.get_batch_status(batch_id)

    end = time.time()
    elapsed = end - start
    print("Finished processing task in %d seconds" % elapsed)
    return get_batch_results(fxc, batch_id)
    

def get_function_ids(fxc):
    funcx_config_filename = os.path.expanduser('~') + "/.dials.xysweep.cfg"
    funcx_config = ConfigObj(funcx_config_filename, create_empty=True)

    try:
        fxid_create_phil = funcx_config['funcx_create_phil']
        fxid_stills_process = funcx_config['funcx_stills_process']
        fxid_count_ints = funcx_config['funcx_count_ints']
    except KeyError:
        fxid_create_phil = fxc.register_function(funcx_create_phil, description="Create the phil file for analysis.")
        fxid_stills_process = fxc.register_function(funcx_stills_process, description="Process stills images.")
        fxid_count_ints = fxc.register_function(funcx_count_ints, description="Count number of int files in a directory.")

    config = ConfigObj(funcx_config_filename, create_empty=True)
    config['funcx_create_phil'] = fxid_create_phil
    config['funcx_stills_process'] = fxid_stills_process
    config['funcx_count_ints'] = fxid_count_ints
    config.write()             
    return fxid_create_phil, fxid_stills_process, fxid_count_ints


def plot(df, output="ints.png"):
    table = df.pivot('Y', 'X', 'Ints')
    ax = sb.heatmap(table, annot=True, fmt='d', linewidths=0.5, cmap="Blues")
    ax.invert_yaxis()
    plt.savefig(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    parser.add_argument('--span', default=1.0, type=float, help='Parameter sweep range (should be even)')
    parser.add_argument('--delta', default=0.1, type=float, help='Size of parameter sweep increments')
    parser.add_argument('--significant_digits', default=1, type=int, help='Number of significant digits in beamx/beamy')
    args = parser.parse_args()

    significant_digits = args.significant_digits
    delta = args.delta
    span = args.span
    span_half = span / 2

    with open(args.config) as config_json:
        config = json.load(config_json)
        beamx = float(config['beamx'])
        beamy = float(config['beamy'])
        endpoint = config['endpoint']
        endpoint_local = config['endpoint_local']

    x_values = np.round(np.arange(beamx - span_half, beamx + span_half + delta, delta), decimals=significant_digits)
    y_values = np.round(np.arange(beamy - span_half, beamy + span_half + delta, delta), decimals=significant_digits)

    phil_data = list()
    phil_data2 = list()

    for x in x_values:
        for y in y_values:
            new_config = copy.deepcopy(config)
            new_config['beamx'] = x
            new_config['beamy'] = y
            new_config['suffix'] = get_random_str()
            phil_data.append(new_config)

    fxc = FuncXClient()
    fxc.throttling_enabled = False
    fxid_create_phil, fxid_stills_process, fxid_count_ints = get_function_ids(fxc)

    # Phil files
    print("Running funcx_create_phil")
    phil_batch = fxc.create_batch()
    for phil in phil_data:
        phil_batch.add(phil, endpoint_id=endpoint_local, function_id=fxid_create_phil)
    phil_job = fxc.batch_run(phil_batch)
    wait_batch(fxc, phil_job)

    # Stills process
    print("\nRunning funcx_stills_process")
    stills_batch = fxc.create_batch()
    for phil in phil_data:
        stills_batch.add(phil, endpoint_id=endpoint, function_id=fxid_stills_process)
    stills_job = fxc.batch_run(stills_batch)
    wait_batch(fxc, stills_job)

    # Count ints
    print("\nRunning funcx_count_ints")
    combined_df = pd.DataFrame()
    count_batch = fxc.create_batch()
    for phil in phil_data:
        count_batch.add(phil, endpoint_id=endpoint, function_id=fxid_count_ints)
    count_job = fxc.batch_run(count_batch)
    count_results = wait_batch(fxc, count_job)

    # Create CSV and heatmap
    for df in count_results:
        if combined_df.empty:
            combined_df = df[2]
        else:
            combined_df = pd.concat([combined_df, df[2]], axis=0)

    combined_df.sort_values(['X', 'Y'], ascending=[True, True], inplace=True)
    combined_df.to_csv("ints.csv", index=False)
    plot(combined_df)


if __name__ == "__main__":
    main()
