import copy


class Map:
    def __init__(self, dictionary):
        d = {}
        for k, v in dictionary.items():
            d[k] = Map(v) if isinstance(v, dict) else v
        self.__dict__.update(d)

    def __repr__(self):
        return self.__dict__.__repr__()

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        if isinstance(value, dict):
            value = Map(value)
        self.__dict__[key] = value

    def __contains__(self, item):
        return item in self.__dict__

    def __copy__(self):
        return Map(self.__dict__.copy())

    def copy(self):
        return copy.copy(self)

    def to_dict(self):
        return self.__dict__.copy()


CONFIG_JSON_ = {
    "indices": {
        "scaling_coefficients": {
            "nir": 0.69,
            "red": 1,
            "green": 1.09,
        },
        "scale_rgb_brightness": True,
        "percentiles": {
            "red": {"low": 2, "high": 98},
            "green": {"low": 2, "high": 98},
            "blue": {"low": 1, "high": 99},
            "nir": {"low": 2, "high": 98},
        },
        "clip_ranges": {},
    },
    "veg_rows": {
        "fft_threshold": {
            "NDVI": 0.0001,
            "SciNDVI": 0.0004,
            "ExG": 0.015,
            "NIR": 0.00001,
            "GNDVI": 0.0001,
            "GREEN": 0.00001,
        },
        "veg_indices": ["NIR", "NDVI", "GREEN"],
        "max_distance": 150,
        "should_use_rgb_for_red_green": True
    },
    "change": {"veg_index": "NDVI", "compute_method": "diff", "blur_size": 450},
    "ndvi_anomaly": {
        "boundary_mask_erosion_in_cm": 500,
        "averaging_box_size": 450,
        "mean_range": [0.59, 0.61],
        "steps": [0.02, 0.06, 0.18],
        "soil_averaging_box_size": 15000,  # 150m
        "soil_ndvi_resize_factor": 4,  # should be integer
        "soil_correction_coefficient": 4,
        "locality_averaging_box_size": 0,  # global anomalies
        "locality_resize_factor": 8,  # should be integer
        "min_areas": {1: 1800, 2: 1400, 3: 1000},  # ~0.005 acres under ~10cm resolution
        "contour_config": {
            "tolerance": 0.1,
            "bezier": True,
        },
    },
    "gndvi_anomaly": {
        "boundary_mask_erosion_in_cm": 500,
        "averaging_box_size": 350,
        "mean_range": [0.59, 0.61],
        "steps": [0.03, 0.09, 0.27],
        "soil_averaging_box_size": 15000,  # 150m
        "soil_ndvi_resize_factor": 4,  # should be integer
        "soil_correction_coefficient": 0,  # no soil correction
        "locality_averaging_box_size": 0,  # global anomalies
        "locality_resize_factor": 8,  # should be integer
        "min_areas": {1: 1800, 2: 1400, 3: 1000},  # ~0.005 acres under ~10cm resolution
        "contour_config": {"tolerance": 0.1, "bezier": True},  # was 0.15
    },
    "thermal_local_anomaly": {
        "boundary_mask_erosion_in_cm": 500,
        "averaging_box_size": 450,
        "mean_range": [0.49, 0.51],
        "steps": [100, 300, 900],
        "soil_averaging_box_size": 15000,  # 150m
        "soil_ndvi_resize_factor": 4,  # should be integer
        "soil_correction_coefficient": 0,  # no soil correction
        "locality_averaging_box_size": 50000,  # 500m
        "locality_resize_factor": 10,  # should be integer
        "min_areas": {1: 1800, 2: 1800, 3: 1800},  # ~0.005 acres under ~10cm resolution
        "contour_config": {"tolerance": 0.1, "bezier": True},
    },
    "ndvi_anomaly_on_rows": {
        "boundary_mask_erosion_in_cm": 500,
        "apply_row_mask": True,
        "averaging_box_size": 450,
        "mean_range": [0.59, 0.61],
        "steps": [0.02, 0.06, 0.18],
        "soil_averaging_box_size": 15000,  # 150m
        "soil_ndvi_resize_factor": 4,  # should be integer
        "soil_correction_coefficient": 0,  # when rows are visible, soil effect is negligible
        "locality_averaging_box_size": 0,  # global anomalies
        "locality_resize_factor": 8,  # should be integer
        "min_areas": {1: 1800, 2: 1400, 3: 1000},  # ~0.005 acres under ~10cm resolution
        "contour_config": {"tolerance": 0.1, "bezier": True},
    },
    "gndvi_anomaly_on_rows": {
        "boundary_mask_erosion_in_cm": 500,
        "apply_row_mask": True,
        "averaging_box_size": 350,
        "mean_range": [0.59, 0.61],
        "steps": [0.03, 0.09, 0.27],
        "soil_averaging_box_size": 15000,  # 150m
        "soil_ndvi_resize_factor": 4,  # should be integer
        "soil_correction_coefficient": 0,  # no soil correction
        "locality_averaging_box_size": 0,  # global anomalies
        "locality_resize_factor": 8,  # should be integer
        "min_areas": {1: 1800, 2: 1400, 3: 1000},  # ~0.005 acres under ~10cm resolution
        "contour_config": {"tolerance": 0.1, "bezier": True},  # was 0.15
    },
    "weed_heatmap": {"cluster_distance": 1, "max_acceptable_area": None},  # in meters
    "stand_count": {
        "contour_config": {
            "tolerance": 0.1,  # was 0.5 or 0.3
            "bezier": True,
        }
    },
    "stand_count_no_rows": {
        "contour_config": {"tolerance": 0.1, "bezier": False}
    },
    "sparse_weed_detection": {"extra_args": {"extra_nodata_masks": ["waterway_detection:waterway_mask"]}},
    "equipment_application_dates": {"min_days_passed": 7, "max_days_passed": 21},
}

SEPERATED_CROPS = ["coffee"]


class AgmriConfig(Map):
    def __init__(self, crop_type=None):
        super().__init__(CONFIG_JSON_)
        self.indices.clip_ranges = {}
        if crop_type and crop_type in SEPERATED_CROPS:
            self.ndvi_anomaly = self.ndvi_anomaly_on_rows.copy()
            self.thermal_local_anomaly.apply_row_mask = True


class Sentinel2Config(AgmriConfig):
    def __init__(self, crop_type):
        super().__init__(crop_type)

        self.ndvi_anomaly.averaging_box_size = 0
        self.ndvi_anomaly.soil_correction_coefficient = 0
        self.ndvi_anomaly.locality_resize_factor = 1
        self.ndvi_anomaly.min_areas = {
            1: 180,  # The images are being upsampled by 10x for anomaly detection.
            2: 140,  # If the factor changes need to change here as well. Was 18 before
            3: 100,
        }


class MicasenseConfig(AgmriConfig):
    def __init__(self, crop_type):
        super().__init__(crop_type)

        self.ndvi_anomaly.min_areas = {1: 5400, 2: 4200, 3: 3000}

        self.ndvi_anomaly_on_rows.min_areas = {1: 5400, 2: 4200, 3: 3000}
        self.veg_rows.should_use_rgb_for_red_green = False

        self.indices.stretch_ranges_coefficients = {
            "red": {"low": 0, "high": 1},
            "green": {"low": 0, "high": 1},
            "blue": {"low": 0, "high": 1.15},
            "nir": {"low": 0, "high": 1},
        }


class PlanetPlanetScope(AgmriConfig):
    """
    Previously we used images from planet which required some preprocessing to be more human eye friendly.
    Now we get separate band which are already preprocessed by provider and will show these to the end user.
    Still, in case of old formatted input (missing red1, green1, blue1) we fal back to old way.
    At the same time, the analytics pipeline still uses the rgb channels which were used previously.
    """

    def __init__(self, crop_type):
        super().__init__(crop_type)

        self.indices.stretch_ranges_coefficients = {
            "red": {"low": 0.8, "high": 1},
            "green": {"low": 0.8, "high": 1},
            "blue": {"low": 0.8, "high": 1},
            "nir": {"low": 0.5, "high": 1},
        }

        self.indices.scale_rgb_brightness = True
        self.indices.percentiles.blue = {"low": 1, "high": 99}
        self.indices.clip_ranges = {"nir": (0, 5000), "red": (0, 1000000), "green": (0, 1000000), "blue": (0, 1000000)}

        self.ndvi_anomaly.averaging_box_size = 0
        self.ndvi_anomaly.soil_correction_coefficient = 0
        self.ndvi_anomaly.locality_resize_factor = 1
        self.ndvi_anomaly.min_areas = {1: 180, 2: 140, 3: 100}
        self.ndvi_anomaly.steps = [0.01, 0.05, 0.1]

        self.gndvi_anomaly.averaging_box_size = 0
        self.gndvi_anomaly.soil_correction_coefficient = 0
        self.gndvi_anomaly.locality_resize_factor = 1
        self.gndvi_anomaly.min_areas = {1: 180, 2: 140, 3: 100}
        self.gndvi_anomaly.steps = [0.01, 0.05, 0.1]


class AirbusConfig(AgmriConfig):
    def __init__(self, crop_type):
        super().__init__(crop_type)
        self.indices.scaling_coefficients = {"nir": 0.6, "red": 0.9, "green": 1}
        self.ndvi_anomaly.averaging_box_size = 0
        self.ndvi_anomaly.soil_correction_coefficient = 0
        self.ndvi_anomaly.locality_resize_factor = 1
        self.ndvi_anomaly.min_areas = {0: 200, 1: 180, 2: 1000, 3: 100}
        self.ndvi_anomaly.contour_config = {"tolerance": 0.1, "bezier": True}
        self.ndvi_anomaly.steps = [0.02, 0.06, 0.16]

        self.gndvi_anomaly.averaging_box_size = 0
        self.gndvi_anomaly.steps = [0.03, 0.06, 0.09, 0.15, 0.27]
        self.gndvi_anomaly.min_areas = {
            1: 1800,  # ~0.005 acres under ~10cm resolution
            2: 1400,
            3: 1000,
            4: 1000,
            5: 1000,
            6: 1000,
        }


CONFIGS_ = {
    "airbus_fake": {
        "default": AirbusConfig,
    },
    "airbus_pleiades": {
        "default": AirbusConfig,
    },
    "airbus_pleiades_1b": {
        "default": AirbusConfig,
    },
    "airbus_spot": {
        "default": AirbusConfig
    },
    "dji mavic 3m": {
        "default": MicasenseConfig
    },
    "sentinel2": {
        "default": Sentinel2Config,
    },
    "micasense": {
        "default": MicasenseConfig,
    },
    "micasense altum": {
        "default": MicasenseConfig,
    },
    "planet_planetscope": {
        "default": PlanetPlanetScope,
    }
}


def agmri_config_for_provider(provider, crop_type=None, config_type="default"):
    """
    Instantiate config for specified provider and specific type if provided
    :param provider:
    :param crop_type:
    :param config_type: Additional type to handle cases like different configs per provider
    :return: AgmriConfig instance
    """
    if provider not in CONFIGS_ or config_type not in CONFIGS_[provider]:
        print("provider {} / {} not found, returning base config".format(provider, config_type))
        return AgmriConfig(crop_type)
    return CONFIGS_[provider][config_type](crop_type)
