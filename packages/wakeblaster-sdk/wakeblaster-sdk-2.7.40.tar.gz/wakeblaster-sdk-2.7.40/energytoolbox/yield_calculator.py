import numpy as np
import time
from .flow_case_maker import GaussianQuadratureFlowCaseMaker
from .wakeblaster_simulation import create_simulation


def calculate_yield(frequency_matrix, simulation_dependencies,
                    flow_case_maker=GaussianQuadratureFlowCaseMaker(3),
                    output_file_path=None,
                    timeout=None):
    """
    Calculate the annual energy yield of the farm

    :param frequency_matrix: A WindFrequencyMatrix object describing the expected hours per year in each wind speed and direction sector.
    :param simulation_dependencies: A WakeBlasterDependencies object which stores the uploaded farm and config
    :param flow_case_maker: A FlowCaseMaker object which generates a flow case pandas.DataFrame from the frequency_matrix. Default is GaussianQuadratureFlowCaseMaker(3).
    :param output_file_path: If provided, the flow case results are saved to this file path in csv format.
    :param timeout: time-out in seconds until it gives up waiting for results. If none, time-out = 60 x number of flow cases

    :return: Annual energy yield in Watt-hours (Wh)
    """
    flow_case_set = flow_case_maker.make(frequency_matrix)
    simulation = create_simulation(flow_case_set, simulation_dependencies)
    print("Simulation id '{}'".format(simulation.id))

    timeout = timeout or 60 * flow_case_set.shape[0]
    wait = max(timeout/100, 1.0)
    start = time.clock()
    while not simulation.are_results_ready():
        if time.clock() - start > timeout:
            raise RuntimeError('Yield calculation exceeded time-out of ' + str(timeout) + ' seconds')
        time.sleep(wait)

    flow_case_set, _ = simulation.get_results(['farm_power_output'], [])
    if output_file_path is not None:
        flow_case_set.to_csv(output_file_path)
    farm_yield = np.dot(flow_case_set['weighting'], flow_case_set['farm_power_output'])
    return farm_yield
