from geli.pysam_resources import PySAM_Resources


class PySAM_Solar_Resources(PySAM_Resources):
    """Class to access NREL solar resources through PySAM"""

    def __init__(self, nrel_api_key=None, nrel_api_email=None):
        # sanity checks
        assert all([
            nrel_api_key is not None,
            nrel_api_email is not None,
        ]), "Please supply NREL API key/email"

        # set the technology as solar
        self._set_technology("solar")

        # call base class __init__
        super().__init__(nrel_api_key, nrel_api_email)

        # Set the meteorological data fetcher (National Solar Radiation Database)
        self._set_met_data_fetcher()
        # create an alias to the get_met_data_fetcher base class method
        self.get_nsrdbfetcher = self.get_met_data_fetcher

    def set_resource_file_paths(self):
        self._nsrdb_path_dict = (
            self.get_nsrdbfetcher().resource_file_paths_dict
        )

    def get_resource_file_paths(self):
        return self._nsrdb_path_dict
