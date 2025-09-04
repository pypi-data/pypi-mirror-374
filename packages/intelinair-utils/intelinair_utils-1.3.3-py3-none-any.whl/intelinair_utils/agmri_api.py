"""
This library provides an interface to the REST API exposed by Ag-MRI.

This library acts as a thin authentication library for the Requests library.
When performing any requests that library documentation should be referenced.

Admin credentials are pulled from the ~/.agmri.cfg file. This file is in the
.ini file format, which is documented here: https://docs.python.org/3.5/library/configparser.html
It should contain a section for each environment with an admin_username and
admin_password value within it.

Example:
```ini
[release]
admin_username = EMAIL
admin_password = PASSWORD

[prod]
admin_username = EMAIL
admin_password = PASSWORD
```

The section headers should match the value that is specified when
initializing the Api() class. An example:

```python
from commons.agmri_api import Api

api = Api("prod")  # This will work with the above cfg file
api = Api("preprod")  # So will this
api = Api("testing")  # This will fail because it's missing from the cfg file
```

"""

import configparser
import logging
import os
from string import Template
from typing import Optional, Tuple, Union, Any, List
from urllib.parse import urlparse

import deprecation
import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError
from urllib3.util.retry import Retry

import intelinair_utils.token_store as token_stores
from intelinair_utils.api import Api
from intelinair_utils.api_utils import validate_date
from intelinair_utils.ssm_utils import get_parameter_from_ssm
from intelinair_utils.token_store import TokenPair

REQUEST_TIMEOUT = 180
RETRIES = 7

logger = logging.getLogger(__name__)


class AgmriApi(Api):
    """
    Wrapper class for authenticated queries against Ag-MRI.

    After initialization, authentication has been completed and requests
    through this object will be automatically authenticated. Only GET,
    POST and PATCH are supported right now.

    URL-resolution precedence (backward compatible):

      1. `api_url` in config → used directly.
      2. `url_template` in config → formatted with {environment}.
      3. Legacy logic:
         • prod  → hard-coded PROD URL
         • other → legacy URL_TEMPLATE

      If both `api_url` and `url_template` are present, `api_url` wins and
      a single warning is logged.
      """

    MAIN_PROD_URL = "https://api.ag-mri.intelinair.com/admin/api/"
    URL_TEMPLATE = "https://api.{}.intelinair.dev/admin/api/"

    def __init__(self, environment: str, config_path: str = None, version_string: str = 'v2/'):
        # version_string == '' corresponds to the first version of API
        if not version_string.endswith('/'):
            raise ValueError(f"all calls (other than login) should use the version string: {version_string}")

        self.environment = environment
        self._config_path = config_path

        self.tokens: TokenPair | None = None
        self._config: configparser.ConfigParser | None = None
        self._token_store = None

        self.api_url = self._resolve_api_url()
        self.api_version_url = self.api_url + version_string
        self.url_template = f"{self.api_version_url}{{}}"

        self.session = requests.Session()
        retries = Retry(
            total=10, read=10, connect=10, backoff_factor=1,
            allowed_methods=False, status_forcelist=[409] + list(range(500, 600))
        )
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

        self.headers = {
            'processing': {'X-Processing': 'true'},
            'graphql': {'Content-Type': 'application/graphql'},
            'refresh': {'Content-Type': 'application/x-www-form-urlencoded'}
        }

    @property
    def config(self) -> configparser.ConfigParser:
        if self._config is None:
            self._config = configparser.ConfigParser()
            self._config['DEFAULT']['token_store'] = 'FileStore'

            if self._config_path is not None:
                parsed_path = urlparse(self._config_path)
                if parsed_path.scheme == "file":
                    self._config.read(parsed_path.path)
                elif parsed_path.scheme == "ssm":
                    config_content = get_parameter_from_ssm(parsed_path.path)
                    self._config.read_string(config_content)
                else:
                    raise Exception("Not supported configuration format. Please use file:// or ssm://")
            else:
                # checking the env variable for config content
                if "AGMRI_API_CONFIG" in os.environ:
                    self._config.read_string(os.environ['AGMRI_API_CONFIG'])
                else:
                    self._config.read(os.path.expanduser("~/.agmri.cfg"))

            if not self._config.has_section(self.environment):
                raise Exception("Missing settings for {} environment in".format(self.environment))
        return self._config

        if not cfg.has_section(self.environment):
            raise KeyError(
                f"Config missing section [{self.environment}]"
            )

        self._config = cfg
        return cfg

    def _resolve_api_url(self) -> str:
        """
        Resolve the base API URL for the chosen environment.

        Precedence:
          1. [env].api_url       – exact value
          2. [env].url_template  – formatted with {environment} or {env},
                                   e.g. https://api-{environment}.newdomain.com/admin/api/
                                        https://api-{env}.newdomain.com/admin/api/
          3. Legacy paths        – prod constant or URL_TEMPLATE

        Always returns a URL ending with exactly one “/”.
        """

        cfg = self.config
        def _with_slash(url: str) -> str:
            """Ensure one (and only one) trailing slash."""
            url = url.strip()
            return url if url.endswith("/") else url + "/"

        def _safe_get(option: str) -> str:
            """Return stripped option value or '' if missing / error / not str."""
            try:
                val = cfg.get(self.environment, option)
            except Exception:
                return ""
            return val.strip() if isinstance(val, str) else ""

        api_raw = _safe_get("api_url")
        tpl_raw = _safe_get("url_template")

        if api_raw:
            if tpl_raw:
                logger.warning(
                    "Both 'api_url' and 'url_template' found for '%s'; using 'api_url'.",
                    self.environment,
                )
            final = _with_slash(api_raw)
            logger.info("API URL via api_url: %s", final)
            return final

        if tpl_raw:
            try:
                rendered = tpl_raw.format(environment=self.environment, env=self.environment)
            except Exception as exc:
                logger.error(
                    "Invalid url_template for '%s' (%s): %s",
                    self.environment, tpl_raw, exc
                )
                raise
            final = _with_slash(rendered)
            logger.info("API URL via url_template: %s", final)
            return final

        if self.environment == "prod":
            final = _with_slash(self.MAIN_PROD_URL)
            logger.info("API URL via legacy PROD constant: %s", final)
            return final

        try:
            final = _with_slash(self.URL_TEMPLATE.format(self.environment))
        except Exception as exc:
            logger.error("Failed to resolve legacy URL for '%s': %s", self.environment, exc)
            raise
        logger.info("API URL via legacy template: %s", final)
        return final

    @property
    def user(self) -> dict:
        return {
            'username': self.config.get(self.environment, 'admin_username'),
            'password': self.config.get(self.environment, 'admin_password')
        }

    @property
    def token_store(self) -> Union[token_stores.SSMStore, token_stores.FileStore]:
        if self._token_store is None:
            driver = self.config.get(self.environment, 'token_store')
            self._token_store = getattr(token_stores, driver)(self.environment, self.user['username'])
        return self._token_store

    def login(self) -> None:
        # login URL does not use version url. it's always /api/login
        logger.info(f'Logging in to {self.api_url} with username={self.user["username"]}')
        auth_response = self.make_request(
            self.session.post,
            self.api_url + "login",
            json=self.user,
            ignore_json=False,
            attempt_authentication=False
        )
        if auth_response is not None:
            self.tokens = TokenPair(
                access_token=auth_response['access_token'],
                refresh_token=auth_response['refresh_token']
            )
            self.headers['processing']['X-Auth-Token'] = auth_response['access_token']
        else:
            raise Exception("Failed to login into ag-mri")

    def token_is_valid(self) -> bool:
        if self.tokens is None or not self.tokens.access_token:
            return False

        url = os.path.join(self.api_url, "validate")
        try:
            res = self.make_request(
                self.session.post,
                url,
                headers={'X-Auth-Token': self.tokens.access_token},
                ignore_json=True,
                attempt_authentication=False
            )
        except HTTPError as e:
            logger.debug(f'token not valid with exception {e}')
            return False
        else:
            if res.status_code == 200:
                return True
            else:
                return False

    def refresh_token(self) -> None:
        url = self.api_url.replace("api/", "oauth/access_token")
        params = {
            'grant_type': 'refresh_token',
            'refresh_token': self.tokens.refresh_token
        }
        res = self.make_request(
            self.session.post,
            url,
            params=params,
            headers=self.headers['refresh'],
            attempt_authentication=False
        )
        self.tokens = TokenPair(access_token=res['access_token'], refresh_token=res['refresh_token'])
        self.headers['processing']['X-Auth-Token'] = res['access_token']

    def ensure_authenticated(self) -> None:
        """This is the main method that ensures that the api is connected."""
        if self.token_is_valid():
            return

        try:
            self.tokens = self.token_store.get_tokens()
            if self.token_is_valid():
                self.headers['processing']['X-Auth-Token'] = self.tokens.access_token
                return
        except Exception as e:
            logger.debug(f'failed to fetch tokens with exception {e}')

        try:
            self.refresh_token()
        except Exception as e:
            logger.debug(f'failed to refresh tokens with exception {e}')
        else:
            self.token_store.store_tokens(self.tokens)
            return

        self.login()
        self.token_store.store_tokens(self.tokens)

    def make_request(
        self, http_method: Any,
        *args: Any,
        ignore_json: bool = False,
        attempt_authentication: bool = True,
        **kwargs: Any
    ) -> Union[Any, requests.Response]:
        """Makes the Session request.

        Returns:
            the response object if ignore_json is True, otherwise response json decoded object
        """
        response = http_method(*args, **kwargs, timeout=REQUEST_TIMEOUT)
        status_code = response.status_code

        if status_code == 401 and attempt_authentication:
            self.ensure_authenticated()
            kwargs['headers'].update(self.headers['processing'])
            return self.make_request(
                http_method, *args, ignore_json=ignore_json, attempt_authentication=False, **kwargs
            )

        response.raise_for_status()

        if status_code == 204:
            return response

        if ignore_json:
            return response
        else:
            return response.json()

    @deprecation.deprecated(details="Please use specific function instead of direct end point request.")
    def get(self, path, params=None, ignore_json=False, **kwargs):
        """Perform a GET request to the specified endpoint"""
        return self.make_request(
            self.session.get,
            self.api_version_url + path.lstrip('/'),
            headers=self.headers['processing'],
            params=params,
            ignore_json=ignore_json,
            **kwargs
        )

    @deprecation.deprecated(details="Please use specific function instead of direct end point request.")
    def post(self, path, params=None, ignore_json=False, **kwargs):
        # basically this extends http://docs.python-requests.org/en/latest/api/#requests.request
        # in particular, kwargs can contain files array
        """Perform a POST request to the specified endpoint"""
        return self.make_request(
            self.session.post,
            self.api_version_url + path.lstrip('/'),
            headers=self.headers['processing'],
            params=params,
            ignore_json=ignore_json,
            **kwargs
        )

    @deprecation.deprecated(details="Please use specific function instead of direct end point request.")
    def delete(self, path, params=None, ignore_json=True):
        """Perform a POST request to the specified endpoint"""
        return self.make_request(self.session.delete, self.api_version_url + path.lstrip('/'),
                                 headers=self.headers['processing'], params=params, ignore_json=ignore_json)

    @deprecation.deprecated(details="Please use specific function instead of direct end point request.")
    def post_json(self, path, json=None, ignore_json=False):
        """Perform a POST request to the specified endpoint"""
        return self.make_request(self.session.post, self.api_version_url + path.lstrip('/'),
                                 headers=self.headers['processing'], json=json, ignore_json=ignore_json)

    @deprecation.deprecated(details="Please use specific function instead of direct end point request.")
    def patch_json(self, path, json=None, ignore_json=True):
        """Perform a PATCH request to the specified endpoint"""
        return self.make_request(self.session.patch, self.api_version_url + path.lstrip('/'),
                                 headers=self.headers['processing'], json=json, ignore_json=ignore_json)

    @deprecation.deprecated(details="Please use specific function instead of direct end point request.")
    def put_json(self, path, json=None, ignore_json=False):
        # TODO set ignore_json=True in after making sure that json problem is not connected with response code
        """Perform a PUT request to the specified endpoint"""
        return self.make_request(self.session.put, self.api_version_url + path.lstrip('/'),
                                 headers=self.headers['processing'], json=json, ignore_json=ignore_json)



    @property
    def _graphql_host(self) -> str:
        """
        Reuse the same host logic as REST, but strip any path.
        E.g. if api_url → "https://foo.bar/admin/api/v2/", returns "foo.bar"
        """
        parsed = urlparse(self._resolve_api_url())
        return parsed.netloc

    def graphql_request(
        self,
        service: str,
        query: str,
        extra_headers: Optional[dict] = None,
        graphql_content_as_json: bool = False,
    ) -> dict:
        """Perform a GraphQL request to the specified endpoint

        Args:
            service: service name, e.g. 'admin', 'reports'
            query: GraphQL query
            extra_headers: extra headers to be added to the request
            graphql_content_as_json: if True, assumes that the graphql query will have JSON content
        Returns:
            GraphQL response dict
        """
        extra_headers = extra_headers or {}
        if 'X-Auth-Token' not in self.headers['processing']:
            self.ensure_authenticated()

        if graphql_content_as_json:
            graphql_headers = {'Content-Type': 'application/json'}
            graphql_headers.update({k: v for k, v in self.headers['graphql'].items() if k != 'Content-Type'})
        else:
            graphql_headers = self.headers['graphql']

        headers = {**self.headers['processing'], **graphql_headers, **extra_headers}

        host = self._graphql_host
        graphql_url = "https://{}/{}/graphql".format(host, service)

        response = self.make_request(self.session.post, graphql_url, headers=headers, data=query)
        return response

    def fields_report(
        self,
        request_fields: Union[List[str], Tuple[str, ...]],
        extent: Optional[Tuple[int, int, int, int]] = None,
        only_monitored: bool = True,
        enabled: bool = True,
        company_deleted: bool = False,
        prospecting_mode=None,
        only_in_grid: str = None,
        satellite_only: bool = False,
        company_id: int = None,
        provider: str = None,
        flight_date: str = None,
        r_max: int = 10000,
        offset: int = 0
    ):

        query = Template("""{
          fieldsReport(queryCommand: {
            $params
          }, max: $r_max, offset: $offset) {
                totalCount
                results {
                    $results
                }
            }
        }""")

        params = ""
        if extent is not None:
            params += """northEastLatitude: {},
            northEastLongitude: {},
            southWestLatitude: {},
            southWestLongitude: {},""".format(extent[0], extent[1], extent[2], extent[3])
        if only_monitored is True:
            params += """
            onlyMonitored: true,"""
        if enabled is True:
            params += """
            enabled: true,"""
        if company_deleted is False:
            params += """
            companyDeleted: false,"""
        if only_in_grid is True:
            params += """
            onlyInGrid: true,"""
        if satellite_only is True:
            params += """
            satelliteOnly: true,"""
        if prospecting_mode:
            params += """
            prospectingMode: {},""".format(prospecting_mode)
        if company_id:
            params += """
            companyId: {},""".format(company_id)
        if provider is not None:
            params += """
            provider: \"{}\",""".format(provider)
        if flight_date is not None:
            params += """
            flightDate: \"{}\",""".format(flight_date)
        params += """
            sort: \"id\""""

        results = ""
        if 'id' in request_fields:
            results += "id"
        if 'name' in request_fields:
            results += """
                    name"""
        if 'area' in request_fields:
            results += """
                    area"""
        if 'tags' in request_fields:
            results += """
                    tags"""
        if 'description' in request_fields:
            results += """
                    description"""
        if 'grid_id' in request_fields:
            results += """
                    grid{
                        id
                    }"""
        if 'grid_ids' in request_fields:
            results += """
                    gridIds"""
        if 'prospecting_mode' in request_fields:
            results += """
                    farm{
                        division{
                            company{
                                alias{
                                    companyHierarchy{
                                      prospectingMode
                                    }
                                }
                            }
                        }
                    }"""
        if 'latestFlight' in request_fields:
            results += """
                    latestFlight{
                        code
                    }"""
        if 'geometry' in request_fields:
            results += """
                    geoData{
                        geometry
                    }"""

        query = query.substitute(params=params, results=results, r_max=r_max, offset=offset)
        data = self.graphql_request(service="reports", query=query)
        return data

    def get_field_info(self, field_id: int, request_fields: List[str], service: str = 'admin'):
        """get field info

        Args:
            field_id: field id
            request_fields: fields to request available fields are
                id, name, latestFlight, fieldSeason, cropTypes, plantingDate, tags, area, token, plantedSeeds, flights
            service: service to make a call. Defaults to 'admin'.

        Returns:
            dict: field info
        """
        query = Template(
            """{
              field(id: $field_id) {
                $params
                } 
            }"""
        )
        params = ""

        if 'id' in request_fields:
            params += """
            id"""
        if 'name' in request_fields:
            params += """
            name"""
        if 'latestFlight' in request_fields:
            params += """
            latestFlight{
                id
                date
            }"""
        if 'fieldSeason' in request_fields:
            params += """
            fieldSeason{
                id
                geoData{
                    id
                    geometry
                }
            }"""
        if 'cropTypes' in request_fields:
            params += """
            cropTypes {
                id
                name
            }"""
        if 'plantingDate' in request_fields:
            params += """
            plantingDate"""
        if 'tags' in request_fields:
            params += """
            tags"""
        if 'area' in request_fields:
            params += """
            area"""
        if 'token' in request_fields:
            params += """
            token"""
        if 'plantedSeeds' in request_fields:
            params += """
            plantedSeeds"""
        if 'flights' in request_fields:
            params += """
            flights {
                id,
                date,
                code
                season {
                    id
                }
                provider
                reviewStatus
            }"""
        query = query.substitute(params=params, field_id=field_id)
        data = self.graphql_request(service=service, query=query)
        return data.get('data', {}).get('field', {})

    def get_attachment_types(self) -> dict:
        types = self.get("fieldattachmenttypes?max=100")
        return {z['keyName']: z['id'] for z in types['fieldAttachmentTypes']}

    # GET requests
    def get_flight(self, flight_code: str) -> dict:
        """Getting flight object."""
        url = self.url_template.format(f"flights/{flight_code}")
        response = self.make_request(self.session.get, url, headers=self.headers['processing'])
        return response

    def get_flight_features(self, flight_code: str) -> dict:
        """Getting flight features."""
        url = self.url_template.format(f"flights/{flight_code}/features")
        response = self.make_request(self.session.get, url, headers=self.headers['processing'])
        return response

    def get_imagery(self, imagery_code: str) -> dict:
        """Getting imagery data."""
        url = self.url_template.format(f"imagery/{imagery_code}")
        response = self.make_request(self.session.get, url, headers=self.headers['processing'])
        return response

    def get_seasons(self) -> dict:
        """
        Getting season info.
        Returns:
            list of seasons info wrapped in dict.
        """
        url = self.url_template.format("season/")
        response = self.make_request(self.session.get, url, headers=self.headers['processing'])
        return response

    def get_field(self, field_id: Union[int, str]) -> dict:
        """Getting field info for a given field_id or field_token."""
        url = self.url_template.format(f"fields/{field_id}")
        response = self.make_request(self.session.get, url, headers=self.headers['processing'])
        return response

    def get_field_products(self, field_id: Union[int, str], season_id: Union[int, str]) -> dict:
        """Getting field products for a given field_id and season_id."""
        url = self.url_template.format(f"fieldInfo/{field_id}/{season_id}")
        response = self.make_request(self.session.get, url, headers=self.headers['processing'])
        return response

    def get_flight_processing_data(self, flight_code: str) -> dict:
        """ Getting processing data for the flight."""
        url = self.url_template.format(f"flights/{flight_code}/processing")
        response = self.make_request(self.session.get, url, headers=self.headers['processing'])
        return response

    def get_equipment_flight_data(self, flight_code: str) -> dict:
        """Getting equipment flight data."""
        url = self.url_template.format(f"flights/{flight_code}/equipmentData")
        response = self.make_request(self.session.get, url, headers=self.headers['processing'])
        return response

    def get_uploaded_file(self, file_id: Union[int, str]) -> dict:
        """Getting uploaded file by ID."""
        url = self.url_template.format(f"uploadFile/{file_id}/")
        response = self.make_request(self.session.get, url, headers=self.headers['processing'])
        return response

    def get_uploaded_files(self, params: dict) -> dict:
        """
        Getting uploaded files based on filters in params.
        Args:
            params: http request params as key values.
        """
        url = self.url_template.format("uploadFile/")
        response = self.make_request(self.session.get, url, params=params, headers=self.headers['processing'])
        return response

    def get_field_attachments(self, field_id: Union[int, str]) -> list:
        """Getting field attachments list."""
        url = self.url_template.format(f"fields/{field_id}/attachments")
        response = self.make_request(self.session.get, url, headers=self.headers['processing'])
        return response

    def get_field_processing_data(self, field_id: Union[int, str]) -> list:
        """Get processing data for the field."""
        url = self.url_template.format(f"fields/{field_id}/processing")
        response = self.make_request(self.session.get, url, headers=self.headers['processing'])
        return response

    def get_field_all_boundaries(self, field_id: Union[int, str], ignore_json: bool = True) -> dict:
        """Getting field all boundaries."""
        url = self.url_template.format(f"fields/{field_id}/allboundaries")
        response = self.make_request(self.session.get, url, headers=self.headers['processing'], ignore_json=ignore_json)
        return response

    def get_previous_flight(self, flight_code: str) -> dict:
        """Getting previous flight of the given one."""
        url = self.url_template.format(f"flights/{flight_code}/previous")
        response = self.make_request(self.session.get, url, headers=self.headers['processing'])
        return response

    def get_field_tilesets(self, field_id: Union[int, str]) -> dict:
        """Getting list if tilesets for a given field."""
        url = self.url_template.format(f"fields/{field_id}/tilesets")
        response = self.make_request(self.session.get, url, headers=self.headers['processing'])
        return response

    def refresh_field_report(self) -> None:
        """Refresh field report."""
        url = self.url_template.format("fields/refreshFieldReport")
        self.make_request(self.session.get, url, headers=self.headers['processing'])

    def get_flight_alerts(self, flight_code: str, alert_name: str) -> dict:
        """
        Getting flight alerts for the given alert name and flight code.
        Args:
            flight_code:
            alert_name:
        """
        url = self.url_template.format(f"flights/{flight_code}/alerts?kindKeys={alert_name}")
        response = self.make_request(self.session.get, url, headers=self.headers['processing'])
        return response

    def get_imageries(self, filters: dict) -> dict:
        """
        Getting imageries filtered by given constraints in filters.
        Args:
            filters: key values based on which output will be generated. e.g.
            {
                "startDate": 2022-05-01,
                "endDate": 2022-05-31,
                "seasonId": 71,
                "provider": "Sentinel2"
            }
        """
        url = self.url_template.format("imagery/")
        response = self.make_request(self.session.get, url, params=filters, headers=self.headers['processing'])
        return response

    @deprecation.deprecated(details='Use get_growing_degree_days_by_field instead.')
    def get_growing_degree_days(self, flight_code: str, date_from: str, date_to: str) -> dict:
        """
        Get GDD for the flight.
        Args:
            flight_code:
            date_from:
            date_to:
        """
        validate_date(date_from)
        validate_date(date_to)
        params = {
            'flightCode': flight_code,
            'dateFrom': date_from,
            'dateTo': date_to
        }
        url = self.url_template.format("flights/gddForFlight")
        response = self.make_request(self.session.get, url, params=params, headers=self.headers['processing'])
        return response

    def get_growing_degree_days_by_field(self, field_id: int, date_from: Optional[str], date_to: str) -> dict:
        """Get GDD for a given field and date range."""
        if date_from:
            validate_date(date_from)
        validate_date(date_to)
        params = {
            'fieldId': field_id,
            'dateFrom': date_from,
            'dateTo': date_to
        }
        url = self.url_template.format("fields/gdd")
        response = self.make_request(self.session.get, url, params=params, headers=self.headers['processing'])
        return response

    def get_last_frost_date(self, field_id: Union[int, str], season_id: int, date_to: str) -> dict:
        """
        Get last frost date for the field.
        Args:
            field_id: the field id or token
            season_id: the season id
            date_to: the date before which the last frost will be returned
        """
        validate_date(date_to)
        url = self.url_template.format(f'fields/{field_id}/lastFrost')
        params = {
            'seasonId': season_id,
            'dateTo': date_to
        }
        response = self.make_request(self.session.get, url, params=params, headers=self.headers['processing'])
        return response

    def get_rollback_gdd_date(self, field_id: Union[int, str], season_id: int, date_from: str, rollback=100) -> dict:
        """
        Get rollback gdd date for the field.
        Args:
            field_id: the field id or token
            season_id: season id
            date_from: the date from which GDD should be rolled back
            rollback: the amount of GDD should be rolled back
        """
        validate_date(date_from)
        url = self.url_template.format(f'fields/{field_id}/rollbackGdd')
        params = {
            'seasonId': season_id,
            'dateFrom': date_from,
            'delta': rollback
        }
        response = self.make_request(self.session.get, url, params=params, headers=self.headers['processing'])
        return response

    def get_field_planting_date_and_crop_types(
        self,
        field_id: Union[str, int],
        season_id: int
    ) -> Tuple[Optional[str], list]:
        """Gets the available planting date and crop types from the api

        Args:
            field_id: the field id
            season_id: the season id

        Returns:
            planting datetime and list of crop types
        """
        query = f"""{{
                  listFieldSeasons(queryCommand: {{seasonId: {season_id}, fieldId: {field_id}}}) {{
                    results {{
                      cropTypeKeys
                      plantingDate
                    }}
                  }}
                }}"""
        query_results = self.graphql_request(service='admin', query=query)
        if not query_results['data']['listFieldSeasons']['results']:
            return None, []
        [field_season] = query_results['data']['listFieldSeasons']['results']
        if field_season.get('cropTypeKeys') is not None:
            crop_types = [ct.split('.')[-1].lower() for ct in field_season['cropTypeKeys']]
        else:
            crop_types = []
        planting_date = field_season.get('plantingDate')
        return planting_date, crop_types

    def get_field_attachment_types(self, max_count: int = 100) -> list:
        """
        Getting available attachment types for the field.
        Args:
            max_count: Maximum count of types to return.
        """
        url = self.url_template.format("fieldattachmenttypes")
        params = {
            'max': max_count
        }
        response = self.make_request(self.session.get, url, params=params, headers=self.headers['processing'])
        return response

    def check_field_weather_data_existence(self, field_id: Union[int, str], start_date: str, end_date: str) -> dict:
        """Checking given field weather data download completion status between given date range."""
        validate_date(start_date)
        validate_date(end_date)
        url = self.url_template.format("weather/verifyConsistency")
        params = {
            'fieldId': field_id,
            'startDate': start_date,
            'endDate': end_date
        }
        response = self.make_request(self.session.get, url, params=params, headers=self.headers['processing'])
        return response

    def get_company(self, company_id: Union[int, str]) -> dict:
        """Getting company info from given company id."""
        url = self.url_template.format(f"companies/{company_id}")
        response = self.make_request(self.session.get, url, headers=self.headers['processing'])
        return response

    def get_flight_tilesets(self, flight_code: str) -> dict:
        """Getting flight tilesets."""
        url = self.url_template.format(f"flights/{flight_code}/tilesets")
        response = self.make_request(self.session.get, url, headers=self.headers['processing'])
        return response

    def get_problem_alert_default_tileset(self, flight_code: str, badge_id: Union[int, str]) -> dict:
        """
        Getting default tileset for problem alert.
        Args:
            flight_code: the flight code for which the alerts should be returned
            badge_id: problem alert badge ID
        """
        params = {
            'badgeId': badge_id
        }
        url = self.url_template.format(f"flights/{flight_code}/defaultTileset")
        response = self.make_request(self.session.get, url, params=params, headers=self.headers['processing'])
        return response

    # POST requests
    def imageries_report(self, filters: dict) -> dict:
        """
        Getting reported imagery list based on filters.
        Args:
            filters: key values based on which output will be generated. e.g.
            {
                "startDate": 2022-05-01,
                "endDate": 2022-05-31
            }
        """
        url = self.url_template.format("reports/imagery/")
        response = self.make_request(self.session.post, url, params=filters, headers=self.headers['processing'])
        return response

    def upload_complete_flight(self, flight_code: str) -> None:
        """Setting upload Complete to the flight."""
        url = self.url_template.format(f"flights/{flight_code}/uploadComplete")
        self.make_request(self.session.post, url, headers=self.headers['processing'])

    def get_field_equipment_flight_data(self, field_id: Union[int, str], season_id: int) -> dict:
        """Getting list of equipment flights data for the field."""
        url = self.url_template.format("flights/equipmentFlightsData")
        params = {
            "fieldId": field_id,
            "seasonId": season_id
        }
        response = self.make_request(self.session.post, url, params=params, headers=self.headers['processing'])
        return response

    def upload_field_attachment(self, field_id: Union[int, str], attachment_id: Union[int, str], attachment_path: str):
        """
        Uploading field attachment file.
        Attachment is done through binary stream.
        Args:
            field_id: the field id for which attachment should be uploaded
            attachment_id: the id of the attachment
            attachment_path: the path of tha attachment to be uploaded
        """
        url = self.url_template.format(f"fields/{field_id}/attachments/{attachment_id}/upload")
        with open(attachment_path, 'rb') as attachment_handle:
            files = {
                "attachmentFile": (os.path.basename(attachment_path), attachment_handle, 'application/octet-stream')
            }
            self.make_request(self.session.post, url, files=files, headers=self.headers['processing'])

    def rerun_flight(self, flight_code: str) -> None:
        """Rerunning given flight processing."""
        url = self.url_template.format(f"flights/{flight_code}/rerun")
        self.make_request(self.session.post, url, headers=self.headers['processing'])

    # DELETE requests
    def delete_flight(self, flight_code: str) -> None:
        """Delete flight by code."""
        url = self.url_template.format(f"flights/{flight_code}")
        self.make_request(self.session.delete, url, headers=self.headers['processing'], ignore_json=True)

    def delete_field_attachment(self, field_id: Union[int, str], attachment_id: Union[int, str]) -> None:
        """Delete field attachment file by given field and file id."""
        url = self.url_template.format(f"fields/{field_id}/attachments/{attachment_id}")
        self.make_request(self.session.delete, url, headers=self.headers['processing'], ignore_json=True)

    def delete_field_attachments_by_file_type(self, field_id: int, flight_id: Optional[int], file_type_id: int) -> None:
        """Deletes all the field attachments matching the given criteria

        Args:
            field_id: the id of the field to delete attachments for
            flight_id: if provided will only delete attachments that have this flight_id
            file_type_id: only deletes attachments with this file_type_id
        """
        query = f"""query {{
        field(id: {field_id}) {{ id fieldAttachments{{ id version fileType {{ id }} flight {{ id }}}}}}}}
        """
        result = self.graphql_request(service='admin', query=query)
        attachments = result['data']['field']['fieldAttachments']
        attachments = filter(lambda x: x['fileType']['id'] == file_type_id, attachments)
        if flight_id:
            attachments = filter(lambda x: x['flight'] is not None, attachments)
            attachments = filter(lambda x: x['flight']['id'] == flight_id, attachments)

        attachments = list(attachments)
        logger.info(f'Found {len(attachments)} existing veg row field attachments for this flight, will delete them')
        for att in attachments:
            logger.info(f'Deleting Field Attachment with id={att["id"]}')
            self.delete_field_attachment(field_id=field_id, attachment_id=att['id'])

    def delete_field_tileset(self, field_id: Union[int, str], tileset_id: Union[int, str]) -> None:
        """Delete field tileset by id."""
        url = self.url_template.format(f"fields/{field_id}/tilesets/{tileset_id}")
        self.make_request(self.session.delete, url, headers=self.headers['processing'], ignore_json=True)

    def delete_flight_tileset(self, flight_id: Union[int, str], tileset_id: Union[int, str]) -> None:
        """Delete flight tileset by id."""
        url = self.url_template.format(f"flights/{flight_id}/tilesets/{tileset_id}")
        self.make_request(self.session.delete, url, headers=self.headers['processing'], ignore_json=True)

    # POST_JSON requests
    def get_flights_annotations(self, filters: dict, params=None) -> dict:
        """
        Getting flight annotations report based on input params in filter.
        Args:
            filters: key values based on which output will be generated. e.g.
            {
                "alertKindId": 29,
                "annotationStatus": "QA_COMPLETE"
            }
            params: http request params as key values.
        """
        url = self.url_template.format("reports/toafa")
        response = self.make_request(self.session.post, url, filters, params=params, headers=self.headers['processing'])
        return response

    def add_field_tag(self, field_id: Union[int, str], tag: str, key_name: str = 'dashboard') -> None:
        """
        Add tag to field object.
        Args:
            field_id: the field id or token
            tag: Tag name to add.
            key_name: tag keyname (mainly dashboard and system).
        """
        url = self.url_template.format(f"fields/{field_id}/addTag")
        params = {
            "optionName": tag,
            "keyName": key_name
        }
        self.make_request(self.session.post, url, json=params, headers=self.headers['processing'])

    def remove_field_tag(self, field_id: Union[int, str], tag: str, key_name: str = 'dashboard') -> None:
        """
        Remove given tag from the field object.
        Args:
            field_id: the field id or token
            tag: tag name
            key_name: tag keyname (mainly dashboard and system).
        """
        url = self.url_template.format(f"fields/{field_id}/removeTag")
        params = {
            "optionName": tag,
            "keyName": key_name
        }
        self.make_request(self.session.post, url, json=params, headers=self.headers['processing'])

    def add_flight_tag(self, flight_code: str, tag: str, key_name: str = 'dashboard') -> None:
        """
        Add tag to the flight object.
        Args:
            flight_code: flight code
            tag: tag name to add
            key_name: tag keyname (mainly dashboard and system).
        """
        url = self.url_template.format(f"flights/{flight_code}/addTag")
        params = {
            "optionName": tag,
            "keyName": key_name
        }
        self.make_request(self.session.post, url, json=params, headers=self.headers['processing'])

    def remove_flight_tag(self, flight_code: str, tag: str, key_name: str = 'dashboard') -> None:
        """
        Remove given tag from the flight object.
        Args:
            flight_code: flight code
            tag: tag name
            key_name: tag keyname (mainly dashboard and system).
        """
        url = self.url_template.format(f"flights/{flight_code}/removeTag")
        params = {
            "optionName": tag,
            "keyName": key_name
        }
        self.make_request(self.session.post, url, json=params, headers=self.headers['processing'])

    def get_field_flight(self, field_id: Union[int, str], filters: dict) -> dict:
        """
        Getting flight for a given field based on input filters.
        Args:
            field_id:
            filters: key values based on which output will be generated. e.g.
            {
                'provider': 'Aeroptic',
                'date': 2022-05-01,
            }
        """
        url = self.url_template.format(f"fields/{field_id}/flight")
        response = self.make_request(self.session.post, url, json=filters, headers=self.headers['processing'])
        return response

    def flights_report(self, filters: dict) -> dict:
        """
        Generates report of the flights based on a given filters.
        Args:
            filters: key values based on which output will be generated. e.g.
            {
                'fieldId': 12345678,
                'providers': ['Aeroptic'],
                'startDate': 2022-05-01,
                'endDate': 2022-05-30
            }
        """
        url = self.url_template.format("reports/toaf")
        response = self.make_request(self.session.post, url, json=filters, headers=self.headers['processing'])
        return response

    def create_imagery(self, payload: dict) -> dict:
        """
        Creates imagery object with values passed through payload.
        Args:
            payload: properties of imagery object to create.
        Returns:
            Created imagery object.
        """
        url = self.url_template.format("imagery/")
        response = self.make_request(self.session.post, url, json=payload, headers=self.headers['processing'])
        return response

    def delete_imagery(self, imagery_code: str) -> None:
        """Deletes imagery object with values passed through payload."""
        url = self.url_template.format(f"imagery/{imagery_code}")
        response = self.make_request(self.session.delete, url, headers=self.headers['processing'], ignore_json=True)
        response.raise_for_status()

    def create_flight(self, payload: dict) -> dict:
        """
        Creates flight object with values passed through payload.
        Args:
            payload: properties of flight object to create.
        Returns:
            Created flight object.
        """
        url = self.url_template.format("flights/")
        response = self.make_request(self.session.post, url, json=payload, headers=self.headers['processing'])
        return response

    def create_imagery_tile_layer(self, payload: dict) -> None:
        """
        Creates imagery layer.
        Args:
            payload: properties of tile layer to create.
        """
        url = self.url_template.format("imagery/tiles/layers")
        self.make_request(self.session.post, url, json=payload, headers=self.headers['processing'])

    def post_field_metadata(self, field_id: Union[int, str], metadata: dict) -> requests.Response:
        """Create field metadata."""
        url = self.url_template.format(f"fields/{field_id}/metadata/")
        response = self.make_request(self.session.post, url, json=metadata, headers=self.headers['processing'],
                                     ignore_json=True)
        return response

    def toggle_flight_tileset(self, flight_code: str, tileset_name: str, is_hidden: bool) -> None:
        """
        Changing hidden attribute of the flight tileset.
        Args:
            flight_code: on which change should be performed.
            tileset_name: tileset which will be changed.
            is_hidden: value to be set.
        """
        url = self.url_template.format(f"flights/{flight_code}/toggleTilesets/")
        payload = {
            'tilesets': [
                {
                    'name': tileset_name,
                    'hidden': is_hidden
                }
            ]
        }
        self.make_request(self.session.post, url, json=payload, headers=self.headers['processing'],
                          ignore_json=True)

    def reject_flight(self, flight_code: str, comment: str) -> None:
        """Automatically reject the flight with a given comment."""
        url = self.url_template.format(f"flights/{flight_code}/flightComments/")
        payload = {
            "reviewer": "Automatic",
            "flightCode": flight_code,
            "subject": "Automatic rejection",
            "comments": comment
        }
        self.make_request(self.session.post, url, json=payload, headers=self.headers['processing'])

    def create_field_attachment(self, field_id: Union[int, str], attachment_data: dict) -> dict:
        """Create field attachment with given data."""
        url = self.url_template.format(f'/fields/{field_id}/attachments')
        response = self.make_request(self.session.post, url, json=attachment_data, headers=self.headers['processing'])
        return response

    def create_field_tilesets(self, field_id: Union[int, str], tilesets_data: dict) -> None:
        """Creates tilesets from data for the given field."""
        url = self.url_template.format(f'/fields/{field_id}/tilesets')
        self.make_request(self.session.post, url, json=tilesets_data, headers=self.headers['processing'])

    def create_flight_tilesets(self, flight_code: str, tilesets_data: dict) -> None:
        """Creates tilesets from data for the given flight."""
        url = self.url_template.format(f'/flights/{flight_code}/tilesets')
        self.make_request(self.session.post, url, json=tilesets_data, headers=self.headers['processing'])

    # PATCH_JSON requests
    def update_imagery(self, imagery_code: str, imagery_data: dict) -> None:
        """
        Update imagery object properties.
        Args:
            imagery_code: code of imagery to be changed.
            imagery_data: key-values of properties that will be changed.
        """
        url = self.url_template.format(f"imagery/{imagery_code}/")
        self.make_request(self.session.patch, url, json=imagery_data, headers=self.headers['processing'],
                          ignore_json=True)

    def update_field(self, field_id: Union[int, str], field_data: dict) -> None:
        """
        Update field object properties.
        Args:
            field_id: id of field to be changed.
            field_data: key-values of properties that will be changed.
        """
        url = self.url_template.format(f"fields/{field_id}/")
        self.make_request(self.session.patch, url, json=field_data, headers=self.headers['processing'],
                          ignore_json=True)

    def update_field_attachment(
        self,
        field_id: Union[int, str],
        attachment_id: Union[int, str],
        attachment_data: dict
    ) -> None:
        """
        Update field attachment file
        Args:
            field_id: the field id or token
            attachment_id: id of a file to be changed
            attachment_data: key-values of properties that will be changed
        """
        url = self.url_template.format(f"fields/{field_id}/attachments/{attachment_id}/")
        self.make_request(self.session.patch, url, json=attachment_data, headers=self.headers['processing'],
                          ignore_json=True)

    def update_flight(self, flight_code: str, flight_data: dict) -> None:
        """
        Update flight object.
        Args:
            flight_code: code of flight to change
            flight_data: key-values of properties that will be changed
        """
        url = self.url_template.format(f"flights/{flight_code}/")
        self.make_request(self.session.patch, url, json=flight_data, headers=self.headers['processing'],
                          ignore_json=True)

    def update_flight_features(self, flight_code: str, features: dict) -> None:
        """
        Update flight features.
        Args:
            flight_code: code of flight to change.
            features: key-values of properties that will be changed.
        """
        url = self.url_template.format(f"flights/{flight_code}/features")
        self.make_request(self.session.post, url, json=features, headers=self.headers['processing'],
                          ignore_json=False)

    def update_flight_tilesets(
        self,
        flight_id: Union[int, str],
        tileset_id: Union[int, str],
        tilesets_data: dict
    ) -> None:
        """Update given flight tilesets."""
        url = self.url_template.format(f"flights/{flight_id}/tilesets/{tileset_id}")
        self.make_request(self.session.patch, url, json=tilesets_data, headers=self.headers['processing'],
                          ignore_json=True)

    # PUT_JSON requests
    def update_uploaded_file(self, file_id: Union[int, str], file_data: dict) -> None:
        """
        Update uploaded file.
        Args:
            file_id: id of file to change
            file_data: key-values of properties that will be changed
        """
        url = self.url_template.format(f"uploadFile/{file_id}/")
        self.make_request(self.session.put, url, json=file_data, headers=self.headers['processing'])

    def update_flight_alert(self, flight_code: str, alert_id: Union[int, str], alert_data: dict) -> None:
        """
        Update alert of the flight.
        Args:
            flight_code: code of a flight to change.
            alert_id: id of an alert to change.
            alert_data: key-values of properties that will be changed.
        """
        url = self.url_template.format(f"flights/{flight_code}/alerts/{alert_id}/")
        self.make_request(self.session.put, url, json=alert_data, headers=self.headers['processing'])

    def add_field_list_to_file(self, file_id: Union[int, str], field_list: list) -> None:
        """
        add field list to the uploaded file.
        Args:
            file_id: uploaded file id
            field_list: list of fields to be added
        """
        url = self.url_template.format(f"uploadFile/{file_id}/addToFieldList")
        payload = {
            "fields": field_list
        }
        self.make_request(self.session.put, url, json=payload, headers=self.headers['processing'])

    def delete_tileset(self, tileset_id: int) -> None:
        """
        Deletes tileset with the given id.
        Args:
            tileset_id: the id of the tileset to be deleted
        """
        url = self.url_template.format(f"tilesets/{tileset_id}")
        self.make_request(self.session.delete, url, headers=self.headers['processing'], ignore_json=True)
