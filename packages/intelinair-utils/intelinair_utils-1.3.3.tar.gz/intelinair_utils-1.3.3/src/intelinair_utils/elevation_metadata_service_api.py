"""Planting service API wrapper class."""

import json
from typing import Union, Optional

from shapely import wkt
import shapely.geometry
import shapely.wkt
from pydantic import BaseModel, field_validator, ConfigDict

from intelinair_utils.api_wrapper import ApiWrapper



class Geometry(BaseModel):
    """Model for geometry data supporting multiple formats."""
    geometry: Optional[Union[shapely.geometry.MultiPolygon, shapely.geometry.Polygon, dict, str]]

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={
            shapely.geometry.MultiPolygon: lambda s: shapely.geometry.mapping(s) if s else None,
            shapely.geometry.Polygon: lambda s: shapely.geometry.mapping(s) if s else None,
        }
    )

    @field_validator('geometry', mode='before')
    @classmethod
    def parse_geometry(cls, value):
        """Validate geometry as either WKT, GeoJSON, or a shapely object."""
        return cls.validate_geometry(value)

    def dict_jsonable(self):
        """Return dictionary which is serializable to json."""
        return json.loads(self.model_dump_json())

    @classmethod
    def validate_geometry(cls, value):
        """Validates that the geometry is a valid Polygon, MultiPolygon, WKT, or GeoJSON."""
        if value:
            if isinstance(value, (shapely.geometry.MultiPolygon, shapely.geometry.Polygon)):
                return value
            elif isinstance(value, str):
                try:
                    shapely.wkt.loads(value)  # Validate as WKT string
                except shapely.errors.WKTReadingError:
                    raise ValueError(f"Invalid WKT string: {value}")
            elif isinstance(value, dict):
                try:
                    shapely.geometry.shape(value)  # Validate as GeoJSON dictionary
                except (TypeError, ValueError):
                    raise ValueError(f"Invalid GeoJSON dictionary: {value}")
            else:
                raise ValueError(f"Unsupported geometry type: {type(value).__name__}")
        return value


class ElevationTile(Geometry):
    """Model for elevation data."""
    name: str
    s3_path: str
    north_east_latitude: float
    north_east_latitude: float
    north_east_longitude: float
    south_west_latitude: float
    south_west_longitude: float
    resolution: float
    country: str
    geometry: Optional[Union[shapely.geometry.MultiPolygon, shapely.geometry.Polygon, dict, str]]

    @field_validator('geometry', mode='before')
    @classmethod
    def parse_geometry(cls, value):
        """Validate geometry as either WKT, GeoJSON, or a shapely object."""
        return cls.validate_geometry(value)


class ElevationMetadataServiceApi(ApiWrapper):
    """API wrapper for interacting with the Elevation Metadata Service."""

    ELEVATION_METADATA_SERVICE_URLS = {
        "prod": "https://utl43kq9za.execute-api.us-east-1.amazonaws.com/api",
        "release": "https://p8u69ef8d4.execute-api.us-east-1.amazonaws.com/api",
        "longview": "https://i7upioahk4.execute-api.us-east-1.amazonaws.com/api",
    }

    def __init__(self, environment: str, config_path: Optional[str] = None):
        super().__init__(environment, self._get_api_urls(), config_path=config_path)

    def _get_api_urls(self):
        """Overridden method for getting elevation metadata service API gateway URLs."""
        return self.ELEVATION_METADATA_SERVICE_URLS

    def create_tile(self, elevation_tile: ElevationTile):
        """Create a new elevation tile and return the created ElevationTile object."""
        url = self.url_template.format("create-tile-info")
        response = self._make_request(self.session.post, url, json=elevation_tile.dict_jsonable())
        response.raise_for_status()
        return ElevationTile(**response.json())

    def get_tiles_s3_paths_by_lonlat(self, ne_lat, ne_lon, sw_lat, sw_lon):
        """Retrieve S3 paths of tiles intersecting the specified latitude and longitude bounds."""
        url = self.url_template.format(f"/get-intersected-tiles-by-lonlat/{ne_lat}/{ne_lon}/{sw_lat}/{sw_lon}")
        response = self._make_request(self.session.get, url)
        response.raise_for_status()
        return response.json()

    def get_tiles_s3_paths_by_geom(self, geometry: Geometry):
        """Retrieve S3 paths of tiles intersecting the specified geometry."""
        url = self.url_template.format("get-intersected-tiles-by-geom")
        response = self._make_request(self.session.post, url, json=geometry.dict_jsonable())
        response.raise_for_status()
        return response.json()

    def get_tile_by_name(self, tile_name: str):
        """Retrieve tile info by name."""
        url = self.url_template.format(f"get-tile-info/{tile_name}")
        response = self._make_request(self.session.get, url)
        response.raise_for_status()
        return response.json()
