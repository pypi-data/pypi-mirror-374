"""Flight service API client."""

import logging
import urllib.parse
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from intelinair_utils.agmri_api import AgmriApi

# types:
AERIAL = 'aerial'
EQUIPMENT = 'equipment'
IMAGERY = 'imagery'

logger = logging.getLogger(__name__)


class FlightServiceApi:
    """API wrapper for flight service."""

    REQUEST_TIMEOUT = 180
    FLIGHT_SERVICE_URLS = {
        "ivesdale": "https://zt2rsi1flf.execute-api.us-east-1.amazonaws.com/api",
        "thomasboro": "https://ukfq5winf5.execute-api.us-east-1.amazonaws.com/api"
    }

    def __init__(self, environment: str, agmri_api: Optional[AgmriApi] = None, config_path: Optional[str] = None):
        """

        Args:
            environment: the env name
            agmri_api: initialized AgmriApi object
            config_path:  the optional path to agmri.cfg, if yoy want to use ssm, use ssm://<ssm param name>
        """
        self.environment = environment
        self.session = requests.Session()
        self.url_template = f"{self.FLIGHT_SERVICE_URLS[self.environment]}/{{}}"
        self._token = self._get_auth_token(agmri_api, config_path)
        self._headers = {
            'x-auth-token': self._token
        }
        retries = Retry(total=10, read=10, connect=10, backoff_factor=1,
                        allowed_methods=False,
                        status_forcelist=[409] + list(range(500, 600)))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def _get_auth_token(self, agmri_api: Optional[AgmriApi] = None, config_path: Optional[str] = None):
        if agmri_api is None:
            agmri_api = AgmriApi(self.environment, config_path=config_path)
        agmri_api.login()
        token = agmri_api.headers['processing']['X-Auth-Token']
        return token

    def _make_request(self, http_method, *args, ignore_json=False, **kwargs):
        response = http_method(*args, **kwargs, headers=self._headers, timeout=self.REQUEST_TIMEOUT)
        return response if ignore_json else response.json()

    def get_flight(self, flight_code: str, flight_type: str) -> dict:
        """
        Getting flight object.
        Args:
            flight_code: unique flight code.
            flight_type: either equipment or aerial.
        """
        url = self.url_template.format(f"flights/{flight_type}/{flight_code}")
        response = self._make_request(self.session.get, url)
        return response

    def create_flight(self, flight_type: str, flight_data: dict) -> dict:
        """
        Creates flight object with values passed through flight_data.
        Args:
            flight_type: either equipment or aerial.
            flight_data: properties of flight object to create.
        Returns:
            Created flight object.
        """
        url = self.url_template.format(f"flights/{flight_type}/create")
        response = self._make_request(self.session.post, url, json=flight_data)
        return response

    def update_flight(self, flight_type: str, flight_code: str, flight_data: dict):
        """
        Update flight object.
        Args:
            flight_type: either equipment or aerial.
            flight_code: code of flight to change.
            flight_data: key-values of properties that will be changed.
        """
        url = self.url_template.format(f"flights/{flight_type}/{flight_code}/update")
        responce = self._make_request(self.session.post, url, json=flight_data)
        return responce

    def delete_flight(self, flight_type: str, flight_code: str):
        """
        Delete flight by code.
        Args:
            flight_type: either equipment or aerial.
            flight_code: code of flight to delete.
        """
        url = self.url_template.format(f"flights/{flight_type}/{flight_code}")
        self._make_request(self.session.delete, url, ignore_json=True)

    def add_flight_tags(self, flight_type: str, flight_code: str, tags: list):
        """
        Add flight tags
        Args:
            flight_type: either equipment or aerial.
            flight_code: code of flight to change.
            tags: list of tags to add
        Returns:
            list of tags after updates
        """
        url = self.url_template.format(f"flights/{flight_type}/{flight_code}/addTags")
        self._make_request(self.session.post, url, json=tags)

    def remove_flight_tags(self, flight_type: str, flight_code: str, tags: list):
        """
        Remove flight tags
        Args:
            flight_type: either equipment or aerial.
            flight_code: code of flight to change.
            tags: list of tags to Remove
        Returns:
            list of tags after updates
        """
        url = self.url_template.format(f"flights/{flight_type}/{flight_code}/removeTags")
        self._make_request(self.session.post, url, json=tags)

    def report_flights(self, flight_type, filters: dict):
        """
        Report flights based on input filters.
        Args:
            flight_type: either equipment or aerial.
            filters: key values, based on which flights will be reported.
                     additional ones are date_to, date_from, offset, limit
        Returns:
            list of flights reported by given filters.
        """
        query_params = urllib.parse.urlencode(filters)
        url = self.url_template.format(f"flights/report/{flight_type}?{query_params}")
        response = self._make_request(self.session.get, url)
        return response

    def get_imagery(self, imagery_code: str) -> dict:
        """
        Getting imagery object.
        Args:
            imagery_code: unique imagery code.
        """
        url = self.url_template.format(f"imageries/{imagery_code}")
        response = self._make_request(self.session.get, url)
        return response

    def create_imagery(self, imagery_data: dict) -> dict:
        """
        Creates imagery object with values passed through imagery_data.
        Args:
            imagery_data: properties of imagery object to create.
        Returns:
            Created imagery object.
        """
        url = self.url_template.format("imageries/create")
        response = self._make_request(self.session.post, url, json=imagery_data)
        return response

    def update_imagery(self, imagery_code: str, imagery_data: dict):
        """
        Update imagery object properties.
        Args:
            imagery_code: code of imagery to be changed.
            imagery_data: key-values of properties that will be changed.
        """
        url = self.url_template.format(f"imageries/{imagery_code}/update")
        response = self._make_request(self.session.post, url, json=imagery_data)
        return response

    def delete_imagery(self, imagery_code: str):
        """
        Delete imagery by code.
        Args:
            imagery_code: code of imagery to delete.
        """
        url = self.url_template.format(f"imageries/{imagery_code}")
        self._make_request(self.session.delete, url, ignore_json=True)

    def get_tileset(self, tileset_type: str, code: str) -> dict:
        """
        Getting tileset object.
        Args:
            tileset_type: either equipment, aerial or imagery.
            code: flight/imagery object code for which tileset is returned.
        """
        url = self.url_template.format(f"tilesets/{tileset_type}/{code}")
        response = self._make_request(self.session.get, url)
        return response

    def create_tileset(self, tileset_type: str, code: str, tileset_data: dict) -> dict:
        """
        Creates tileset object with values passed through tileset_data.
        Args:
            tileset_type: either equipment, aerial or imagery.
            code: flight/imagery object code for which tileset is created.
            tileset_data: properties of tileset object to create.
        Returns:
            Created tileset object.
        """
        url = self.url_template.format(f"tilesets/{tileset_type}/{code}/create")
        response = self._make_request(self.session.post, url, json=tileset_data)
        return response

    def update_tileset(self, tileset_id: str, tileset_data: dict):
        """
        Update tileset object properties.
        Args:
            tileset_id: ID of tileset to be changed.
            tileset_data: key-values of properties that will be changed.
        """
        url = self.url_template.format(f"/tilesets/update/{tileset_id}")
        response = self._make_request(self.session.post, url, json=tileset_data)
        return response

    def delete_tileset(self, tileset_id: int):
        """
        Delete tileset by ID.
        Args:
            tileset_id: ID of tileset to delete.
        """
        url = self.url_template.format(f"tilesets/delete/{tileset_id}")
        self._make_request(self.session.delete, url, ignore_json=True)
