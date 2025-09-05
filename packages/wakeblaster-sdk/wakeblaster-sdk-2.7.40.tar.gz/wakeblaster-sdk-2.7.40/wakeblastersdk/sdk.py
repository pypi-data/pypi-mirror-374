import time
from datetime import datetime
import logging
import gzip
from json import dumps as to_json
from xml.etree import ElementTree

import requests  # use the 'requests' library. More info: http://docs.python-requests.org
from requests.exceptions import RequestException, SSLError

_api_base_url = ''
_api_key = ''
_client_id = 'wakeblastersdk-python'

logger = logging.getLogger(__name__)


class WakeBlasterError(Exception):
    def __init__(self, message):
        super().__init__(message)


class WakeBlasterResponseError(WakeBlasterError):
    def __init__(self, action, response):
        message = 'Failed to {}: Error Code: {}, Message: {}'\
            .format(action, response.status_code, response.text)
        super().__init__(message)


def do_request(req, endpoint, tries=5, *args, **kwargs):
    if tries <= 0:
        raise ValueError('tries must be >= 0')
    for i in range(tries):
        try:
            response = req(endpoint, *args, **kwargs)
        except RequestException as exception:
            raise WakeBlasterError(exception)
        if response.status_code == 408:     # timeout
            logger.debug('Timeout (408) on try number %d', i+1)
        elif response.status_code == 429:   # too many requests
            logger.debug('Too many requests (429) on try number %d. Sleeping for 1s', i+1)
            time.sleep(1.0)
        elif response.status_code >= 400:
            logger.debug('Unexpected error (%d) on try number %d. Sleeping for 1s', response.status_code, i+1)
            time.sleep(1.0)
        else:
            return response
    raise WakeBlasterResponseError('connect to perform request at endpoint {} after {} tries'.format(endpoint, tries), response)

def _validate_response(response, expected_status_code, operation, object_id=None):
    if response.status_code == 404:
        if object_id:
            message = '{}: object with ID {} not found'.format(operation, object_id)
        else:
            message = '{}: object not found'.format(operation)
        raise WakeBlasterError(message)
    if response.status_code != expected_status_code:
        raise WakeBlasterResponseError(operation, response)

def set_api_url_and_key(api_key, api_base_url=None):
    """
    Set the URL of the WakeBlaster API and its key that will be used for subsequent API calls.

    :param api_key: Access key for the WakeBlaster API provided to you by the WakeBlaster support team
    :param api_base_url: Base URL of all WakeBlaster HTTP requests. Default is the beta URL.
    """
    global _api_base_url, _api_key
    _api_base_url = api_base_url or 'https://beta.app.wakeblaster.net/api'
    _api_key = api_key

def set_client_id(client_id):
    """
    Set the client ID. This will be stored in the simulations database and is useful for tracking usage.

    :param client_id: The client ID to use.
    """
    global _client_id
    _client_id = client_id

def _standard_headers():
    headers = {'x-api-key': _api_key}
    if _client_id is not None:
        headers['x-client-id'] = _client_id
    return headers

def upload_turbine_design(design_id, wtg_file, tries=5):
    """
    Upload a wind turbine design, overwriting any previous design with the same design_id

    :param design_id: Design identifier.
    :param wtg_file: String contents of .wtg file in WASP established xml format.
    :param tries: Number of times the HTTP request should be tried in case of timeout or 'too many requests'
    """
    logger.debug('Uploading turbine design %s', design_id)
    endpoint = _api_base_url + '/designs/' + design_id
    response = do_request(
        requests.put,
        endpoint,
        tries,
        data=gzip.compress(to_json({'wtg_file': wtg_file}).encode('utf8')),
        headers={**_standard_headers(), 'Content-Type': 'application/json', 'Content-Encoding': 'gzip'}
    )
    _validate_response(response, 201, 'upload turbine design {}'.format(design_id))


def upload_met_mast_design(design_id, met_mast_design, tries=5):
    """
    Upload a met mast design, overwriting any previous design with the same design_id.

    :param design_id: Design identifier.
    :param met_mast_design: Met mast design in the WakeBlaster specified format (see WakeBlaster documentation for format).
    :param tries: Number of times the HTTP request should be tried in case of timeout or 'too many requests'
    """
    logger.debug('Uploading met mast design %s', design_id)
    endpoint = _api_base_url + '/designs/' + design_id
    response = do_request(
        requests.put,
        endpoint,
        tries,
        data=gzip.compress(to_json({'met_mast_design': met_mast_design}).encode('utf8')),
        headers={**_standard_headers(), 'Content-Type': 'application/json', 'Content-Encoding': 'gzip'}
    )
    _validate_response(response, 201, 'upload met mast design {}'.format(design_id))


def get_design(design_id, json=False, tries=5):
    """
    Get either a wind turbine or met mast design
    :param design_id: ID of design
    :param json: False if a turbine design (.wtg files are XML), True if met mast design
    :param tries: Number of times the HTTP request should be tried in case of timeout or 'too many requests'
    :return: design in text format if json=False, else design dict
    """
    logger.debug('Getting design %s', design_id)
    endpoint = _api_base_url + '/designs/' + design_id + '/design'
    response = do_request(requests.get, endpoint, tries, headers=_standard_headers())
    _validate_response(response, 200, 'get design', design_id)
    return response.json() if json else response.text


def upload_asset(asset_id, wind_farm_def, wind_resource_grid_file=None, wind_farm_turbulence=None, associated_wind_speeds=None, regional_roughness=None, tries=5):
    """
    Upload a wind farm definition, overwriting it if a matching asset ID already existed.

    :param asset_id: ID of the asset (wind farm).
    :param wind_farm_def: Wind farm definition in a dict object according to wind farm definition format.
    :param wind_resource_grid_file: (optional) The contents of a WASP format .wrg or .rsf file as a string.
    :param wind_farm_turbulence: (optional) Information for the default wind farm turbulence. See docs
    :param associated_wind_speeds: (optional) Information about the wind speeds associated to each instance. Determines relative wind speeds across the farm. See docs
    :param regional_roughness: (optional) Regional roughness length.
    :param tries: Number of times the HTTP request should be tried in case of timeout or 'too many requests'
    """
    logger.debug('Uploading asset %s', asset_id)
    endpoint = _api_base_url + '/assets/' + asset_id
    body = {'wind_farm_description': wind_farm_def}
    if wind_resource_grid_file:
        body['wind_resource_grid_file'] = wind_resource_grid_file
    if wind_farm_turbulence:
        body['wind_farm_turbulence'] = wind_farm_turbulence
    if associated_wind_speeds:
        body['associated_wind_speeds'] = associated_wind_speeds
    if regional_roughness:
        body['regional_roughness'] = regional_roughness
    response = do_request(
        requests.put,
        endpoint,
        tries,
        data=gzip.compress(to_json(body).encode('utf8')),
        headers={**_standard_headers(), 'Content-Type': 'application/json', 'Content-Encoding': 'gzip'}
    )
    _validate_response(response, 201, 'upload wind farm definition {}'.format(asset_id))


def get_asset(asset_id, tries=5):
    """
    Get the definition for a previously uploaded asset (wind farm)
    :param asset_id: ID of the asset (wind farm).
    :param tries: Number of times the HTTP request should be tried in case of timeout or 'too many requests'
    :return: A dict containing asset items 'wind_farm_description', 'wind_resource_grid_file' and 'wind_farm_turbulence' as per WakeBlaster docs
    """
    logger.debug('Retrieving asset %s', asset_id)
    endpoint = _api_base_url + '/assets/' + asset_id
    response = do_request(requests.get, endpoint, tries, headers=_standard_headers())
    _validate_response(response, 200, 'get asset', asset_id)
    return response.json()


def get_wind_farm_description(asset_id, tries=5):
    """
    Get the wind farm description for a previously uploaded asset (wind farm)
    :param asset_id: ID of the asset (wind farm).
    :param tries: Number of times the HTTP request should be tried in case of timeout or 'too many requests'
    :return: A dict containing the description of a wind farm (turbine instances and met mast instances) as per WakeBlaster docs
    """
    logger.debug('Retrieving wind farm description for asset %s', asset_id)
    endpoint = _api_base_url + '/assets/' + asset_id + '/wind-farm-description'
    response = do_request(requests.get, endpoint, tries, headers=_standard_headers())
    _validate_response(response, 200, 'get wind farm description', asset_id)
    return response.json()


def upload_measurement_set(farm_id, measurements, tries=5):
    """
    Upload a set of measurements for a later simulation. Return measurement set info including the measurement set ID.

    :param farm_id: ID of the wind farm (asset).
    :param measurements: A list of measurements objects, each of which is a dict containing instance_id, signal_id, value and timestamp or flow_case_id
    :param tries: Number of times the HTTP request should be tried in case of timeout or 'too many requests'
    """
    logger.debug('Uploading measurement set with %d measurements at farm \'%s\'', len(measurements), farm_id)
    endpoint = _api_base_url + '/measurement-sets'
    json_body = {'measurements': measurements}
    if farm_id:
        json_body['farm_id'] = farm_id
    response = do_request(
        requests.post,
        endpoint,
        tries,
        data=gzip.compress(to_json(json_body).encode('utf8')),
        headers={**_standard_headers(), 'Content-Type': 'application/json', 'Content-Encoding': 'gzip'}
    )
    _validate_response(response, 201, 'add measurements')
    return response.json()


def run_simulation(simulation_config, measurement_set_ids, farm_id=None, tries=5):
    """
    Run a simulation on a set of previously created measurement sets. Return the simulation info including its ID.

    :param simulation_config: A python dict specifying configuration options for a WakeBlaster simulation (see WakeBlaster documentation for configuration format).
    :param measurement_set_ids: A list of measurement set identifiers (as returned by upload_measurement_set)
    :param tries: Number of times the HTTP request should be tried in case of timeout or 'too many requests'
    """
    logger.debug('Running simulation on %d measurement sets', len(measurement_set_ids))
    endpoint = _api_base_url + '/simulations'
    json_body = {'measurement_set_ids': measurement_set_ids, 'simulation_config': simulation_config}
    if farm_id is not None:
        json_body['farm_id'] = farm_id
    response = do_request(
        requests.post,
        endpoint,
        tries,
        json=json_body,
        headers=_standard_headers()
    )
    _validate_response(response, 201, 'run simulation', response)
    return {**response.json(), 'version': response.headers.get('x-wakeblaster-version')}

def get_measurements(simulation_id, limit=None, tries=5):
    info = get_simulation_info(simulation_id)
    measurement_sets = info["measurement_set_ids"]
    meas = []
    offs = 0

    if limit:
        lim = limit
    else:
        lim = 1000

    for sets in measurement_sets:
        exit_for = False
        while(True):
            endpoint = _api_base_url + "/measurements?set_id=" + sets + "&limit=" + str(lim) + "&offset=" + str(offs)
            response = do_request(requests.get, endpoint, tries, headers=_standard_headers())
            meas += response.json()
            if lim < 1000:
                exit_for = True
                break
            if int(response.headers["X-Count"]) < 1000:
                offs=0
                break
            offs=offs+1000
        if exit_for:
            break

    return meas

def get_simulation_info(simulation_id, tries=5):
    """
    Get information about a simulation including its current execution progress.

    :param simulation_id: Identifier of the simulation (as returned by run_simulation).
    :param tries: Number of times the HTTP request should be tried in case of timeout or 'too many requests'
    """
    logger.debug('Retrieving information for simulation %s', simulation_id)
    endpoint = _api_base_url + '/simulations/' + simulation_id
    response = do_request(requests.get, endpoint, tries, headers=_standard_headers())
    _validate_response(response, 200, 'get simulation {}'.format(simulation_id))
    return response.json()

def get_simulations(submitted_from=None, submitted_to=None, tries=5):
    """
    Get information about simulations, that have been or are running on this environment.

    :param submitted_from: If provided, this is the start timestamp of the period.
    :param submitted_to: If provided, this is the end timestamp of the period.
    :param tries: Number of times the HTTP request should be tried in case of timeout or 'too many requests'
    """
    logger.debug('Retrieving information for simulations')
    params = "?"
    if submitted_from:
        params += "submitted_from=" + submitted_from
    if submitted_to:
        params += "&submitted_to=" + submitted_to
    endpoint = _api_base_url + '/simulations' + params
    response = do_request(requests.get, endpoint, tries, headers=_standard_headers())
    _validate_response(response, 200, 'get simulations')
    return response.json()


def get_results(simulation_id, tries=5, format='json', property=None, batch_limit=1000):
    """
    Meta function to call either get_results_api or get_results_s3, depending on the number of turbines.
    """
    if format not in ['json', 'csv']:
        raise ValueError('Unsupported format: ' + format)
    if format == "csv": # Currently get_results_s3 does not support csv format.
        return get_results_api(simulation_id, tries, format, property, batch_limit)

    measurements = get_measurements(simulation_id, limit=1)
    try:
        asset_id = measurements[0]["farm_id"]
    except:
        logger.debug("Could not get asset_id for simulation %s. Falling back to API mode.", simulation_id)
        return get_results_api(simulation_id, tries, format, property, batch_limit)

    wind_farm_description = get_wind_farm_description(asset_id)

    turbine_count = len(wind_farm_description["turbine_instances"])

    if turbine_count > 500:
        return get_results_s3(simulation_id, tries)
    elif turbine_count <= 500:
        return get_results_api(simulation_id, tries, format, property, batch_limit)
    else:
        logger.debug("Turbine count is invalid for simulation %s.", simulation_id)
    return


def get_results_api(simulation_id, tries=5, format='json', property=None, batch_limit=1000):
    """
    Get results of a simulation. Usually it is advisable to not call this until the result_count has been checked by calling get_simulation_info.

    :param simulation_id: Identifier of the simulation (as returned by run_simulation).
    :param tries: Number of times the HTTP request should be tried in case of timeout or 'too many requests'
    :param format: Format of the results. One of [json|csv]. If csv, the property can be specified. csv format contains instances (columns) against flow cases/timestamps (rows).
    :param property: If format is csv, the property to retrieve. One of [power|unwaked_power|rotor_wind_speed|hub_wind_speed|wake_speed_factor|blockage_speed_factor|air_density|turbulence_intensity]. Defaults to 'power'.
    """
    logger.debug('Retrieving results for simulation %s', simulation_id)
    results_endpoint = 'results' if format == 'json' else 'results-csv'
    endpoint = _api_base_url + '/' + results_endpoint + '?simulation_id=' + simulation_id + ('' if property is None else '&property=' + property)
    headers = {**_standard_headers(), 'Accept-Encoding': 'gzip'}
    head_response = do_request(requests.head, endpoint, tries, headers=headers)
    _validate_response(head_response, 200, 'get results (count)')
    count = head_response.headers.get('x-count')
    if count is None:
        raise WakeBlasterError('Could not get result count')
    try:
        count = int(count)
    except ValueError:
        raise WakeBlasterError('Invalid value returned for result count: "{}"'.format(count))
    offset = 0
    result = [] if format == 'json' else ''
    while offset <= count:
        batch_endpoint = endpoint + '&offset={offset}&limit={limit}'.format(offset=offset, limit=batch_limit)
        response = do_request(requests.get, batch_endpoint, tries, headers=headers)
        _validate_response(response, 200, 'get results (offset {})'.format(offset))
        offset += batch_limit
        if format == 'json':
            result += response.json()
        else:
            if result:
                # Remove header line if header has already been added
                result += '\n'.join(response.text.split('\n')[1:])
            else:
                result += response.text
    return result


def get_results_s3(simulation_id, tries=5):
    """
    Get results of a simulation directly from S3. Usually it is advisable to not call this until the result_count has been checked by calling get_simulation_info.

    :param simulation_id: Identifier of the simulation (as returned by run_simulation).
    """
    logger.debug('Retrieving results for simulation %s', simulation_id)
    urls_endpoint = 'object-urls'
    endpoint = _api_base_url + '/' + urls_endpoint + '/' + simulation_id
    headers = {**_standard_headers(), 'Accept-Encoding': 'gzip'}
    response = do_request(requests.get, endpoint, tries, headers=headers)
    _validate_response(response, 200, 'get results (count)')

    l_res = []
    j_res = response.json()
    
    for i in j_res:
        if i.endswith(".json") and i.find("/results-")>0:
            try: 
                res_file = requests.get(j_res[i]).json()["results"]
            except SSLError:
                """
                Apparently sometimes the requests are too fast, so a retry solves it. 
                """
                res_file = requests.get(j_res[i]).json()["results"]
            l_res.extend(res_file)

    def _formatres(origres):
        origres['turbine_results'] = origres['turbines']
        if origres['met_masts'] == '':
            origres['met_mast_results'] = []
        else:
            origres['met_mast_results'] = origres['met_masts']
        del origres['turbines']
        del origres['met_masts']
        return origres

    results = []
    for origres in l_res:
        results.append(_formatres(origres))

    return results


def retrieve_results(simulation_id, wait=10., number_of_attempts=100, tries_per_request=5, format='json', property=None, partial=True):
    """
    Make repeated queries of the number of results produced and return results once the expected number of results have been produced by the simulation

    :param simulation_id: Identifier of the simulation (as returned by run_simulation).
    :param wait: Time in seconds between each query of simulation info
    :param number_of_attempts: Maximum number of query attempts to make before giving up on retrieving all results.
    :param verbose: if True, print information to screen on each query attempt
    :param tries_per_request: Number of times each HTTP request should be tried in case of timeout or 'too many requests'
    :param format: Format of the results. One of [json|csv]. If csv, the property can be specified. csv format contains instances (columns) against flow cases/timestamps (rows).
    :param property: If format is csv, the property to retrieve. One of [power|unwaked_power|rotor_wind_speed|wake_speed_factor|air_density|turbulence_intensity]. Defaults to 'power'.
    """
    attempts = 0
    while attempts < number_of_attempts:
        simulation_info = get_simulation_info(simulation_id, tries_per_request)
        attempts += 1
        if simulation_info['state'] == 'initialising':
            logger.info('Simulation still initialising after attempt %d of retrieving results', attempts)
            time.sleep(wait)
        elif simulation_info['state'][:5] == 'error':
            raise WakeBlasterError('Simulation {} had an error: {}'.format(simulation_id, simulation_info['state']))
        elif simulation_info['result_count'] + simulation_info['error_count'] == simulation_info['flow_case_count']:
            if simulation_info['error_count'] > 0:
                logger.warning('%d result(s) in simulation %s have errors',
                               simulation_info['error_count'], simulation_id)
            logger.info('Retrieved all %d result(s)', simulation_info['flow_case_count'])
            return get_results(simulation_id, tries_per_request, format=format, property=property)
        else:
            logger.info('Retrieved %d/%d result(s) after %d attempts',
                        simulation_info['result_count'], simulation_info['flow_case_count'], attempts)
            time.sleep(wait)
    logger.info('Failed to retrieve all results for simulation %s', simulation_id)
    if partial:
        return get_results(simulation_id, tries_per_request, format=format, property=property)
    else:
        return None


def get_error_messages(simulation_id, measurement_set_id=None, tries=5, batch_limit=1000):
    """
    Get all error messages for a simulation
    :param simulation_id: Identifier of the simulation (as returned by run_simulation).
    :param measurement_set_id: (optional) Identifier for the measurement set. This can be used for further filtering
    :param tries: Number of times the HTTP request should be tried in case of timeout or 'too many requests'
    :return: list of dicts containing error messages and their corresponding simulation and measurements set ID's
    """
    logger.debug('Retrieving error messages for simulation %s', simulation_id)
    query = '?simulation_id=' + simulation_id
    if measurement_set_id:
        query += '&measurement_set_id=' + measurement_set_id
    endpoint = _api_base_url + '/errors' + query
    headers = {**_standard_headers(), 'Accept-Encoding': 'gzip'}
    head_response = do_request(requests.head, endpoint, tries, headers=headers)
    _validate_response(head_response, 200, 'get error messages for simulation {} (count)'.format(simulation_id))
    count = head_response.headers.get('x-count')
    if count is None:
        raise WakeBlasterError('Could not get error count')
    try:
        count = int(count)
    except ValueError:
        raise WakeBlasterError('Invalid value returned for error count: "{}"'.format(count))
    offset = 0
    result = []
    while offset <= count:
        batch_endpoint = endpoint + '&offset={offset}&limit={limit}'.format(offset=offset, limit=batch_limit)
        response = do_request(requests.get, batch_endpoint, tries, headers=headers)
        _validate_response(response, 200, 'get error messages for simulation {}'.format(simulation_id))
        offset += batch_limit
        result += response.json()
    return result


def usage_stats():
    """
    Get usage statistics
    :return: dict containing list of period statistics, with the format {'periods': [{'period': 'YYYYMM', 'flow_case_count': count, 'max_flow_case_count': max}]}
    :rtype: dict
    """
    response = do_request(requests.get, _api_base_url + '/stats', headers={**_standard_headers(), 'Accept-Encoding': 'gzip'})
    _validate_response(response, 200, 'usage stats')
    return response.json()

def usage_stats_for_period(period=None):
    """
    Get usage statistics
    :return: dict containing single period statistics, with the format {'period': 'YYYYMM', 'flow_case_count': count, 'max_flow_case_count': max}
    :rtype: dict
    """
    period = period or datetime.now().strftime('%Y%m')
    response = do_request(requests.get, _api_base_url + '/stats/' + period, headers={**_standard_headers(), 'Accept-Encoding': 'gzip'})
    _validate_response(response, 200, 'usage stats for period')
    return response.json()

def remaining_flow_cases(period=None):
    stats = usage_stats_for_period(period)
    return stats['max_flow_case_count'] - stats['flow_case_count']

def csv_to_dict(csv_text, property=None):
    """
    Converts csv text to WakeBlaster results-format struct
    :param csv_text: The CSV to convert
    :param property: The property contains in the csv-formatted data. One of [power|unwaked_power|rotor_wind_speed|wake_speed_factor|air_density|turbulence_intensity]. Defaults to 'power'.
    :return: WakeBlaster results-formatted struct (same as returned from get_results with json format)
    """
    property = property or 'power'
    lines = csv_text.split('\n')
    if not lines:
        raise ValueError('Could not convert csv_text (incorrect format)')
    header_values = lines[0].split(',')
    id_type = header_values[0]
    instance_ids = header_values[1:]
    results = []
    for line in lines[1:]:
        if not line:
            continue
        values = line.split(',')
        results.append({
            id_type: values[0],
            'turbine_results': [{property: v, 'instance_id': i} for v, i in zip(values[1:], instance_ids)]
        })
    return results

def flow_cases_in_period():
    """Returns the number of flow cases completed in a period

    :returns: The number of flow cases completed in this period
    :rtype: int
    """
    response = do_request(requests.head, _api_base_url + '/simulations?current_period=true', headers={**_standard_headers(), 'Accept-Encoding': 'gzip'})
    _validate_response(response, 200, 'simulations in period')
    count = response.headers.get('x-flow-case-count')
    if count is None:
        raise WakeBlasterError('Could not get flow case count')
    try:
        count = int(count)
    except (ValueError, TypeError):
        raise WakeBlasterError('Invalid value returned for flow case count: "{}"'.format(count))
    return count

def download_flow_plane(simulation_id, target_path):
    """
    Downloads the flow plane for the simulation id provided, if it exists.
    :param simulation_id: The simulation id
    :param target_path: The path to download the file to
    :param region: Optionally provide the region in which the s3 bucket resides. Generally not necessary.
    """
    response = do_request(requests.get, _api_base_url + '/flow-plane/' + simulation_id, headers={**_standard_headers(), 'Accept-Encoding': 'gzip'}, allow_redirects=False)
    _validate_response(response, 302, 'download flow plane')
    redirect_location = response.headers['Location']

    def _download_part(written=0, chunk_size=2**20):
        try:
            with requests.get(redirect_location, stream=True, headers={'Range': 'bytes={}-'.format(written)}, timeout=1) as r:
                r.raise_for_status()
                with open(target_path, 'wb' if written == 0 else 'ab') as f:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        if chunk:
                            written += chunk_size
                            f.write(chunk)
                            f.flush()
                    return -1
        except:
            return written

    attempts = 0
    written = 0
    while attempts < 20:
        written = _download_part(written)
        if written == -1:
            break
        attempts += 1
    else:
        raise WakeBlasterError('Could not download flow plane for simulation {}'.format(simulation_id))

def download_surfer_grid(simulation_id, height, target_path):
    """
    Get a surfer grid
    :param: simulation_id
    :param: height
    :param: target_path
    :return: string, containing a surfer grid file
    :rtype: str
    """
    response = do_request(requests.get, _api_base_url + '/flow-plane/' + simulation_id + "?format=surfer&height=" + str(height), headers={**_standard_headers(), 'Accept-Encoding': 'gzip'})
    _validate_response(response, 200, 'surfer grid for flow plane log')
    try:
        with open(target_path, "w") as fp:
            fp.write(response.text)
    except OSError as ex:
        raise WakeBlasterError('Could not write downloaded surfer grid to {}: {}'.format(target_path, ex))

def get_version():
    """
    Get WakeBlaster version
    :return: string of the WakeBlaster version
    :rtype: str
    """
    response = requests.get(_api_base_url, headers={**_standard_headers(), 'Accept-Encoding': 'gzip'})
    return response.headers['X-Wakeblaster-Version']

