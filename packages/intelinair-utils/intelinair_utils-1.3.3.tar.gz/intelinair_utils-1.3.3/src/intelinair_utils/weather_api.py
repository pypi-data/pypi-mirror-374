import datetime
from typing import Dict, List, Optional, Tuple

import pytz
import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from intelinair_utils.agmri_api import AgmriApi


class WeatherApi:
    """Special class for working getting weather data."""

    DAILY_REQUEST_KEY = 'historicalDaily'
    HOURLY_REQUEST_KEY = 'historicalHourly'
    DAY_KEY = 'day'
    HOUR_KEY = 'hour'

    def __init__(self, api: AgmriApi, number_of_retries: int = 3) -> None:
        """Class responsible for communication with weather service."""
        self._api = api
        self._weather_url_fmt = self._get_weather_observation_url()

        retries = Retry(
            total=number_of_retries, read=number_of_retries, connect=number_of_retries,
            backoff_factor=1, allowed_methods=False,
            status_forcelist=[409] + list(range(500, 600))
        )
        self._session = requests.session()
        self._session.mount('https://', HTTPAdapter(max_retries=retries))

    def get_daily(
        self,
        longitude: float,
        latitude: float,
        start_date: datetime.date,
        end_date: datetime.date,
        timezone: str,
        features: List = None
    ) -> List[Dict]:
        """Get weather daily data.

            Args:
                longitude: longitude for which weather data is needed
                latitude: latitude for which weather data is needed
                start_date: weather data will be provided from this time point
                end_date: weather data will be provided up to this time point
                timezone: the timezone for which the data should be fetched, basically it should represent the
                           timezone of the lat and lng
                features: list of features to return. If None all features in response are returned.
            Returns:
                list with dicts with features for each day.
        """
        start_datetime = datetime.datetime(start_date.year, start_date.month, start_date.day)
        end_datetime = datetime.datetime(end_date.year, end_date.month, end_date.day)

        start_timestamp, end_timestamp = self._get_start_end_timestamp(timezone, start_datetime, end_datetime)
        response = self._make_request(self.DAILY_REQUEST_KEY, longitude, latitude, start_timestamp, end_timestamp)
        return self._parse_response(self.DAY_KEY, response=response, features=features)

    def get_hourly(
        self,
        longitude: float,
        latitude: float,
        start_datetime: datetime,
        end_datetime: datetime,
        timezone: str,
        features: List = None
    ) -> List[Dict]:
        """Get weather hourly data.

            Args:
                longitude: longitude for which weather data is needed
                latitude: latitude for which weather data is needed
                start_datetime: weather data will be provided from this time point
                end_datetime: weather data will be provided up to this time point
                timezone: the timezone for which the data should be fetched, basically it should represent the
                          timezone of the lat and lng
                features: list of features to return. If None all features in response are returned.
            Returns:
                list with dicts with features for each hour
        """
        start_timestamp, end_timestamp = self._get_start_end_timestamp(timezone, start_datetime, end_datetime)
        response = self._make_request(self.HOURLY_REQUEST_KEY, longitude, latitude, start_timestamp, end_timestamp)
        return self._parse_response(self.HOUR_KEY, response=response, features=features)

    def features_list(self, daily: bool) -> List:
        """Get possible features list for weather api"""
        response = self._api.make_request(
            self._api.session.get,
            self._get_weather_feature_url(),
            headers={'Content-Type': 'application/json'}
        )
        if daily:
            request_key = self.DAILY_REQUEST_KEY
            added_key = self.DAY_KEY
        else:
            request_key = self.HOURLY_REQUEST_KEY
            added_key = self.HOUR_KEY

        scheme = response['paths'][f'/weather-observation/{request_key}']['get']['responses']['200']
        property_key = scheme['content']['application/json']['schema']['items']['$ref'].split('/')[-1]
        features = list(response['components']['schemas'][property_key]['properties'].keys())
        features.append(added_key)

        if 'id' in features:
            features.remove('id')

        return features

    def _get_weather_observation_url(self) -> str:
        """Returns url with which weather data is requested."""
        observation_request_fmt = (
            '/weather-observation/{granularity}?'
            'longitude={longitude}&latitude={latitude}&'
            'dateFrom={start_timestamp}&dateTo={end_timestamp}'
        )
        return self._get_weather_url() + observation_request_fmt

    def _get_weather_feature_url(self) -> str:
        return self._get_weather_url() + '/swagger/swagger.json'

    def _get_weather_url(self) -> str:
        """Get weather base Url"""
        return f"{'/'.join(self._api.api_url.split('/')[:-3])}/weather"

    @staticmethod
    def _get_start_end_timestamp(
        timezone: str,
        start_datetime: datetime.datetime,
        end_datetime: datetime.datetime
    ) -> Tuple[int, int]:
        """Returns the start and end timestamps in a given timezone."""
        if start_datetime.tzinfo is not None or end_datetime.tzinfo is not None:
            raise ValueError("start_datetime and end_datetime must be native, aka without timezone info")

        time_zone_obj = pytz.timezone(timezone)
        start_timestamp = int(time_zone_obj.localize(start_datetime).timestamp() * 1000)
        end_timestamp = int(time_zone_obj.localize(end_datetime).timestamp() * 1000)
        return start_timestamp, end_timestamp

    @staticmethod
    def _parse_response(key: str, response: List, features: Optional[List[str]] = None) -> List[Dict]:
        """Parses the response."""
        result = []
        for item in response:
            item_timestamp = int(item['validTimeLocal'])
            item_result = {f: item.get(f) for f in features} if features else item
            item_result[key] = item_timestamp
            result.append(item_result)
        return result

    def _make_request(
        self,
        granularity: str,
        longitude: float,
        latitude: float,
        start_timestamp: int,
        end_timestamp: int
    ) -> List[Dict]:
        """Get weather data.

            Args:
                granularity: either historicalHourly or historicalDaily
                longitude: longitude for which weather data is needed
                latitude: latitude for which weather data is needed
                start_timestamp: get weather data from this timestamp
                end_timestamp: get weather data up to this timestamp
            Returns:
                list of dicts with features key/values as values.
        """
        return self._api.make_request(
            self._session.get,
            self._weather_url_fmt.format(
                granularity=granularity,
                longitude=longitude,
                latitude=latitude,
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp
            ),
            headers=self._api.headers['processing']
        )
