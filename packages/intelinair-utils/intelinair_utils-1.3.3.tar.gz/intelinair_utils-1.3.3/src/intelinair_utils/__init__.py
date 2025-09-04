from .__version__ import __version__
from .agmri_api import AgmriApi
from .alert_service_api import AlertServiceApi
from .ec2_utils import *
from .efs_utils import *
from .error_logger import ErrorLogger
from .flight_service_api import FlightServiceApi, AERIAL, EQUIPMENT, IMAGERY
from .integration_service_api import IntegrationServiceApi
from .logging_utils import *
from .ml_api import MLApi
from .os_utils import *
from .pipeline_stats_api import PipelineStatsApi
from .processing_zone_service_api import ProcessingZoneServiceApi, ProcessingZone
from .s3_utils import *
from .ssm_utils import *
from .vector_tile_service_api import VectorTileServiceApi
from .weather_api import WeatherApi
from .efs_utils import get_available_efses, get_available_efses_from_s3
try:
    from .annotations_api import AnnotationsApi
    from .planting_service_api import PlantingServiceApi, PlantingServiceOperation
    from .elevation_metadata_service_api import ElevationMetadataServiceApi
except ImportError:
    import logging
    logger = logging.getLogger('intelinair_utils')
    logger.warning("The optional dependency 'shapely' is missing, which means certain functionalities "
                   "(such as AnnotationsApi) will be unavailable. To enable these features, install 'shapely' "
                   "by running: pip install intelinair_utils[shapely].")
