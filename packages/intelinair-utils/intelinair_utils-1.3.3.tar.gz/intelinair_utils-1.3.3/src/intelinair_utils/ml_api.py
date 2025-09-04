import json
import logging
import os
from collections import defaultdict
from datetime import datetime
from typing import Generator, List, Optional, Tuple, Dict

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from intelinair_utils.api import Api

logger = logging.getLogger(__name__)

KNOWN_ENVS = ['prod', 'release', 'bellflower', 'local']
DEFAULT_FILTER_PATH = os.path.expanduser('~/.mlapi_filters.json')
FILTER_PATH_ENV_KEY = 'MLAPI_FILTER_PATH'


class MLApi(Api):
    """
    Wrapper class for queries against the ML Service

    Supports a config file which can be used to filter information returned by this client,
    The default config location is '~/.mlapi_filters.json' and can be provided by setting
    the MLAPI_FILTER_PATH environment variable

    The config file should be a json file with the following keys:
        `inference_filter_list`    : A dictionary of filter params to include for the get_inferences function
                                     The parameter should be a dictionary with the key being an inference_type
                                     and the value should be extra filter parameters to include with the request
                                     to the ML Api.
                                     Example:
                                         {
                                            "inference_type1": {"model_name": "your-model", "model_version": 2},
                                            "inference_type2": {"model_id": 2, "docker_image": "model_image:tag"}
                                        }

        `inference_type_allow_list`: A list of allowed inference types for the get_inferences function to return
                                     The function will raise a ValueError for any request for an inference_type
                                     not in this allow list
                                     Example:
                                         ["inference_type1", "inference_type2"]

    """

    def __init__(self, environment):
        # version_string == '' corresponds to the first version of API
        assert environment in KNOWN_ENVS, 'Unknown environment for the ML Service'
        self.environment = environment
        if environment == 'local':
            self.api_url = 'http://localhost:8080'
        else:
            self.api_url = f'https://ml.{environment}.int.intelinair.dev'
        # all calls (other than login) should use the version string
        self.session = requests.Session()
        retries = Retry(total=10, read=5, connect=5, backoff_factor=1, allowed_methods=False,
                        status_forcelist=[104, 500, 502, 503, 504])
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        self.session.mount('http://', HTTPAdapter(max_retries=retries))

        filter_path = os.environ.get(FILTER_PATH_ENV_KEY, DEFAULT_FILTER_PATH)
        filter_content = self._load_filters(filter_path)
        self.inference_filters = filter_content.get('inference_filter_list', {})
        self.inference_type_allow_list = filter_content.get('inference_type_allow_list', None)

    @staticmethod
    def _load_filters(filter_path):
        """Loads the filter config"""
        if os.path.exists(filter_path):
            with open(filter_path) as fp:
                return json.load(fp)
        else:
            return {}

    def get(self, path, params=None, json=None, ignore_json=False):
        res = self.session.get(self.api_url + path, params=params, json=json)
        res.raise_for_status()
        if ignore_json is True:
            return res
        else:
            return res.json()

    def post(self, path, json=None, params=None):
        res = self.session.post(self.api_url + path, json=json, params=params)
        res.raise_for_status()
        return res.json()

    def patch(self, path, json=None, params=None):
        res = self.session.patch(self.api_url + path, json=json, params=params)
        res.raise_for_status()
        return res.json()

    def delete(self, path, json=None, params=None):
        res = self.session.delete(self.api_url + path, json=json, params=params)
        res.raise_for_status()
        return res.json()

    def create_dataset(self, name: str, version: int, data: dict, tags: dict = None) -> dict:
        """Creates a dataset with the given parameters"""
        return self.post('/datasets/', json={
            'name': name,
            'version': version,
            'data': data,
            'tags': tags
        })

    def update_dataset(self, dataset: dict) -> dict:
        """Updates a dataset object in the service with new data"""
        return self.patch(f'/datasets/{dataset["id"]}', json=dataset)

    def get_dataset_by_id(self, dataset_id: int) -> dict:
        """Gets a dataset by its id"""
        return self.get(f'/datasets/{dataset_id}')

    def get_latest_dataset(self, dataset_name: str) -> dict:
        """Gets the latest dataset with the given name"""
        return self.get(f'/datasets/latest', params={'dataset_name': dataset_name})

    def get_datasets(self, dataset_name: str = None, dataset_version: int = None,
                     api_limit_size: int = 100) -> Generator[dict, None, None]:
        """Gets a generator of datasets optionally filtering by name and/or version"""
        skip = 0
        while True:
            datasets = self.get(
                '/datasets/',
                params={
                    'skip': skip,
                    'limit': api_limit_size,
                    'name': dataset_name,
                    'version': dataset_version
                }
            )
            for dataset in datasets:
                yield dataset
            if len(datasets) == api_limit_size:
                skip += api_limit_size
            else:
                break

    def get_dataset(self, dataset_name: str, dataset_version: int = None) -> dict:
        """Gets a dataset by name and optionally a specific version of the dataset"""
        if dataset_version is None:
            return self.get_latest_dataset(dataset_name)
        datasets = list(self.get_datasets(dataset_name, dataset_version))
        if len(datasets) == 0:
            raise Exception(f'Could not find dataset with  '
                            f'dataset_name={dataset_name} and version={dataset_version}')
        try:
            [dataset] = datasets
            return dataset
        except ValueError:
            raise ValueError(f'Multiple datasets registered with the same version '
                             f'model_name={dataset_name} and version={dataset_version}')

    def get_dataset_flights(self, dataset_id: int, api_limit_size: int = 250) -> Dict[str, List[dict]]:
        """Gets all the flights in a dataset"""
        offset = 0
        final_results = defaultdict(list)
        while True:
            results = self.get(f'/datasets/flights',
                               json={
                                   'dataset_id': dataset_id,
                                   'offset': offset,
                                   'limit': api_limit_size,
                               })
            for split, flights in results.items():
                final_results[split].extend(flights)
            if sum([len(flights) for flights in results.values()]) == api_limit_size:
                offset += api_limit_size
            else:
                break
        return final_results

    def create_model(self, model_name: str, model_version: int, model_hash: str, s3_location: str,
                     tags: dict = None, data: dict = None) -> dict:
        """Creates a model with the ML Service with the given parameters"""
        return self.post(
            '/models/',
            json={
                "model_name": model_name,
                "model_version": model_version,
                "model_hash": model_hash,
                "s3_location": s3_location,
                "tags": tags,
                "data": data
            }
        )

    def update_model(self, model: dict) -> dict:
        """Updates a model"""
        return self.patch(f'/models/{model["id"]}', json=model)

    def get_or_create_model_from_script(self, git_repo_name: str, script_name: str, git_description: str) -> dict:
        """Gets a model by script name and git description or creates one if it doesn't exist"""
        return self.post('/models/script', params={
            'git_repo_name': git_repo_name,
            'script_name': script_name,
            'git_description': git_description
        })

    def get_model_by_id(self, model_id: int) -> dict:
        """Gets a model by id"""
        return self.get(f'/models/{model_id}')

    def get_latest_model(self, model_name: str) -> dict:
        """Gets the latest model with the given name"""
        return self.get(f'/models/latest', params={'model_name': model_name})

    def get_models(self, model_name: str = None, model_version: int = None,
                   api_limit_size: int = 100) -> Generator[dict, None, None]:
        """Gets models from the api with optional filters"""
        skip = 0
        while True:
            models = self.get(f'/models/?skip={skip}&limit={api_limit_size}',
                              json={'model_name': model_name, 'model_version': model_version})
            for model in models:
                yield model
            if len(models) == api_limit_size:
                skip += api_limit_size
            else:
                break

    def get_model(self, model_name: str, model_version: int = None) -> dict:
        """Gets the model with the give name and version, if no version is specified the latest version is returned"""
        if model_version is None:
            return self.get_latest_model(model_name)
        models = list(self.get_models(model_name, model_version))
        if len(models) == 0:
            raise Exception(f'Could not find registered models with '
                            f'model_name={model_name} and version={model_version}')
        try:
            [model] = models
            return model
        except ValueError:
            raise ValueError(f'Multiple models registered with the same version '
                             f'model_name={model_name} and version={model_version}')

    def create_inference(self, flight_code: str, inference_type: str, model_id: int, docker_image: str,
                         hparams: dict, result: dict, zone_token: Optional[str] = None,
                         pipeline_version: Optional[str] = None) -> dict:
        """Creates an inference with the given parameters"""
        return self.post('/inferences/flight/', json={
            'flight_code': flight_code,
            'zone_token': zone_token,
            'inference_type': inference_type,
            'model_id': model_id,
            'docker_image': docker_image,
            'pipeline_version': pipeline_version,
            'hparams': hparams,
            'result': result,
        })

    def create_inference_from_script(self, flight_code: str, inference_type: str, result: dict, git_repo_name: str,
                                     script_name: str, git_description: str, hparams: dict,
                                     zone_token: Optional[str] = None, docker_image: Optional[str] = None,
                                     pipeline_version: Optional[str] = None) -> dict:
        """Creates an inference from a script"""
        return self.post('/inferences/flight/script', json={
            'flight_code': flight_code,
            'zone_token': zone_token,
            'inference_type': inference_type,
            'git_repo_name': git_repo_name,
            'script_name': script_name,
            'git_description': git_description,
            'docker_image': docker_image,
            'pipeline_version': pipeline_version,
            'hparams': hparams,
            'result': result
        })

    def update_inference(self, inference: dict) -> dict:
        return self.patch(f'/inferences/flight/{inference["id"]}', json=inference)

    def get_inference_by_id(self, inference_id: int) -> dict:
        """Gets an inference by id"""
        return self.get(f'/inferences/flight/{inference_id}')

    def get_inferences(self, flight_code: List[str] = None, inference_type: str = None, model_id: int = None,
                       model_name: str = None, model_version: int = None, git_repo_name: str = None,
                       script_name: str = None, git_description: str = None, docker_image: str = None,
                       pipeline_version: str = None, hparams: dict = None,
                       start_ts: datetime = None, end_ts: datetime = None,
                       zone_token: str = None, api_limit_size: int = 100) -> Generator[dict, None, None]:
        """Returns inferences that match the provided filters"""
        if self.inference_type_allow_list and inference_type not in self.inference_type_allow_list:
            raise ValueError(f"inference type: {inference_type} not in "
                             f"inference type allow list {self.inference_type_allow_list}")

        request = {
            'flight_code': flight_code,
            'inference_type': inference_type,
            'zone_token': zone_token,
            'start_ts': str(start_ts) if start_ts else None,
            'end_ts': str(end_ts) if end_ts else None,
            'model_id': model_id,
            'model_name': model_name,
            'model_version': model_version,
            'git_repo_name': git_repo_name,
            'script_name': script_name,
            'git_description': git_description,
            'docker_image': docker_image,
            'pipeline_version': pipeline_version,
            'hparams': hparams
        }

        if inference_type and inference_type in self.inference_filters:
            request.update(**self.inference_filters[inference_type])

        base_id = 0
        while True:
            response = self.get(f'/v2/inferences/flight/?base_id={base_id}&limit={api_limit_size}', json=request)
            for inference in response['inferences']:
                yield inference
            if response['next_id'] is not None:
                base_id = response['next_id']
            else:
                break

    def get_inference_types(self, flight_code: str) -> List[str]:
        """Returns the inference types available for this flight"""
        return self.get(f'/inferences/flight/types/{flight_code}')

    def get_flight_codes_with_inference_type(self, inference_type: str,
                                             api_limit_size: int = 10000) -> Generator[str, None, None]:
        """Returns a list of flight codes with an inference with the given inference type"""
        skip = 0
        while True:
            flight_codes = self.get(f'/inferences/flight/codes/{inference_type}?skip={skip}&limit={api_limit_size}')
            for flight_code in flight_codes:
                yield flight_code
            if len(flight_codes) == api_limit_size:
                skip += api_limit_size
            else:
                break

    def create_flight_evaluation(self, flight_code: str, inference_id: int, scores: dict, eval_type: str = 'default') -> dict:
        """Creates an evaluation for a flight with the given parameters"""
        return self.post('/evaluations/flight/', json={
            'flight_code': flight_code,
            'inference_id': inference_id,
            'type': eval_type,
            'scores': scores,
        })

    def get_flight_evaluation_by_id(self, flight_evaluation_id: int) -> dict:
        """Returns an evaluation by id"""
        return self.get(f'/evaluations/flight/{flight_evaluation_id}')

    def get_flight_evaluations(self, flight_code: List[str] = None, inference_type: str = None,
                               model_id: int = None, model_name: str = None, model_version: int = None,
                               git_repo_name: str = None, script_name: str = None, git_description: str = None,
                               docker_image: str = None, hparams: dict = None,
                               inference_id: int = None, eval_type: str = None,
                               api_limit_size: int = 100) -> Generator[dict, None, None]:
        """Generates a set of evaluations that match the provided filters"""
        skip = 0
        while True:
            evaluations = self.get(
                '/evaluations/flight/',
                json={
                    'flight_code': flight_code,
                    'inference_type': inference_type,
                    'type': eval_type,
                    'model_id': model_id,
                    'model_name': model_name,
                    'model_version': model_version,
                    'git_repo_name': git_repo_name,
                    'script_name': script_name,
                    'git_description': git_description,
                    'docker_image': docker_image,
                    'hparams': hparams,
                    'inference_id': inference_id,
                },
                params={
                    'skip': skip,
                    'limit': api_limit_size,
                }
            )
            for evaluation in evaluations:
                yield evaluation
            if len(evaluations) == api_limit_size:
                skip += api_limit_size
            else:
                break

    def create_field_inference(self, field_token: str, date_active: datetime, inference_type: str, model_id: int,
                               docker_image: str, hparams: dict, result: dict, season_id: int = -1,
                               zone_token: str = 'boundary', pipeline_version: Optional[str] = None) -> dict:
        """Creates an inference with the given parameters"""
        return self.post('/inferences/field/', json={
            'field_token': field_token,
            'season_id': season_id,
            'zone_token': zone_token,
            'date_active': date_active.isoformat(),
            'inference_type': inference_type,
            'model_id': model_id,
            'docker_image': docker_image,
            'pipeline_version': pipeline_version,
            'hparams': hparams,
            'result': result,
        })

    def create_field_inference_from_script(self, field_token: str, date_active: datetime, inference_type: str,
                                           result: dict,
                                           git_repo_name: str, script_name: str, git_description: str, hparams: dict,
                                           season_id: int = -1, zone_token: str = 'boundary',
                                           docker_image: Optional[str] = None,
                                           pipeline_version: Optional[str] = None) -> dict:
        """Creates an inference from a script"""
        return self.post('/inferences/field/script', json={
            'field_token': field_token,
            'season_id': season_id,
            'zone_token': zone_token,
            'date_active': date_active.isoformat(),
            'inference_type': inference_type,
            'git_repo_name': git_repo_name,
            'script_name': script_name,
            'git_description': git_description,
            'docker_image': docker_image,
            'pipeline_version': pipeline_version,
            'hparams': hparams,
            'result': result
        })

    def update_field_inference(self, inference: dict) -> dict:
        return self.patch(f'/inferences/field/{inference["id"]}', json=inference)

    def get_field_inference_by_id(self, inference_id: int) -> dict:
        """Gets an inference by id"""
        return self.get(f'/inferences/field/{inference_id}')

    def get_field_inferences(self, date: datetime = datetime.max, field_token: List[str] = None,
                             season_id: List[int] = None,
                             zone_token: List[str] = None, inference_type: str = None, model_id: int = None,
                             model_name: str = None,
                             model_version: int = None, git_repo_name: str = None, script_name: str = None,
                             git_description: str = None, docker_image: str = None, pipeline_version: str = None,
                             hparams: dict = None, start_ts: datetime = None, end_ts: datetime = None,
                             api_limit_size: int = 100) -> Generator[dict, None, None]:
        """Returns inferences that match the provided filters"""
        if self.inference_type_allow_list and inference_type not in self.inference_type_allow_list:
            raise ValueError(f"inference type: {inference_type} not in "
                             f"inference type allow list {self.inference_type_allow_list}")

        request = {
            'date': date.isoformat(),
            'field_token': field_token,
            'season_id': season_id,
            'inference_type': inference_type,
            'zone_token': zone_token,
            'start_ts': str(start_ts) if start_ts else None,
            'end_ts': str(end_ts) if end_ts else None,
            'model_id': model_id,
            'model_name': model_name,
            'model_version': model_version,
            'git_repo_name': git_repo_name,
            'script_name': script_name,
            'git_description': git_description,
            'docker_image': docker_image,
            'pipeline_version': pipeline_version,
            'hparams': hparams
        }

        if inference_type and inference_type in self.inference_filters:
            request.update(**self.inference_filters[inference_type])

        base_id = 0
        while True:
            response = self.get(f'/inferences/field/?base_id={base_id}&limit={api_limit_size}', json=request)
            for inference in response['inferences']:
                yield inference
            if response['next_id'] is not None:
                base_id = response['next_id']
            else:
                break

    def get_latest_field_inferences(
        self, field_token: List[str], date: datetime = datetime.max, season_id: List[int] = None,
        zone_token: List[str] = None,
        inference_type: str = None, model_id: int = None, model_name: str = None,
        model_version: int = None, git_repo_name: str = None, script_name: str = None,
        git_description: str = None, docker_image: str = None, pipeline_version: str = None,
        hparams: dict = None, start_ts: datetime = None, end_ts: datetime = None, api_limit_size: int = 100
    ) -> Generator[Tuple[Tuple[str, int], dict], None, None]:
        """Returns the latest field inferences that match the given filters
        After the filters are applied inferences are grouped by field_toke, season_id, zone_token, and inference type
        For each of these groups the latest inference is defined to be in the group of inferences with the latest active date
        and among these the inference with the highest version is selected

        Yields:
            key: the key for the latest inference (field_token, season_id, zone_token, inference_type)
            inference: the dict of the inference
        """
        if self.inference_type_allow_list and inference_type not in self.inference_type_allow_list:
            raise ValueError(f"inference type: {inference_type} not in "
                             f"inference type allow list {self.inference_type_allow_list}")

        request = {
            'date': date.isoformat(),
            'season_id': season_id,
            'inference_type': inference_type,
            'zone_token': zone_token,
            'start_ts': str(start_ts) if start_ts else None,
            'end_ts': str(end_ts) if end_ts else None,
            'model_id': model_id,
            'model_name': model_name,
            'model_version': model_version,
            'git_repo_name': git_repo_name,
            'script_name': script_name,
            'git_description': git_description,
            'docker_image': docker_image,
            'pipeline_version': pipeline_version,
            'hparams': hparams
        }

        if inference_type and inference_type in self.inference_filters:
            request.update(**self.inference_filters[inference_type])

        for i in range(0, len(field_token), api_limit_size):
            request['field_token'] = field_token[i:i + api_limit_size]
            response: List = self.get(f'/inferences/field/latest', json=request)
            for inference in response:
                key = (
                    inference['field_token'], inference['season_id'],
                    inference['zone_token'], inference['inference_type']
                )
                yield key, inference

    def get_field_inference_types(self, field_token: str) -> List[str]:
        """Returns the inference types available for this field"""
        return self.get(f'/inferences/field/types/{field_token}')

    def get_field_tokens_with_inference_type(self, inference_type: str,
                                             api_limit_size: int = 10000) -> Generator[str, None, None]:
        """Returns a list of field tokens with an inference with the given inference type"""
        skip = 0
        while True:
            field_tokens = self.get(f'/inferences/field/tokens/{inference_type}?skip={skip}&limit={api_limit_size}')
            for field_token in field_tokens:
                yield field_token
            if len(field_tokens) == api_limit_size:
                skip += api_limit_size
            else:
                break

    def create_field_evaluation(self, inference_id: int, scores: dict, eval_type: str = 'default') -> dict:
        """Creates an evaluation for a field with the given parameters"""
        return self.post('/evaluations/field/', json={
            'inference_id': inference_id,
            'type': eval_type,
            'scores': scores,
        })

    def get_field_evaluation_by_id(self, field_evaluation_id: int) -> dict:
        """Returns an evaluation by id"""
        return self.get(f'/evaluations/field/{field_evaluation_id}')

    def get_field_evaluations(self, date: datetime = datetime.max, field_token: List[str] = None,
                              season_id: List[int] = None,
                              zone_token: List[str] = None, inference_type: str = None, model_id: int = None,
                              model_name: str = None, model_version: int = None, git_repo_name: str = None,
                              script_name: str = None, git_description: str = None, docker_image: str = None,
                              hparams: dict = None, inference_id: List[int] = None, eval_type: str = None,
                              api_limit_size: int = 100) -> Generator[dict, None, None]:
        """Generates a set of evaluations that match the provided filters"""
        skip = 0
        while True:
            evaluations = self.get(
                '/evaluations/field/',
                json={
                    'date': date.isoformat(),
                    'field_token': field_token,
                    'season_id': season_id,
                    'zone_token': zone_token,
                    'inference_type': inference_type,
                    'model_id': model_id,
                    'model_name': model_name,
                    'model_version': model_version,
                    'git_repo_name': git_repo_name,
                    'script_name': script_name,
                    'git_description': git_description,
                    'docker_image': docker_image,
                    'hparams': hparams,
                    'inference_id': inference_id,
                    'type': eval_type,
                },
                params={
                    'skip': skip,
                    'limit': api_limit_size,
                }
            )
            for evaluation in evaluations:
                yield evaluation
            if len(evaluations) == api_limit_size:
                skip += api_limit_size
            else:
                break

    def create_dataset_evaluation(self, dataset_id: int, model_id: int, scores: dict, hparams: dict, tags: dict = None,
                                  docker_image: str = None, pipeline_version: str = None) -> dict:
        """Creates an evaluation for the given dataset and model"""
        return self.post('/evaluations/dataset/', json={
            'dataset_id': dataset_id,
            'model_id': model_id,
            'scores': scores,
            'hparams': hparams,
            'tags': tags,
            'docker_image': docker_image,
            'pipeline_version': pipeline_version
        })

    def get_dataset_evaluation_by_id(self, dataset_evaluation_id: int) -> dict:
        """Returns a dataset evaluation by id"""
        return self.get(f'/evaluations/dataset/{dataset_evaluation_id}')

    def get_dataset_evaluations(self, model_id: id = None, docker_image: str = None, hparams: dict = None,
                                dataset_id: int = None, pipeline_version: str = None,
                                api_limit_size: int = 100) -> Generator[dict, None, None]:
        """Generates a set of dataset evaluations that match the given parameters"""
        skip = 0
        while True:
            evaluations = self.get(
                '/evaluations/dataset/',
                json={
                    'model_id': model_id,
                    'docker_image': docker_image,
                    'pipeline_version': pipeline_version,
                    'hparams': hparams,
                    'dataset_id': dataset_id,
                },
                params={
                    'skip': skip,
                    'limit': api_limit_size,
                }
            )
            for evaluation in evaluations:
                yield evaluation
            if len(evaluations) == api_limit_size:
                skip += api_limit_size
            else:
                break

    @staticmethod
    def _validate_flight(flight: dict) -> dict:
        if (
            (flight['planting_date'] or flight['gdd'] is not None or flight['days_after_planting'] is not None)
            and flight['planting_date_guessed'] is None
        ):
            raise ValueError("Must provide planting_date_guessed if providing planting date")

        if flight['crop_type'] and flight['crop_type_guessed'] is None:
            raise ValueError("Must provide crop_type_guessed if providing crop type")

        return {k: v.isoformat() if isinstance(v, datetime) else v for k, v in flight.items()}

    def create_flight(self, flight_code: str, date: Optional[datetime] = None, provider: Optional[str] = None,
                      planting_date: Optional[datetime] = None, planting_date_guessed: Optional[bool] = None,
                      gdd: Optional[float] = None, days_after_planting: Optional[int] = None,
                      days_after_emergence: Optional[int] = None, growth_stage: Optional[str] = None,
                      crop_type: Optional[str] = None, crop_type_guessed: Optional[bool] = None) -> dict:
        """Creates a flight with the ml service"""
        flight = {
            'flight_code': flight_code,
            'date': date,
            'provider': provider,
            'planting_date': planting_date,
            'planting_date_guessed': planting_date_guessed,
            'gdd': gdd,
            'days_after_planting': days_after_planting,
            'days_after_emergence': days_after_emergence,
            'growth_stage': growth_stage,
            'crop_type': crop_type,
            'crop_type_guessed': crop_type_guessed,
        }
        flight = self._validate_flight(flight)

        return self.post('/flight/', json=flight)

    def get_flight(self, flight_code: str) -> dict:
        """Gets a flight by flight code"""
        return self.get(f'/flight/{flight_code}')

    def update_flight(self, flight: dict) -> dict:
        """Updates a flight in the ml service"""
        flight = self._validate_flight(flight)
        return self.patch(f'/flight/', json=flight)

    def bulk_update_flights(self, flights: List[dict], api_limit_size: int = 100) -> None:
        """Does a bulk update for a list of flights"""
        parsed_flights = list()
        for flight in flights:
            parsed_flights.append(self._validate_flight(flight))

        for i in range(0, len(flights), api_limit_size):
            self.patch('/flight/bulk_update', json=parsed_flights[i:i + api_limit_size])

    def add_flights_to_dataset(self, dataset_id: int, flight_codes: List[str], split: Optional[str] = None,
                               api_limit_size: int = 1000):
        """Adds the given flights codes to the specified dataset with the given split"""
        for i in range(0, len(flight_codes), api_limit_size):
            self.post('/flight/add_to_dataset', json={
                'dataset_id': dataset_id,
                'flight_codes': flight_codes[i:i + api_limit_size],
                'split': split
            })

    def remove_flights_from_dataset(self, dataset_id: int, flight_codes: List[str], api_limit_size: int = 1000):
        """Removes the flight codes for the dataset"""
        for i in range(0, len(flight_codes), api_limit_size):
            self.delete('/flight/remove_from_dataset', json={
                'dataset_id': dataset_id,
                'flight_codes': flight_codes[i:i + api_limit_size]
            })

    def get_flight_datasets(self, flight_code: str, api_limit_size: int = 100) -> Dict[str, List[dict]]:
        """Gets all the datasets that contain this flight"""
        offset = 0
        final_results = defaultdict(list)
        while True:
            results = self.get(f'/flight/datasets',
                               json={
                                   'flight_code': flight_code,
                                   'offset': offset,
                                   'limit': api_limit_size,
                               })
            for split, datasets in results.items():
                final_results[split].extend(datasets)
            if sum([len(datasets) for datasets in results.values()]) == api_limit_size:
                offset += api_limit_size
            else:
                break
        return final_results
