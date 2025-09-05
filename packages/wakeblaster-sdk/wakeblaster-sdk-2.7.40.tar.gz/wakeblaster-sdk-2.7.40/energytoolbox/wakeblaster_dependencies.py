import json
import wakeblastersdk as wb


class WindFarm:
    """
    Holder for information relating to a WakeBlaster wind farm (a.k.a asset)
    
    :param farm_description: wind farm description - see WakeBlaster docs
    :param wind_resource_grid: Contents of a WASP style .wrg or .rsf file
    :param farm_turbulence: wind farm default turbulence - see WakeBlaster docs
    :param associated_WS: associateded wind speed, speedups between different points - see WakeBlaster docs
    :param regional_roughness: regional roughness length - see WakeBlaster docs
    """
    def __init__(self, farm_description, wind_resource_grid=None, farm_turbulence=None, associated_WS=None, regional_roughness=None):
        self._description = farm_description
        self._resource_grid = wind_resource_grid
        self._turbulence = farm_turbulence
        self._associated_WS = associated_WS
        self._regional_roughness = regional_roughness
        
    @classmethod
    def from_file(cls, farm_file_path_json, wind_resource_grid_file_path=None, farm_turbulence_file_json=None, regional_roughness_file_json=None):
        """
        Create WakeBlaster wind farm from file paths

        :param farm_file_path_json: JSON file describing the wind farm - see WakeBlaster docs
        :param wind_resource_grid_file_path: Path to WASP style .wrg or .rsf file
        :param farm_turbulence_file_json: JSON file describing wind farm turbulence - see WakeBlaster docs
        :param regional_roughness_file_json: JSON file describing regional roughness - see WakeBlaster docs
        """
        with open(farm_file_path_json, 'r') as fp:
            farm_description = json.load(fp)
        wind_resource_grid = None
        if wind_resource_grid_file_path:
            with open(wind_resource_grid_file_path, 'r') as fp:
                wind_resource_grid = fp.read()
        farm_turbulence = None
        if farm_turbulence_file_json:
            with open(farm_turbulence_file_json, 'r') as fp:
                farm_turbulence = json.load(fp)
        regional_roughness = None
        if regional_roughness_file_json:
            with open(regional_roughness_file_json, 'r') as fp:
                regional_roughness = json.load(fp)
        return cls(farm_description=farm_description, wind_resource_grid=wind_resource_grid, farm_turbulence=farm_turbulence, regional_roughness=regional_roughness)

    def get_reference_id(self):
        def has(key):
            return key in self._description and len(self._description[key]) > 0

        if has('met_mast_instances'):
            return self._description['met_mast_instances'][0]['id']
        elif has('turbine_instances'):
            return self._description['turbine_instances'][0]['id']
        else:
            raise RuntimeError('No met mast or turbine instances in farm')

    @property
    def description(self):
        return self._description

    @property
    def resource_grid(self):
        return self._resource_grid

    @property
    def turbulence(self):
        return self._turbulence

    @property
    def associated_WS(self):
        return self._associated_WS

    @property
    def regional_roughness(self):
        return self._regional_roughness


class WakeBlasterDependencies:
    """
    Portal for dependencies of a WakeBlaster simulation: Loads designs and farms into the WakeBlaster repository.

    :param api_key: You unique WakeBlaster API key
    :param api_url: URL of WakeBlaster API
    :param simulation_config: Parameters for simulation. See WakeBlaster docs
    """
    def __init__(self, api_key, api_url=None, simulation_config=None):
        if api_url:
            wb.set_api_url_and_key(api_key, api_url)
        else:
            wb.set_api_url_and_key(api_key)
        self._simulation_config = {} if simulation_config is None else simulation_config
        self._farm_id = None
        self._farm_def = None
        self._reference_id = None

    @staticmethod
    def load_turbine_design(design_id, wtg_file_path):
        """Load a wind turbine design into the WakeBlaster repository

        :param design_id: Identifier to be used for this design. Must match contents of wind farm definition fields
        :param wtg_file_path: Path of a WASP-style .wtg file
        """
        with open(wtg_file_path, 'r') as fp:
            wtg_contents = fp.read()
        wb.upload_turbine_design(design_id, wtg_contents)

    @staticmethod
    def load_mast_design(design_id, mast_file_path):
        """Load a met mast design into the WakeBlaster repository

        :param design_id: Identifier to be used for this design. Must match contents of wind farm definition fields
        :param mast_file_path: Path to WakeBlaster style JSON met mast design file
        """
        with open(mast_file_path, 'r') as fp:
            mast_design = json.load(fp)
        wb.upload_met_mast_design(design_id, mast_design)

    def set_farm(self, farm_id, wind_farm, reference_id=None, upload=True):
        """Set the current farm (a.k.a asset) that's being worked on

        :param farm_id: Identifier
        :param wind_farm: WindFarm object
        :param reference_id: Identifier of the turbine in the farm that should be used as the reference location for wind speeds. If 'None', it will use any location in the wind farm (which is irrelevant if there are no terrain effects)
        :param upload: If True (default), the wind farm will be uploaded to the WakeBlaster app. Setting upload=False can save time if the farm and its designs have previously been uplaoded
        :param associated_WS: Speed-ups between the reference point and the turbines
        """
        self._farm_id = farm_id
        self._reference_id = wind_farm.get_reference_id() if reference_id is None else reference_id
        if upload:
            wb.upload_asset(farm_id, wind_farm.description, wind_farm.resource_grid, wind_farm.turbulence, associated_wind_speeds=wind_farm.associated_WS, regional_roughness=wind_farm.regional_roughness)

    @property
    def simulation_config(self):
        return self._simulation_config

    @property
    def farm_id(self):
        if self._farm_id is None:
            raise wb.WakeBlasterError('Farm ID has not been set in WakeBlasterDependencies')
        return self._farm_id

    @property
    def reference_id(self):
        if self._reference_id is None:
            raise wb.WakeBlasterError(
                'ID of the reference instance in the farm has not been determined in WakeBlasterDependencies')
        return self._reference_id
