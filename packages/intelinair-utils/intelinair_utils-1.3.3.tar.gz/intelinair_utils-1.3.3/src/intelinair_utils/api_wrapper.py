"""API wrapper parent class for our microservices."""
import json
import logging
import os
import tempfile
from abc import ABC, abstractmethod
from typing import Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from intelinair_utils.agmri_api import AgmriApi
from intelinair_utils.s3_utils import delete_s3_file, upload_s3_file

logger = logging.getLogger("api_wrapper")


class ApiWrapper(ABC):  # pylint: disable=too-few-public-methods
    """Parent class for our internal API wrapper clients."""
    REQUEST_TIMEOUT = 180
    MAX_UPLOAD_SIZE = 5000000  # ~5MB

    @abstractmethod
    def _get_api_urls(self):
        """Abstract method to ensure child classes had proper setup for API gateway urls."""
        return

    def get_s3_cache_paths(self) -> Dict[str, str]:
        """Return a dictionary of s3 cache paths for each environment supported."""
        return {}

    def __init__(self, environment: str, api_urls: dict, config_path: Optional[str] = None):
        """
        Args:
            environment: the env name
            api_urls: dict of url where the keys are env names and values are urls for making requests
            config_path: the optional path to agmri.cfg, if yoy want to use ssm, use ssm://<ssm param name>
        """
        self.environment = environment
        self.config_path = config_path
        self.session = requests.Session()
        self.url_template = f"{api_urls[self.environment]}/{{}}"
        self.s3_cache_path = self.get_s3_cache_paths().get(self.environment, None)
        self._token = self._get_auth_token()
        retries = Retry(
            total=10,
            read=10,
            connect=10,
            backoff_factor=1,
            allowed_methods=False,
            status_forcelist=[409] + list(range(500, 600))
        )
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def _get_auth_token(self):
        agmri_api = AgmriApi(self.environment, config_path=self.config_path)
        agmri_api.ensure_authenticated()
        token = agmri_api.headers['processing']['X-Auth-Token']
        return token

    def _make_request(self, http_method, *args, attempt_authentication=True, headers=None, **kwargs):
        if not headers:
            headers = {}

        headers['x-auth-token'] = self._token
        response = http_method(*args, **kwargs, headers=headers, timeout=self.REQUEST_TIMEOUT)
        status_code = response.status_code

        if status_code == 401 and attempt_authentication:
            self._token = self._get_auth_token()
            return self._make_request(http_method, *args, attempt_authentication=False, headers=headers, **kwargs)

        return response

    def _upload_data_to_s3(self, json_data):
        with tempfile.NamedTemporaryFile('w', suffix='.json') as tmp_file:
            json.dump(json_data, tmp_file)
            tmp_file.flush()
            tmp_filename = os.path.basename(tmp_file.name)
            upload_s3_file(tmp_file.name, f'{self.s3_cache_path}/{tmp_filename}')
            return tmp_filename

    def _safe_delete_s3_file(self, filename):
        try:
            delete_s3_file(f'{self.s3_cache_path}/{filename}')
        except Exception as err:  # pylint: disable=broad-exception-caught
            logger.error(f'Unable to delete file {filename} from S3: {err}')

    def _make_large_body_request(self, http_method, *args, **kwargs):
        if self.s3_cache_path is not None and 'json' in kwargs:
            large_data_len = len(json.dumps(kwargs['json']))
            logger.debug(f'{self.__class__.__name__} request data length: {large_data_len:,}')
            if large_data_len > self.MAX_UPLOAD_SIZE:
                filename = self._upload_data_to_s3(kwargs['json'])
                try:
                    kwargs['json'] = {}
                    headers = kwargs.pop('headers', {})
                    headers['x-s3-request-body'] = f'{self.s3_cache_path}/{filename}'
                    response = self._make_request(http_method, headers=headers, *args, **kwargs)
                    return response
                finally:
                    self._safe_delete_s3_file(f'{self.s3_cache_path}/{filename}')
        response = self._make_request(http_method, *args, **kwargs)
        return response

    def _custom_chunked_get(self, *args, **kwargs):
        headers = kwargs.pop('headers', {})
        headers['x-chunked-output-byte'] = "0"
        chunks = []
        while True:
            response = self._make_request(self.session.get, *args, headers=headers, **kwargs)
            response.raise_for_status()
            chunks.append(response)
            if 'x-chunked-output-next-byte' in response.headers:
                headers['x-chunked-output-byte'] = response.headers['x-chunked-output-next-byte']
            else:
                break
        concatenated = ''.join([chunk.text for chunk in chunks])
        return json.loads(concatenated)
