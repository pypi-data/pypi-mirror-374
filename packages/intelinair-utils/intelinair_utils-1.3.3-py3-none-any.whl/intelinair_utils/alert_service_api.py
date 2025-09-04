import json
import os
from logging import getLogger
from typing import Optional, Union, Dict, Callable

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from intelinair_utils.agmri_api import AgmriApi
from intelinair_utils.api import Api

logger = getLogger(__name__)

URL = "https://api.{}.intelinair.dev/alerts/api/"
PROD_URL = "https://api.ag-mri.intelinair.com/alerts/api/"
REQUEST_TIMEOUT = 180


class AlertServiceApi(Api):
    """An API for getting alerts from Alert Service."""

    def __init__(self, environment: str, agmri_api: AgmriApi, version_string: str = 'v1/'):
        # version_string == '' corresponds to the first version of API
        self.environment = environment
        self.version_string = version_string
        self.agmri_api = agmri_api
        url = PROD_URL if self.environment == 'prod' else URL.format(self.environment)
        self.url = os.path.join(url, self.version_string)
        self.auth_header = {
            'Content-Type': 'application/json',
            **self.agmri_api.headers["processing"]
        }
        self._session = requests.Session()
        retries = Retry(total=10, read=10, connect=10, backoff_factor=1, allowed_methods=False,
                        status_forcelist=[409] + list(range(500, 600)))
        self._session.mount('https://', HTTPAdapter(max_retries=retries))

    def _make_request(self, method: Callable, path: str, body: Optional[str] = None) -> Dict:
        """
        Makes a request to the Alert Service API of the given method.
        Args:
            method: The method to use for the request.
            path: The path to the endpoint.
            body: The body of the request if POST.
        Returns:
            The response of the request.
        """
        res = method(os.path.join(self.url, path), headers=self.auth_header, timeout=REQUEST_TIMEOUT, data=body)
        if res.status_code == 401:
            self.agmri_api.ensure_authenticated()
            self.auth_header.update(self.agmri_api.headers["processing"])
            res = method(os.path.join(self.url, path), headers=self.auth_header, timeout=REQUEST_TIMEOUT, data=body)
        if res.status_code == 204:
            return dict()
        return res.json()

    def get(self, path: str):
        """
        Performs a GET request to the specified endpoint.
        Args:
            path: The path to the endpoint.
        Returns:
            The json response of the request.
        """
        return self._make_request(self._session.get, path)

    def post(self, path, body: Optional[Union[Dict, str]] = None):
        """
        Performs a POST request to the specified endpoint.
        Args:
            path: The path to the endpoint.
            body: The body of the request.
        Returns:
            The json response of the request.
        """
        if isinstance(body, dict):
            body = json.dumps(body)
        return self._make_request(self._session.post, path, body)

    def delete(self, path: str):
        """
        Performs a DELETE request to the specified endpoint.
        Args:
            path: The path to the endpoint.
        Returns:
            The json response of the request.
        """
        return self._make_request(self._session.delete, path)
