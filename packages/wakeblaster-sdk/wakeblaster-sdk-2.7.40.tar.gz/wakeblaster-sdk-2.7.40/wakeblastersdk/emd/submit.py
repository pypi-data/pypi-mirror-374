from os import makedirs
import sys
import json
import random
import string
from itertools import groupby

from .wakeRequest import LoadWakeReqFile
from .converters import *
from .. import sdk as _sdk

class _DryRun:
    RETURN_VALUES = {
        'upload_measurement_set': {'id': 'measurement_set_id'},
        'run_simulation': {'id': 'simulation_id', 'version': '0.0.0'},
    }
    class _Callable:
        def __init__(self, name):
            self._name = name
    
        def __call__(self, *args, **kwargs):
            sys.stdout.write('Calling {} with args: {}, kwargs: {}\n'.format(self._name, args, kwargs))
            return _DryRun.RETURN_VALUES.get(self._name)
        
    def __getattr__(self, name):
        return self._Callable(name)

def submit_wakereq(file,
                   simulation_dir='.windpro',
                   max_measurements_per_set=250,
                   calculation_configuration=None,
                   dry_run=False,
                   associated_wind_speed_reference=10.5,
                   flow_case_count=None):
    """Submits a wakereq file to wakeblaster

    :param file: The file to submit
    :type file: str
    :param simulation_dir: The directory in which to store simulation data.
    :type simulation_dir: str
    :param calculation_configuration: Override the calculation configuration in the file
    :type calculation_configuration: dict

    :returns: The ID of the simulation
    :rtype: str
    """
    sdk = _DryRun() if dry_run else _sdk
    wake_req = LoadWakeReqFile(file)
    farm_id = 'test_farm_' + ''.join(random.choice(string.ascii_lowercase+string.digits) for _ in range(5))
    for design_id, wtg_file in to_design_descriptions(wake_req):
        sdk.upload_turbine_design(to_qualified_id(farm_id, design_id), wtg_file)
    sdk.upload_met_mast_design(*to_reference_design(wake_req))
    wind_farm_turbulence = to_wind_farm_turbulence(wake_req.Farm)
    flow_cases = to_flow_case_dataframe(wake_req)
    sim_config = calculation_configuration or to_simulation_config(wake_req.CalculationConfigurations)
    use_instance_wind_speed_measurements =\
        sim_config.get('measurements', {}).get('wind_conditions_inference') == 'InstanceBased'
    if use_instance_wind_speed_measurements:
        assoc_wind_speeds = None
    else:
        assoc_wind_speeds = to_associated_wind_speeds(flow_cases, wake_req)
    sdk.upload_asset(farm_id,
                     to_wind_farm_description(farm_id, wake_req.Turbines, wake_req.Reference),
                     associated_wind_speeds=assoc_wind_speeds,
                     wind_farm_turbulence=wind_farm_turbulence)
    keyfunc = lambda m: m.get('flow_case_id') or m['timestamp']
    measurements = sorted(to_measurements(flow_cases, use_instance_wind_speed_measurements), key=keyfunc)
    measurement_set_ids = []
    pending_measurements = []
    for key, group in groupby(measurements, keyfunc):
        next_measurements = list(group)
        if len(pending_measurements) + len(next_measurements) > max_measurements_per_set:
            print(next_measurements)
            print(len(next_measurements))
            print(pending_measurements)
            measurement_set_ids.append(sdk.upload_measurement_set(farm_id, pending_measurements)['id'])
            pending_measurements = next_measurements
        else:
            pending_measurements += next_measurements
    if pending_measurements:
        measurement_set_ids.append(sdk.upload_measurement_set(farm_id, pending_measurements)['id'])
    result = sdk.run_simulation(sim_config, measurement_set_ids)
    simulation_id = result['id']
    if not path.isdir(simulation_dir):
        makedirs(simulation_dir)
    with open(path.join(simulation_dir, simulation_id + '.json'), 'w') as fp:
        json.dump(get_job_info(wake_req.JobInfo, simulation_id, result['version'], file), fp)
    return simulation_id

def generate_wakeres(simulation_id, simulation_dir='.windpro', dry_run=False):
    """Downloads simulation results and generates a wakeres file

    :param simulation_id: The ID of the simulation to get
    :type simulation_id: str
    :param simulation_dir: The directory used for the simulation data (should contain the <simulation_id>.json file)
    :type simulation_dir: str
    """
    sdk = _DryRun() if dry_run else _sdk
    simulation_info_file = path.join(simulation_dir, simulation_id + '.json')
    if not path.isfile(simulation_info_file):
        raise FileNotFoundError(simulation_info_file)
    with open(simulation_info_file) as fp:
        job_info = json.load(fp)
    output_path = path.join(simulation_dir, simulation_id + '.wakeRes')
    results = sdk.retrieve_results(job_info['simulation_id'], wait=60., partial=False)
    if results is None:
        raise RuntimeError('Could not retrieve results after timeout')
    to_wakeres(job_info, results, output_path)
