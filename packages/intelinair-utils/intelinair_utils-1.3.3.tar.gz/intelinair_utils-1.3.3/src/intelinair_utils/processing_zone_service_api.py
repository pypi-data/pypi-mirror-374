"""Processing Zone service API wrapper class."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Union, get_type_hints, Optional
from urllib.parse import urlencode
from uuid import UUID

from intelinair_utils.api_wrapper import ApiWrapper


@dataclass
class ProcessingZone:  # pylint: disable=too-many-instance-attributes
    """Processing Zone dataclass.
    
    Used for type hinting and data validation.
    """
    field_token: UUID
    season_id: int
    id: int = None  # pylint: disable=invalid-name
    token: UUID = None
    version: int = None
    date_created: datetime = None
    last_updated: datetime = None
    dates_active: Dict[str, Any] = None
    is_active: bool = None
    zone_type: str = None
    operation_date: datetime = None
    operation_type: str = None
    geometry: Dict[str, Any] = None
    parent: int = None
    extras: Dict[Any, Any] = None

    @classmethod
    def get_instance(cls, data: Dict[str, Any]) -> 'ProcessingZone':
        """Get ProcessingZone instance from dictionary.

        Args:
            data: Dictionary containing data.

        Returns:
            ProcessingZone instance.
        """
        class_properties = get_type_hints(cls)
        deserialized_properties = {}
        for attr, type_ in class_properties.items():
            try:
                if type_ == datetime:
                    if isinstance(data[attr], str):
                        value = datetime.fromisoformat(data[attr])
                    elif isinstance(data[attr], (datetime, type(None))):
                        value = data[attr]
                    else:
                        raise TypeError(f'{attr} must be a datetime or string')
                elif type_ == UUID:
                    if isinstance(data[attr], str):
                        value = UUID(data[attr])
                    elif isinstance(data[attr], (UUID, type(None))):
                        value = data[attr]
                    else:
                        raise TypeError(f'{attr} must be a UUID or string')
                else:
                    value = data[attr]
            except KeyError:
                continue
            deserialized_properties[attr] = value
        return cls(**deserialized_properties)

    def _serialize(self, value: Any) -> Any:
        """Serialize value to JSON compatible type.

        Args:
            value (Any): Value to serialize.

        Returns:
            Any: Serialized value.
        """
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, UUID):
            return str(value)
        return value

    def to_dict(self) -> Dict[str, Any]:
        """Convert dataclass to dictionary.
        """
        return {
            key: self._serialize(value)
            for key, value in self.__dict__.items()
            if value is not None
        }

    def patched_dict(self, **kwargs) -> Dict[str, Any]:
        """Convert dataclass to dictionary and patch with kwargs.
        """
        data = self.to_dict()
        for key, value in kwargs.items():
            data[key] = self._serialize(value)
        return data


class ProcessingZoneServiceApiError(Exception):
    """Processing Zone service API error class."""
    error_code: str = None
    status_code: int = None

    def __init__(self, message: str, error_code: str = None, status_code: int = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code

    def __str__(self) -> str:
        return f'[HTTP {self.status_code}] {self.error_code} ({self.message})'

    def __repr__(self) -> str:
        return f'ProcessingZoneServiceApiError({self.status_code}, {self.error_code}, {self.message})'


class ProcessingZoneServiceApi(ApiWrapper):
    """Processing Zone service API class."""

    PROCESSING_ZONE_SERVICE_URLS = {
        "bellflower": "https://processing-zone-service.bellflower.int.intelinair.dev/api",
        "prod": "https://processing-zone-service.prod.int.intelinair.dev/api",
        "platform": "https://processing-zone-service.platform.int.intelinair.dev/api",
        "release": "https://processing-zone-service.release.int.intelinair.dev/api"
    }

    def __init__(self, environment: str, config_path: Optional[str] = None):
        super().__init__(environment, self._get_api_urls(), config_path=config_path)

    def _get_api_urls(self):
        """Overridden method for getting planting service API gateway URLs."""
        return self.PROCESSING_ZONE_SERVICE_URLS

    def _make_request(self, http_method, *args, **kwargs):
        response = super()._make_request(http_method, *args, **kwargs)
        if response.status_code < 200 or response.status_code >= 300:
            error_response = response.json()
            raise ProcessingZoneServiceApiError(error_response.get('Message'),
                                                error_response.get('Code'),
                                                response.status_code)
        return response

    def get_zones_for_date(
        self,
        field_token: str,
        season_id: Union[int, str],
        flight_date: datetime
    ) -> List[ProcessingZone]:
        """Get processing zones for a given date.

        Retrieves the active processing zones for a given date. In scenarios
        where there are replant zones, the replant zones will be returned
        only when the flight date is after the replant date.

        Args:
            field_token: the token of the field
            season_id: Season ID.
            flight_date: Flight date.
        
        Returns:
            List[ProcessingZone]: List of processing zones.
        """
        query_params = urlencode({
            'flight_date': flight_date.isoformat(),
            'season_id': season_id,
            'field_token': field_token
        })
        url = self.url_template.format(f"zones-for-date?{query_params}")
        response = self._make_request(self.session.get, url)
        zones = [ProcessingZone.get_instance(zone) for zone in response.json().get('zones', [])]
        return zones

    def get_latest_zones(
        self,
        field_token: str,
        season_id: Union[int, str]
    ) -> List[ProcessingZone]:
        """Get latest processing zones for a given field and season.

        Args:
            field_token (str): Field token.
            season_id (Union[int, str]): Season ID.

        Returns:
            List[ProcessingZone]: List of processing zones.
        """
        query_params = urlencode({
            'season_id': season_id,
            'field_token': field_token
        })
        url = self.url_template.format(f"zones/latest?{query_params}")
        response = self._make_request(self.session.get, url)
        zones = [ProcessingZone.get_instance(zone) for zone in response.json().get('zones', [])]
        return zones

    def get_latest_zones_by_type(
        self,
        field_token: str,
        season_id: Union[int, str],
        zone_type: str
    ) -> List[ProcessingZone]:
        """Get latest processing zones for a given field and season of a given type.

        Args:
            field_token: Field token.
            season_id: Season ID.
            zone_type: the type of the zone

        Returns:
            List[ProcessingZone]: List of processing zones.
        """
        query_params = urlencode({
            'season_id': season_id,
            'field_token': field_token,
            'zone_type': zone_type
        })
        url = self.url_template.format(f"zones/latest?{query_params}")
        response = self._make_request(self.session.get, url)
        zones = [ProcessingZone.get_instance(zone) for zone in response.json().get('zones', [])]
        return zones

    def get_zone_by_token(self, zone_token: str) -> Optional[ProcessingZone]:
        """Get processing zone for given zone token.
        Args:
            zone_token: Processing Zne token.

        Returns:
            List of processing zones.
        """
        query_params = urlencode({
            'token': zone_token
        })
        url = self.url_template.format(f"zones?{query_params}")
        response = self._make_request(self.session.get, url)
        zones = response.json().get('zones', [])
        if len(zones) == 0:
            return None
        # take last zone in case there are multiple zones with same token (revision)
        zones.sort(key=lambda x: x['version'], reverse=False)
        zone = ProcessingZone.get_instance(zones.pop())
        return zone

    def revise(
        self,
        field_token: UUID,
        season_id: int,
        zones: List[ProcessingZone]
    ) -> List[ProcessingZone]:
        """Revise processing zones for the given field.
        
        Args:
            field_token: Field token.
            season_id: Season ID.
            zones: List of processing zones.

        Returns:
            List of revised processing zones.
        """
        field_season = {
            'season_id': season_id,
            'field_token': field_token
        }
        url = self.url_template.format(f"zones")
        message_body = {
            'field_token': str(field_token),
            'season_id': season_id,
            'zones': [zone.patched_dict(**field_season) for zone in zones],
        }
        response = self._make_request(self.session.put, url, json=message_body)
        zones = [ProcessingZone.get_instance(zone) for zone in response.json().get('zones', [])]
        return zones

    def create(
        self,
        field_token: UUID,
        season_id: int,
        zones: List[ProcessingZone]
    ) -> List[ProcessingZone]:
        """Create processing zones for a given date.

        Args:
            field_token: Field token.
            season_id: Season ID.
            zones: List of processing zones.

        Returns:
            List of created processing zones.
        """
        field_season = {
            'season_id': season_id,
            'field_token': field_token
        }
        url = self.url_template.format("zones")
        data = [zone.patched_dict(**field_season) for zone in zones]
        response = self._make_request(self.session.post, url, json=data)
        return [ProcessingZone.get_instance(zone) for zone in response.json().get('zones', [])]
