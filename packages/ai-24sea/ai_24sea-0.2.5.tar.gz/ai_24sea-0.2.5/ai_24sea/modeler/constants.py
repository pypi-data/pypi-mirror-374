# -*- coding: utf-8 -*-
"""Constant values like paths used across the module"""

## Config keys
DT_START_TRAINING_KEY = "dt_start_training"
DT_STOP_TRAINING_KEY = "dt_stop_training"
LOCATIONS_TRAINING_KEY = "training_turbines"
DT_START_VALIDITY_KEY = "start_validity_date"
MODEL_TYPE_KEY = "model_type"
SITE_KEY = "site"

REQUIRED_GENERAL_CONFIG_KEYS = [
    SITE_KEY,
    DT_START_TRAINING_KEY,
    DT_STOP_TRAINING_KEY,
    LOCATIONS_TRAINING_KEY,
    MODEL_TYPE_KEY,
]
REQUIRED_INGEST_CONFIG_KEYS = ["parameters"]
REQUIRED_TRANSFORM_CONFIG_KEYS = ["steps"]
REQUIRED_SCALER_CONFIG_KEYS = ["type", "order"]
SPLIT_CONFIG_KEYS = ["test_size"]
