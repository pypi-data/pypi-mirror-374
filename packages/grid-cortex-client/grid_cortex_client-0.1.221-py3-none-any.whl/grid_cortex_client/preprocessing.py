# filepath: /home/pranay/GRID/Grid-Cortex-Infra/grid-cortex-client/src/grid_cortex_client/preprocessing.py
import base64
import io
import logging
import os
from typing import Any, Dict, Optional, Union
import requests # Add requests import

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

SUPPORTED_IMAGE_FORMATS = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff')

def load_image(image_input: Union[str, Image.Image, np.ndarray]) -> Image.Image:
    """Loads an image from various input types into a PIL Image (RGB).
    Can load from a local file path, a URL, a PIL Image object, or a NumPy array.
    """
    if isinstance(image_input, str):
        # Check if it's a URL
        if image_input.startswith(('http://', 'https://')):
            try:
                logger.debug(f"Fetching image from URL: {image_input}")
                response = requests.get(image_input, timeout=10)
                response.raise_for_status() # Raise an exception for bad status codes
                img_bytes = io.BytesIO(response.content)
                return Image.open(img_bytes).convert("RGB")
            except requests.exceptions.RequestException as e:
                raise IOError(f"Failed to fetch image from URL {image_input}: {e}") from e
            except Exception as e:
                raise IOError(f"Failed to load image from URL {image_input} after fetching: {e}") from e
        # Otherwise, assume it's a local file path
        elif not os.path.exists(image_input):
            raise FileNotFoundError(f"Image path does not exist: {image_input}")
        if not image_input.lower().endswith(SUPPORTED_IMAGE_FORMATS):
            raise ValueError(f"Unsupported image format: {image_input}. Supported: {SUPPORTED_IMAGE_FORMATS}")
        try:
            return Image.open(image_input).convert("RGB")
        except Exception as e:
            raise IOError(f"Failed to load image from path {image_input}: {e}") from e
    elif isinstance(image_input, Image.Image):
        return image_input.convert("RGB")
    elif isinstance(image_input, np.ndarray):
        try:
            return Image.fromarray(image_input).convert("RGB")
        except Exception as e:
            raise ValueError(f"Failed to convert numpy array to PIL Image: {e}") from e
    raise TypeError(f"Unsupported image input type: {type(image_input)}. Supported: str, PIL.Image, np.ndarray.")

def resize_image(image: Image.Image, target_width: int, target_height: int, resample_method=Image.Resampling.LANCZOS) -> Image.Image:
    """Resizes a PIL Image to the specified dimensions."""
    if not isinstance(image, Image.Image):
        raise TypeError("Input must be a PIL Image object.")
    if target_width <= 0 or target_height <= 0:
        raise ValueError("Target width and height must be positive.")
    
    logger.debug(f"Resizing image from {image.size} to ({target_width}, {target_height})")
    return image.resize((target_width, target_height), resample=resample_method)

def encode_image_to_base64(image: Image.Image, encoding_format: str = "JPEG") -> str:
    """Encodes a PIL Image to a base64 string."""
    if not isinstance(image, Image.Image):
        raise TypeError("Input must be a PIL Image object.")
    
    buffered = io.BytesIO()
    image.save(buffered, format=encoding_format)
    encoded_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    logger.debug(f"Encoded image to base64 with format {encoding_format}")
    return encoded_image

