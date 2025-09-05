import wakeblastersdk as wb
import numpy as np
import pandas as pd
from io import StringIO

from .util import SignalNames as signals


def get_turbine_ids(results):
    return [t['instance_id'] for t in results[0]['turbine_results']]


def json_results_to_dataframe(results, properties, expected_flow_case_ids):
    data = {p: [] for p in properties}
    for result, i in zip(results, range(len(results))):
        if result['flow_case_id'] != expected_flow_case_ids[i]:
            raise ValueError('Flow case ID mismatch')
        for k in data:
            data[k].append(result[k])
    return pd.DataFrame(data)


class WakeBlasterSimulation:
    """Class for inspecting WakeBlaster simulations

    :param simulation_id: The simulation id
    :param flow_case_set: The origin flow case set
    """
    def __init__(self, simulation_id, flow_case_set):
        self._simulation_id = simulation_id
        self._flow_case_set = flow_case_set

    @property
    def id(self):
        return self._simulation_id

    def are_results_ready(self):
        """
        :return: Whether WakeBlaster results have finished being calculated
        """
        simulation_info = wb.get_simulation_info(self._simulation_id)
        return simulation_info['state'] != 'initialising' and \
               simulation_info['result_count'] + simulation_info['error_count'] == simulation_info['flow_case_count']

    def has_errors(self):
        """
        :return: True if there has been at least one flow case in the simulation that resulted in an error
        """
        simulation_info = wb.get_simulation_info(self._simulation_id)
        return simulation_info['error_count'] > 0

    def get_errors(self):
        """
        :return: List of errors that occurred so far in the simulation, where each error is a dict that contains the error message and flow case ID
        """
        return wb.get_error_messages(self._simulation_id)

    def get_results(self, farm_properties, turbine_properties=[]):
        """Gets the results

        :param farm_properties: Fields from farm-level results to be recorded
        :param turbine_properties: Fields from turbine-level results to be recorded

        :return: Tuple containing
            - A `pandas.DataFrame` of the flow case table with an additional column for each farm property.
            - A `dict` of `pandas.DataFrame` s {turbine_property: table}, with one key for each turbine property and each value is a flow case table with one column for each turbine with the turbine ID as the column header.
        """
        if len(farm_properties) > 0:
            results = wb.get_results(self._simulation_id)
            results.sort(key=lambda r: r['flow_case_id'])
            farm_table = pd.concat([self._flow_case_set,
                                    json_results_to_dataframe(results, farm_properties, self._flow_case_set['flow_case_id'])],
                                   axis=1)
        else:
            farm_table = None

        turbine_tables = {}
        for prop in turbine_properties:
            results_csv = wb.get_results(self._simulation_id, format='csv', property=prop)
            turbine_tables[prop] = pd.read_csv(StringIO(results_csv)).sort_values('flow_case_id').reset_index()
            if not turbine_tables[prop]['flow_case_id'].equals(self._flow_case_set['flow_case_id']):
                raise ValueError('Flow cases from results do not match flow case input')

        return farm_table, turbine_tables


def generate_flow_case_ids(flow_case_set):
    """Generate series of flow case ID's based on flow case set"""
    def generate_id(row):
        return '{:05}WS{:.1f}dir{:.1f}'.format(row.name, row[signals.wind_speed], row[signals.wind_direction])
    return flow_case_set.apply(generate_id, axis=1)


def create_single_flow_case_measurements(flow_case, default_instance_id):
    """
    Create measurements for single flow case
    :param flow_case: dict or pandas.DataFrame row with a value for each property. Must contain 'flow_case_id'
    :param default_instance_id: str used for instance identifier when not specified in flow_case index
    :return: `list` of `dict`s, where each dict is a measurement
    """
    if 'flow_case_id' not in flow_case:
        raise ValueError("'flow_case_id' not present in 'flow_case'")
    measurements = []
    for idx, value in flow_case.items():
        if isinstance(idx, tuple) and len(idx) == 2:
            instance_id = idx[0] or default_instance_id
            signal_id = idx[1]
        elif isinstance(idx, str):
            instance_id = default_instance_id
            signal_id = idx
        else:
            raise ValueError('Invalid flow case specification')
        if signals.is_signal(signal_id):
            measurements.append({'flow_case_id': flow_case['flow_case_id'],
                                 'instance_id': instance_id,
                                 'signal_id': signal_id,
                                 'value': value})
    return measurements


class WakeBlasterNewSimulation(WakeBlasterSimulation):
    """
    Handles the running of a single WakeBlaster simulation.
    On creation it will create a measurement set and start a simulation (which is run asynchronously)
    """
    def __init__(self, farm_id, reference_id, flow_case_set, simulation_config=None, measurements_per_set=200):
        if simulation_config is None:
            simulation_config = {'measurements': {'wind_conditions_inference': 'ReferenceBased'}}
        self._farm_id = farm_id
        self._reference_id = reference_id
        super().__init__(None, flow_case_set)
        self._measurement_set_ids = self.__submit_measurements(measurements_per_set)
        self._simulation_id = wb.run_simulation(simulation_config, self._measurement_set_ids)['id']

    @property
    def farm_id(self):
        return self._farm_id

    @property
    def measurement_set_ids(self):
        return self._measurement_set_ids

    def __submit_measurements(self, measurements_per_set):
        if 'flow_case_id' not in self._flow_case_set:
            self._flow_case_set['flow_case_id'] = generate_flow_case_ids(self._flow_case_set)
        self._flow_case_set = self._flow_case_set.sort_values(by='flow_case_id')
        measurements = []
        set_ids = []
        for index, row in self._flow_case_set.iterrows():
            measurements += create_single_flow_case_measurements(row, self._reference_id)
            if len(measurements) > measurements_per_set:
                set_ids.append(wb.upload_measurement_set(self._farm_id, measurements)['id'])
                measurements.clear()
        if len(measurements) > 0:
            set_ids.append(wb.upload_measurement_set(self._farm_id, measurements)['id'])
        return set_ids


def create_simulation(flow_case_set, dependencies):
    """Creates a WakeBlaster simulation asynchronously

    :param flow_case_set: A pandas DataFrame with column headers corresponding to signal ID's thus determining the flow cases that will be run
    :param dependencies: WakeBlasterDependencies object that contains information on the farm
    :return: WakeBlasterSimulation object
    """
    return WakeBlasterNewSimulation(dependencies.farm_id,
                                    dependencies.reference_id,
                                    flow_case_set,
                                    dependencies.simulation_config)
