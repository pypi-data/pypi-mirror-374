"""Planting service API wrapper class."""

import json
from datetime import datetime
from typing import Tuple, Union, List, Optional
from uuid import UUID

import shapely.geometry
import shapely.wkt
from pydantic import BaseModel, StrictInt, field_validator, ConfigDict

from intelinair_utils.api_wrapper import ApiWrapper


class PlantingServiceOperation(BaseModel):
    field_token: UUID
    season_id: StrictInt
    source: str  # SourceTypes enum: "USER", "MANUAL", "EQUIPMENT", "ANALYTICS"
    id: Optional[int] = None
    date: Optional[datetime] = None
    crop_types: Optional[List[str]] = None
    rate: Optional[int] = None
    geometry: Optional[Union[shapely.geometry.MultiPolygon, shapely.geometry.Polygon]] = None
    coverage_percentage: Optional[float] = None
    hybrid: Optional[str] = None
    active_date_range: Optional[Tuple[datetime, Union[datetime, None]]] = None
    is_active: Optional[bool] = None
    planted: Optional[bool] = None
    author: Optional[str] = None
    operation_id: Optional[UUID] = None
    date_created: Optional[datetime] = None
    replanted: Optional[bool] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={
            shapely.geometry.MultiPolygon: lambda s: shapely.geometry.mapping(s) if s else None,
            shapely.geometry.Polygon: lambda s: shapely.geometry.mapping(s) if s else None,
        }
    )

    @field_validator('rate', mode='before')
    def coerce_fractional_rate_to_int(cls, value):
        """Coerce fractional rate to int."""
        if value is None:
            return None
        try:
            return int(float(value))
        except (ValueError, TypeError):
            raise ValueError(f"Invalid value for rate: {value}. Must be a number or a string representing a number.")

    @field_validator('geometry', mode='before')
    @classmethod
    def parse_geometry(cls, value):
        if value:
            if isinstance(value, shapely.geometry.MultiPolygon) or isinstance(value, shapely.geometry.Polygon):
                return value
            elif isinstance(value, str):
                return shapely.wkt.loads(value)
            elif isinstance(value, dict):
                return shapely.geometry.shape(value)
            raise ValueError(f"Could not parse geometry: {value}")

    def dict_jsonable(self):
        """Return dictionary which is serializable to json."""
        return json.loads(self.model_dump_json())


class PlantingServiceApi(ApiWrapper):
    """Planting service API class."""
    PLANTING_SERVICE_URLS = {
        "bellflower": "https://53h6dpom55.execute-api.us-east-1.amazonaws.com/api",
        "longview": "https://1hqmp8xg3l.execute-api.us-east-1.amazonaws.com/api/",
        "release": "https://ulliupxcdd.execute-api.us-east-1.amazonaws.com/api",
        "platform": "https://oczjs0gwu3.execute-api.us-east-1.amazonaws.com/api",
        "prod": "https://b3on5xa1fd.execute-api.us-east-1.amazonaws.com/api"
    }

    def __init__(self, environment: str, config_path: Optional[str] = None):
        super().__init__(environment, self._get_api_urls(), config_path=config_path)

    def _get_api_urls(self):
        """Overridden method for getting planting service API gateway URLs."""
        return self.PLANTING_SERVICE_URLS

    def get_all_planting_operations(
        self,
        field_token: Union[str, UUID],
        season_id: Union[int, str]
    ) -> List[PlantingServiceOperation]:
        """
        Get all planting operations of field during given season.
        Args:
            field_token: unique field identifier string.
            season_id: id of season for which field is checked.
        Returns:
            List of planting operations.
        """
        url = self.url_template.format(f"all-planting-operations/{field_token}/{season_id}")
        response = self._custom_chunked_get(url)
        return [PlantingServiceOperation(**resp_po) for resp_po in response]

    def get_active_planting_operation(
        self,
        field_token: Union[str, UUID],
        season_id: Union[int, str]
    ) -> PlantingServiceOperation:
        """
        Get current active(default) planting operation based on predefined priorities.
        Args:
            field_token: unique field identifier string.
            season_id: id of season for which field is checked.
        Returns:
            Default planting operation data.
        """
        url = self.url_template.format(f"planting-date/{field_token}/{season_id}")
        response = self._make_request(self.session.get, url)
        response.raise_for_status()
        return PlantingServiceOperation(**response.json())

    def is_planted(self, field_token: Union[str, UUID], season_id: Union[int, str]):
        """
        Check field is planted in given season or not.
        Args:
            field_token: unique field identifier string.
            season_id: id of season for which field is checked.
        Returns:
            Boolean response.
        """
        url = self.url_template.format(f"is-planted/{field_token}/{season_id}")
        response = self._make_request(self.session.get, url)
        response.raise_for_status()
        return response.json()

    def set_not_planted(self, field_token: Union[str, UUID], season_id: Union[int, str]) -> PlantingServiceOperation:
        """
        Set field as not planted.
        Args:
            field_token: unique field identifier string.
            season_id: id of season for which field is used.
        Returns:
            Created Planting Operation.
        """
        url = self.url_template.format(f"not-planted/{field_token}/{season_id}")
        response = self._make_request(self.session.post, url)
        response.raise_for_status()
        return PlantingServiceOperation(**response.json())

    def create_planting_operation(self, planting_op: PlantingServiceOperation) -> PlantingServiceOperation:
        """
        Creating single planting operation.
        Args:
            planting_op: data dictionary of new planting operation.
        """
        url = self.url_template.format("add-planting-operation")
        response = self._make_request(self.session.post, url, json=planting_op.dict_jsonable())
        response.raise_for_status()
        return PlantingServiceOperation(**response.json())

    def create_bulk_planting_operations(
        self, bulk_planting_ops: List[PlantingServiceOperation]
    ) -> List[PlantingServiceOperation]:
        """
        Creating planting operations in bulk.
        Args:
            bulk_planting_ops: list of dicts with new operations data.
        """
        url = self.url_template.format("add-bulk-planting-operation")
        response = self._make_request(self.session.post, url, json=[po.dict_jsonable() for po in bulk_planting_ops])
        response.raise_for_status()
        return [PlantingServiceOperation(**resp_po) for resp_po in response.json()]

    def update_planting_operation(
        self, updated_planting_operation: PlantingServiceOperation
    ) -> PlantingServiceOperation:
        """
        Update existing planting operation by ID.
        Args:
            updated_planting_operation: it should not include any data which will change planting operation itself
            e.g. (source, field_token etc.), so we that data is filtered.
        Returns:
            Updated planting operation.
        """
        url = self.url_template.format(f"planting-operations/{updated_planting_operation.id}")
        changeable_fields = ['geometry', 'rate', 'coverage', 'crop_types', 'replanted']
        payload = updated_planting_operation.dict_jsonable()
        payload = {key: value for key, value in payload.items() if key in changeable_fields}
        payload['geometry'] = json.dumps(payload['geometry'])
        response = self._make_request(self.session.patch, url, json=payload)
        response.raise_for_status()
        return PlantingServiceOperation(**response.json())

    def get_planting_priorities(self) -> dict:
        """
        Gets planting priorities.
        Returns:
            planting priorities.
        """
        url = self.url_template.format(f"priorities-config")
        response = self._make_request(self.session.get, url)
        response.raise_for_status()

        return response.json()
