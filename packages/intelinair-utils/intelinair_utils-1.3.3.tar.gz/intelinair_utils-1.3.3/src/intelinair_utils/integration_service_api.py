"""Integration service API wrapper class."""

from typing import Union, Optional
from uuid import UUID

from intelinair_utils.api_wrapper import ApiWrapper


class IntegrationServiceApi(ApiWrapper):
    """Integration service API Wrapper."""
    INTEGRATION_SERVICE_URLS = {
        "longview": "https://api.longview.intelinair.dev/integration/leaf/operation",
        "release": "https://api.release.intelinair.dev/integration/leaf/operation",
        "prod": "https://api.ag-mri.intelinair.com/integration/leaf/operation"
    }

    def __init__(self, environment: str, config_path: Optional[str] = None):
        super().__init__(environment, self._get_api_urls(), config_path=config_path)

    def _get_api_urls(self):
        """Overridden method for getting integration service API URLs."""
        return self.INTEGRATION_SERVICE_URLS

    def get_operation_units(self, operation_id: Union[str, UUID]) -> dict:
        """
        Getting operation units from leaf integration.
        Args:
            operation_id: UUID of operation to get units for.
        """
        url = self.url_template.format("unit")
        url_params = {
            "operationId": operation_id
        }
        response = self._make_request(self.session.get, url, params=url_params)
        response.raise_for_status()
        return response.json()
