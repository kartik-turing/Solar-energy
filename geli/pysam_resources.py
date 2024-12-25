import PySAM.ResourceTools as resource_tools


class PySAM_Resources:
    """Base Class to access NREL resources"""

    def __init__(self, nrel_api_key, nrel_api_email):
        self._nrel_api_key = nrel_api_key
        self._nrel_api_email = nrel_api_email

    def get_nrel_api_key(self):
        return self._nrel_api_key

    def get_nrel_api_email(self):
        return self._nrel_api_email

    def _set_technology(self, technology):
        self._technology = technology

    def get_technology(self):
        return self._technology

    def _set_met_data_fetcher(self):
        """Set meteorological data fetcher for the considered technology"""
        self._met_data_fetcher = resource_tools.FetchResourceFiles(
            tech=self.get_technology(),
            nrel_api_key=self.get_nrel_api_key(),
            nrel_api_email=self.get_nrel_api_email(),
        )

    def get_met_data_fetcher(self):
        return self._met_data_fetcher
