"""Planting service API wrapper class."""

from typing import Dict, List, Optional

from intelinair_utils.api_wrapper import ApiWrapper


class VectorTileServiceApi(ApiWrapper):
    """Planting service API class."""
    VECTOR_TILE_SERVICE_URLS = {
        "bellflower": "https://pi0m191jpc.execute-api.us-east-1.amazonaws.com/api",
        "release": "https://4yboi7re8i.execute-api.us-east-1.amazonaws.com/api",
        "prod": "https://3qs6tciagc.execute-api.us-east-1.amazonaws.com/api",
    }

    S3_CACHE_PATHS = {
        "bellflower": "s3://intelinair-dev-private/bellflower/apicache/vector-tile-service",
        "release": "s3://intelinair-stage-private/release/apicache/vector-tile-service",
        "prod": "s3://intelinair-prod-private/prod/apicache/vector-tile-service",
    }

    def __init__(self, environment: str, config_path: Optional[str] = None):
        super().__init__(environment, self._get_api_urls(), config_path=config_path)

    def _get_api_urls(self):
        """Overriden method for getting planting service API gateway URLs."""
        return self.VECTOR_TILE_SERVICE_URLS

    def get_s3_cache_paths(self):
        """Overriden method for getting planting service S3 cache paths."""
        return self.S3_CACHE_PATHS

    def create_vector_tile(self, data: Dict):
        """
        Method for creating tile geometry along with metadata and properties
        Args:
            data: data is a dictionary of keys
            such as geometry, properties, metadata

        Returns:
            token
        """
        url = self.url_template.format(f"polygon")
        response = self._make_large_body_request(self.session.post, url, json=data)

        return response.json()

    def get_tile_mvt(self, token, z, x, y):
        """
        Methods for transforming hex-geometry to MVT
        Args:
            token: unique identifier for a tile (UUID)
            x, y, z : MVT coordinates

        Returns:
            MVT transformed geometry
        """
        url = self.url_template.format(f"polygon/{token}/{z}/{x}/{y}")
        response = self._make_request(self.session.get, url)

        return response

    def get_tile_geometry(self, token: str):
        """
        Methods that fetches geometry of a tile in geojson
        Args:
            token: unique identifier for a tile (UUID)

        Returns:
            geometry of a vector tile
            properties

        """
        url = self.url_template.format(f"polygon/{token}")
        json_response = self._custom_chunked_get(url)
        return json_response

    def get_tile_metadata(self, token):
        """
        Method that fetches metadata of a vector tile
        Args:
            token: unique identifier for a tile (UUID)

        Returns:
            vector tile metadata

        """
        url = self.url_template.format(f"polygon/{token}/metadata")
        response = self._make_request(self.session.get, url)

        return response.json()

    def create_feature_collection(self, features: List[Dict], metadata: Dict = None) -> Dict:
        """
        Creates a feature collection
        Args:
            features: list of geojson features

        Returns:
            response from the API
        """
        url = self.url_template.format("feature-collections")
        payload = {
            "features": features,
            "meta_data": metadata
        }
        response = self._make_large_body_request(self.session.post, url, json=payload)
        return response.json()

    def get_feature_collection(self, token: str) -> Dict:
        """
        Retrieves a feature collection for a given token
        Args:
            token: unique identifier for a feature collection

        Returns:
            feature collection resource (not to be confused with geojson feature collection format)

        """
        url = self.url_template.format(f"feature-collections/{token}")
        json_response = self._custom_chunked_get(url)

        return json_response
