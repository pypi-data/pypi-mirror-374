import logging
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from intelinair_utils.agmri_api import AgmriApi

logger = logging.getLogger(__name__)


class PipelineStatsApi:
    """API wrapper for pipeline-stats service, which implements get method for imagery and flight objects"""

    REQUEST_TIMEOUT = 180
    PIPELINE_STATS_URLS = {
        "prod": "https://0lnl943boa.execute-api.us-east-1.amazonaws.com/api/v1",
        "bellflower": "https://679l0mrptd.execute-api.us-east-1.amazonaws.com/api/v1",
        "release": "https://2ruql88p6k.execute-api.us-east-1.amazonaws.com/api/v1",
        "platform": "https://vxfckxgsnc.execute-api.us-east-1.amazonaws.com/api/v1"
    }

    def __init__(self, environment: str, config_path: Optional[str] = None):
        """

        Args:
            environment:  the env name
            config_path: the optional path to agmri.cfg, if yoy want to use ssm, use ssm://<ssm param name>
        """
        self.environment = environment
        self.config_path = config_path
        self.session = requests.Session()
        self.url_template = f"{self.PIPELINE_STATS_URLS[self.environment]}"
        self._token = self._get_auth_token()
        retries = Retry(total=10, read=10, connect=10, backoff_factor=1,
                        allowed_methods=False,
                        status_forcelist=[409] + list(range(500, 600)))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def _get_auth_token(self):
        agmri_api = AgmriApi(self.environment, config_path=self.config_path)
        agmri_api.ensure_authenticated()
        token = agmri_api.headers['processing']['X-Auth-Token']
        return token

    def _make_request(self, http_method, *args, **kwargs):
        response = http_method(*args, **kwargs, headers={'x-auth-token': self._token}, timeout=self.REQUEST_TIMEOUT)
        if response.status_code == 401:
            self._token = self._get_auth_token()
            return self._make_request(http_method, *args, **kwargs)
        return response

    def get_flight_stats(self, code, params=None, ignore_json=False):
        """Perform a GET request to the specified endpoint"""
        url = f"{self.url_template}/logs/flight/{code}"
        response = self._make_request(self.session.get, url, params=params)
        if ignore_json:
            return response
        return response.json()

    def get_imagery_stats(self, code, params=None, ignore_json=False):
        """Perform a GET request to the specified endpoint"""
        url = f"{self.url_template}/logs/imagery/{code}"
        response = self._make_request(self.session.get, url, params=params)
        if ignore_json:
            return response
        return response.json()

    def delete_stats(self, code, obj_type):
        """Perform a DELETE request to the specified endpoint"""

        valid_types = ("soil", "elevation", "equipment", "imagery", "flight")

        if obj_type in valid_types:
            url = f"{self.url_template}/logs/{obj_type}/{code}"
            response = self._make_request(self.session.delete, url)
            return response

        logger.warning("Please indicate valid object type")

    def get_stats_version(self, code, pipeline, processing_id, params=None):
        """Get stats version of a pipeline"""
        url = f"{self.url_template}/version/{pipeline}/{code}/{processing_id}"
        response = self._make_request(self.session.get, url, params=params)
        return response.json()
