import json
from os import path
import numpy as np
import matplotlib.pyplot as plt
from argparse import ArgumentParser

import wakeblastersdk as sdk

def perform_simulation(api_key, url=None):
    here = path.abspath(path.dirname(__file__))
    
    # pass your user-specific api key (obtained from the WakeBlaster support team) here:
    sdk.set_api_url_and_key(api_key, url)

    # 1. Upload designs and farm. This needs to be done only once
    with open(path.join(here, 'examples/SWT-2.3-93m.wtg')) as fp:
        wtg_file = fp.read()
    sdk.upload_turbine_design('SWT 2.3 93m', wtg_file)
    farm_id = 'Lillgrund_demo'
    with open(path.join(here, 'examples/Lillgrund.json'), 'r') as fp:
        wind_farm_def = json.load(fp)
        sdk.upload_asset(farm_id, wind_farm_def)
    reference_id = 'A01'

    # 2. Submit measurements
    _wind_speed_key = 'WNAC_WindSpeed_avg'  # This string has a format that identifies to WakeBlaster it represents wind speed
    _wind_direction_key = 'WNAC_WindDirection_avg'  # This string has a format that identifies to WakeBlaster it represents wind direction
    wind_speed = 8.0
    wind_directions = np.linspace(0, 360.0, 36, endpoint=False)
    measurements = []
    for direction in wind_directions:
        flow_case_id = 'WD{}'.format(direction)
        measurements.append({'instance_id': reference_id, 'signal_id': _wind_speed_key,
                            'flow_case_id': flow_case_id, 'value': wind_speed})
        measurements.append({'instance_id': reference_id, 'signal_id': _wind_direction_key,
                            'flow_case_id': flow_case_id, 'value': direction})
    measurement_set_id = sdk.upload_measurement_set(farm_id, measurements)['id']

    # 3. Kick off the simulation
    with open(path.join(here, 'examples/simulator-config.json'), 'r') as fp:
        simulation_config = json.load(fp)
    simulation_id = sdk.run_simulation(simulation_config, [measurement_set_id])['id']

    # 4. Get the results and plot them
    results = sdk.retrieve_results(simulation_id, len(wind_directions))
    results.sort(key=lambda r: r['farm_wind_direction'])    # sort by wind direction
    farm_powers = [r['farm_power_output'] for r in results]
    plt.plot(wind_directions, farm_powers)
    plt.show()

def main():
    parser = ArgumentParser()
    parser.add_argument('--api-key', help='The API key', required=True)
    parser.add_argument('--url', help='The API url', required=True)
    args = parser.parse_args()
    perform_simulation(args.api_key, args.url)

if __name__ == '__main__':
    main()
