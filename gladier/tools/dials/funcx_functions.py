def funcx_create_phil(data):
    """Create a phil file if one doesn't already exist"""
    import json
    import os
    from string import Template

    run_num = data['input_files'].split("/")[-1].split("_")[1]
    run_dir = "/".join(data['input_files'].split("/")[:-1])

    if 'suffix' in data:
        phil_name = f"{run_dir}/process_{run_num}_{data['suffix']}.phil"
    else:
        phil_name = f"{run_dir}/process_{run_num}.phil"

    beamline_json = f"beamline_run{run_num}.json"
    unit_cell = data.get('unit_cell', None)
    mask = data.get('mask', 'mask.pickle')

    # Prefix mask with ../ if it isn't a full path
    if "/" not in mask:
        mask = f"../{mask}"

    beamline_data = None
    os.chdir(run_dir)

    try:
        with open(beamline_json, 'r') as fp:
            beamline_data = json.loads(fp.read())

        if not unit_cell:
            unit_cell = beamline_data['user_input']['unit_cell']

        unit_cell = unit_cell.replace(",", " ")
        space_group = beamline_data['user_input']['space_group']
        det_distance = float(beamline_data['beamline_input']['det_distance']) * -1.0

    except:
        pass

    template_data = {'det_distance': det_distance,
                     'unit_cell': unit_cell,
                     'nproc': data['nproc'],
                     'space_group': space_group,
                     'beamx': data['beamx'],
                     'beamy': data['beamy'],
                     'mask': mask}

    template_phil = Template("""spotfinder.lookup.mask=$mask
integration.lookup.mask=$mask

spotfinder.filter.min_spot_size=2
significance_filter.enable=True

#significance_filter.isigi_cutoff=1.0

mp.nproc = $nproc
mp.method=multiprocessing

refinement.parameterisation.detector.fix=none
geometry {
  detector {
      panel {
                fast_axis = 0.9999673162585729, -0.0034449798523932267, -0.007314268824966957
                slow_axis = -0.0034447744696749034, -0.99999406591948, 4.0677756813531234e-05
                origin    = $beamx, $beamy, $det_distance
                }
            }
         }
indexing {
  known_symmetry {
    space_group = $space_group
    unit_cell = $unit_cell
  }
  stills.indexer=stills
  stills.method_list=fft1d
  multiple_lattice_search.max_lattices=3
}""")
    phil_data = template_phil.substitute(template_data)

    with open(phil_name, 'w') as fp:
        fp.write(phil_data)
    return phil_name


def funcx_stills_process(data):
    import os
    import shutil
    import subprocess
    from distutils.dir_util import copy_tree
    from subprocess import PIPE

    def append_suffix(string, suffix):
        if suffix:
            return f'{string}_{suffix}'
        else:
            return string

    # change to the process dir
    run_dir = "/".join(data['input_files'].split("/")[:-1])
    exp_name = data['input_files'].split("/")[-1].split("_")[0]

    if 'suffix' in data:
        suffix = data['suffix']
    else:
        suffix = None

    process_dir = append_suffix(f'{run_dir}/{exp_name}_processing', suffix)
    
    if 'temp_directory' in data:
        temp_directory = data["temp_directory"]
        tmp_run_dir = append_suffix(f'{temp_directory}/{exp_name}', suffix)
        tmp_process_dir = append_suffix(f'{temp_directory}/{exp_name}/{exp_name}_processing', suffix)
    else:
        temp_directory = run_dir
        tmp_run_dir = run_dir
        tmp_process_dir = process_dir


    for directory in [process_dir, tmp_run_dir, tmp_process_dir]:
        os.makedirs(directory, exist_ok=True)

    try:
        run_num = data['input_files'].split("_")[1]
        mask_name = data.get('mask', 'mask.pickle').split("/")[-1]
        mask_name_run = os.path.join(run_dir, mask_name)
        phil_file_run = append_suffix(f'{run_dir}/process_{run_num}', suffix) + ".phil"
        
        if 'temp_directory' in data:
            phil_file_tmp = append_suffix(f"{tmp_run_dir}/process_{run_num}", suffix) + ".phil"
            mask_name_tmp = os.path.join(tmp_run_dir, mask_name)
            shutil.copy(phil_file_run, phil_file_tmp)
            shutil.copy(mask_name_run, mask_name_tmp)

    except Exception as e:
        return str(e)

    # Copy inputs into the tmp dir
    if 'temp_directory' in data:
        os.chdir(tmp_run_dir)
        cmd = f"cp {data['input_files']} {tmp_run_dir}/"
        res = subprocess.run(cmd, stdout=PIPE, stderr=PIPE,
                             shell=True, executable='/bin/bash')

        os.chdir(tmp_process_dir)
    else:
        os.chdir(process_dir)

    file_end = data['input_range'].split("..")[-1]
    input_files = data['input_files'].replace(run_dir, tmp_run_dir)
    dials_directory = data['dials_directory']

    if "timeout" in data:
        timeout = data["timeout"]
        cmd = f'source {dials_directory}/dials_env.sh; timeout {timeout} dials.stills_process {phil_file_run} {input_files} > log-{file_end}.txt'
    else:
        cmd = f'source {dials_directory}/dials_env.sh; dials.stills_process {phil_file_run} {input_files} > log-{file_end}.txt'

    with open('cmd.txt', 'w') as fp:
        fp.write(cmd)
    try:
        res = subprocess.run(cmd, stdout=PIPE, stderr=PIPE,
                             shell=True, executable='/bin/bash')
    except:
        pass

    # copy results back and unlink the tmp dir
    if 'temp_directory' in data:
        shutil.copytree(tmp_process_dir, process_dir, dirs_exist_ok=True)
        shutil.rmtree(tmp_run_dir)
    if 'move_phil_to_proc' in data:
        shutil.move(phil_file_run, process_dir)
    return str(res.stdout)


def funcx_plot_ssx(data):
    import os
    import json
    import shutil
    import subprocess
    from subprocess import PIPE
    import numpy as np
    from matplotlib import pyplot as plt
    import matplotlib.cm as cm
    from gladier.tools.dials.plot_ints import get_dims, get_lattice_counts, plot_lattice_counts

    # get the x/y dims
    run_num = data['input_files'].split("_")[1]
    run_dir = "/".join(data['input_files'].split("/")[:-1])
    exp_name = data['input_files'].split("/")[-1].split("_")[0]

    os.chdir(run_dir)

    phil_name = f"{run_dir}/process_{run_num}.phil"
    beamline_json = f"beamline_run{run_num}.json"
    beamline_data = None

    with open(beamline_json, 'r') as fp:
        beamline_data = json.loads(fp.read())

    xdim = int(beamline_data['user_input']['x_num_steps'])
    ydim = int(beamline_data['user_input']['y_num_steps'])

    # Get the list of int files in this range
    int_files = []

    # Get all the int files
    for filename in os.listdir(f'{exp_name}_processing'):
        try:
            if "int-" in filename and ".pickle" in filename:
                int_files.append(filename)
        except:
            pass

    lattice_counts = get_lattice_counts(xdim, ydim, int_files)
    plot_name = f'1int-sinc-{data["input_range"]}.png'
    plot_lattice_counts(xdim, ydim, lattice_counts, plot_name)

    # move the image file up a line
    exp_name = data['input_files'].split("/")[-1].split("_")[0]

    # create an images directory
    image_dir = f"{run_dir}/{exp_name}_images"
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)

    int_file = f"{run_dir}/{exp_name}_images/{exp_name}_ints.txt"
    with open(int_file, 'w+') as fp:
        fp.write("\n".join(i for i in int_files))

    shutil.copyfile(plot_name, f"{image_dir}/{plot_name}")
    shutil.copyfile(plot_name, f"{image_dir}/composite.png")
    shutil.copyfile(f"{run_dir}/{beamline_json}", f"{image_dir}/{beamline_json}")
    shutil.copyfile(f"{phil_name}", f"{image_dir}/{phil_name.split('/')[-1]}")

    os.chdir(image_dir)

    cmd = f"dials.unit_cell_histogram ../{exp_name}_processing/*integrated_experiments.json"

    subprocess.run(cmd, stdout=PIPE, stderr=PIPE, shell=True, executable='/bin/bash')
    return plot_name


def funcx_pilot(data):
    """
    Data should be a dict containing the following.
    * input_files -- A range-path filename which should expand in bash to
      all of the files that should be collected. For example:
    /projects/APSDataAnalysis/SSX/S8/nsp10nsp16/A/Akaroa5_6_{00001..00256}.cbf
    * metadata -- Metadata dict to be uploaded to search. See pilot docs for
      details:
    https://github.com/globusonline/pilot1-tools/blob/master/docs/reference.rst#metadata  # noqa
    * pilot -- dict of extra pilot args, Ex:
        {
            'config': '~/.pilot-kanzus.cfg',
            'context': 'kanzus',
            'project': 'ssx-test',
            'local_endpoint': '08925f04-569f-11e7-bef8-22000b9a448b',
            'dry_run': False,  # Don't upload result, just do test run
        }
    """
    import os
    import json
    import pilot.client

    exp_name = data['metadata']['chip']
    exp_num = data['metadata']['experiment_number']
    run_dir = os.path.dirname(data['input_files'])
    # Ex: /projects/APSDataAnalysis/SSX/S8/nsp10nsp16/A/Akaroa5_processing
    proc_dir = os.path.join(run_dir, f'{exp_name}_processing')
    assert os.path.exists(run_dir), f'"input_files" dir does not exist: {run_dir}'
    assert os.path.exists(proc_dir), f'processing dir does not exist: {proc_dir}'

    # Ex: /projects/APSDataAnalysis/SSX/S8/nsp10nsp16/A/Akaroa5_images
    image_dir = os.path.join(run_dir, f'{exp_name}_images')
    # Ex: /projects/APSDataAnalysis/SSX/S8/nsp10nsp16/A/beamline_run6.json
    beamline_file = os.path.join(run_dir, f'beamline_run{exp_num}.json')

    os.chdir(proc_dir)
    dir_contents = os.listdir()

    cbf_files = []
    int_files = []
    for filename in dir_contents:
        if 'int-' in filename:
            int_files.append(filename)
        elif 'datablock.json' in filename:
            cbf_files.append(filename)

    min_cbf = 1000000
    max_cbf = 0
    for filename in cbf_files:
        tmp_name = int(filename.split("_")[-2])
        if tmp_name > max_cbf:
            max_cbf = tmp_name
        elif tmp_name < min_cbf:
            min_cbf = tmp_name

    metadata = data['metadata']

    metadata['batch_info']['cbf_files'] = len(cbf_files)
    metadata['batch_info']['cbf_file_range'] = {'from': min_cbf, 'to': max_cbf}
    metadata['batch_info']['total_number_of_int_files'] = len(int_files)

    # Read in the beamline.json file
    with open(beamline_file, 'r') as fp:
        beamline_meta = json.load(fp)
    try:
        metadata.update(beamline_meta)
        metadata['protein'] = beamline_meta['user_input']['prot_name']
    except:
        pass

    pargs = data.get('pilot', {})
    pc = pilot.client.PilotClient()
    assert pc.is_logged_in(), 'Please run `pilot login --no-local-server`'
    assert pc.context.current == pargs.get('context', 'kanzus'), 'Please run `pilot context set kanzus`'
    pc.project.current = pargs.get('project', 'ssx')
    # Set this to the local Globus Endpoint
    local_endpoint = pargs.get('local_endpoint', '08925f04-569f-11e7-bef8-22000b9a448b')
    pc.profile.save_option('local_endpoint', local_endpoint)
    assert image_dir.endswith('_images'), f'Filename {image_dir} DOES NOT appear to be correct'
    result = pc.upload(image_dir, '/', metadata=data['metadata'], update=True, skip_analysis=True,
                       dry_run=pargs.get('dry_run', False))
    # For some reason, these cause problems. Delete them before returning.
    del result['previous_metadata']
    del result['upload']

    return result


def funcx_count_ints(data):
    import glob
    import pandas as pd

    beamx = data['beamx']
    beamy = data['beamy']
    run_dir = "/".join(data['input_files'].split("/")[:-1])
    experiment_name = data['input_files'].split("/")[-1].split("_")[0]
    process_dir = f'{run_dir}/{experiment_name}_processing_' + data['random_str']

    int_files = glob.glob(f"{process_dir}/int-*.pickle")
    num_int_files = len(int_files)
    df = pd.DataFrame({"X": [beamx], "Y": [beamy], "Ints": [num_int_files]})

    return int_files, num_int_files, df


def validate_json(data, schema):
    import json
    from jsonschema import validate
    from jsonschema.exceptions import ValidationError, SchemaError
    validate(instance=data, schema=schema)

    # try:
    #     validate(instance=data, schema=schema)
    # except SchemaError:
    #     print("Invalid schema")
    #     raise
    # except ValidationError as e:
    #     msg = f'Unable to validate JSON. {e.message}'
    #     raise ValidationError(msg)



