\
import logging

# Configure the library logger to be silent by default.
# Applications using this library should configure their own logging handlers and levels
# if they wish to see logs from "grid_cortex_client".
logging.getLogger(__name__).addHandler(logging.NullHandler())

# Make key classes and functions available for import
from .client import CortexAPIError, CortexNetworkError, HTTPClient
from .cortex_client import CortexClient
from .models import BaseModel, DepthModel, DetectionModel, SegmentationModel
from .preprocessing import encode_image_to_base64, load_image
from .postprocessing import (
    postprocess_depth_response,
    postprocess_detection_response,
    postprocess_segmentation_response,
)

__all__ = [
    "CortexClient",
    "HTTPClient",
    "CortexAPIError",
    "CortexNetworkError",
    "BaseModel",
    "DepthModel",
    "DetectionModel",
    "SegmentationModel",
    "load_image",
    "encode_image_to_base64",
    "postprocess_depth_response",
    "postprocess_detection_response",
    "postprocess_segmentation_response",
]
