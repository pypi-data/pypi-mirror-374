\
# filepath: /home/pranay/GRID/Grid-Cortex-Infra/grid-cortex-client/src/grid_cortex_client/postprocessing.py
from typing import Dict, Any
import numpy as np
import logging
import base64
import io
from PIL import Image
import PIL
import json # Add json import

logger = logging.getLogger(__name__)

def postprocess_depth_response(response: Dict[str, Any]) -> Image.Image: # Return PIL Image
    """
    Processes JSON response from a depth model into a PIL Image.
    Expects an 'output' key in the response, which contains a base64 encoded
    string of a NumPy array saved with numpy.save().
    """
    logger.info("Attempting to postprocess depth estimation response into a PIL Image.")
    if not isinstance(response, dict) or "output" not in response:
        logger.error(f"Response is not a dict or missing 'output' key. Response: {type(response)}")
        raise ValueError("Response missing 'output' key or is not a dictionary.")
    
    base64_encoded_numpy = response["output"]
    if not isinstance(base64_encoded_numpy, str):
        logger.error(f"'output' key should contain a base64 string, but found {type(base64_encoded_numpy)}.")
        raise ValueError(f"'output' key should contain a base64 string, but found {type(base64_encoded_numpy)}.")

    try:
        decoded_bytes = base64.b64decode(base64_encoded_numpy)
    except base64.binascii.Error as e:
        logger.error(f"Base64 decoding failed: {e}. Input (first 100 chars): '{base64_encoded_numpy[:100]}'")
        raise ValueError(f"Base64 decoding failed: {e}") from e

    try:
        bytes_io = io.BytesIO(decoded_bytes)
        # The warning "UserWarning: The given NumPy array is not writeable..." is harmless here.
        # We are only reading from it.
        depth_array = np.load(bytes_io, allow_pickle=False) # Added allow_pickle=False for security
    except Exception as e: # Catching a broader range of np.load errors
        logger.error(f"Failed to load NumPy array from decoded_bytes. Error: {e}. Decoded bytes (first 100): {decoded_bytes[:100]}")
        raise ValueError(f"Could not load NumPy array from decoded base64 string: {e}") from e
    
    if not isinstance(depth_array, np.ndarray):
        logger.error(f"Loaded data is not a NumPy array. Type: {type(depth_array)}")
        raise ValueError(f"Loaded data is not a NumPy array. Type: {type(depth_array)}")

    return depth_array

    # try:
    #     # Normalize and convert to PIL Image
    #     # Assuming depth_array contains float values representing depth.
    #     # For visualization, it's common to normalize to 0-255 and convert to 'L' (grayscale).
    #     if depth_array.size == 0:
    #         logger.error("Depth array is empty.")
    #         raise ValueError("Depth array is empty after loading.")

    #     # Normalize the depth array to 0-1 range for better visualization
    #     min_val = np.min(depth_array)
    #     max_val = np.max(depth_array)
        
    #     if max_val == min_val: # Avoid division by zero if the array is flat
    #         normalized_array = np.zeros_like(depth_array, dtype=np.uint8)
    #     else:
    #         normalized_array = ((depth_array - min_val) / (max_val - min_val) * 255).astype(np.uint8)
        
    #     image = Image.fromarray(normalized_array, mode='L') # Convert to grayscale PIL Image
    #     logger.info(f"Successfully converted NumPy array (shape: {depth_array.shape}, dtype: {depth_array.dtype}) to PIL Image (mode: 'L').")
    #     logger.info(f"Converted base64 encoded depth map to NumPy array. Shape: {depth_array.shape}, Dtype: {depth_array.dtype}")
    #     return image

    # except Exception as e:
    #     logger.error(f"Could not convert NumPy array (shape: {depth_array.shape}) to PIL Image: {e}", exc_info=True)
    #     raise ValueError(f"Could not convert NumPy array to PIL Image: {e}") from e

def postprocess_detection_response(response_data: Any) -> Dict[str, Any]: # Changed type hint for response_data
    """
    Processes response from a detection model.
    The response from owlv2 is a JSON string literal containing a base64 encoded JSON string.
    This function will decode it accordingly.
    Expected final structure: 'boxes', 'scores', and 'labels' keys, all being lists.
    """
    logger.info("Attempting to postprocess detection response.")

    if not isinstance(response_data, dict):
        logger.error(f"Expected a string response (base64 encoded JSON), but got {type(response_data)}.")
        # If it's already a dict, perhaps another model type sent it directly.
        # For owlv2, it must be a string.
        # For now, let's be strict for the owlv2 case based on the server code provided.
        raise ValueError(f"Expected a string response for owlv2-like model, but got {type(response_data)}.")

    try:
        output = response_data.get("output", None)
        decoded_json_str = base64.b64decode(output).decode('utf-8')
    except (base64.binascii.Error, UnicodeDecodeError) as e:
        logger.error(f"Failed to base64 decode or UTF-8 decode the response string: {e}. Input (first 100 chars): '{response_data[:100]}'")
        raise ValueError(f"Failed to decode base64/utf-8 response string: {e}") from e
    
    try:
        actual_response_dict = json.loads(decoded_json_str)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from decoded string: {e}. Decoded string (first 100 chars): '{decoded_json_str[:100]}'")
        raise ValueError(f"Failed to parse JSON from decoded string: {e}") from e

    if not isinstance(actual_response_dict, dict):
        logger.error(f"Decoded and parsed response is not a dict. Type: {type(actual_response_dict)}")
        raise ValueError("Decoded and parsed response is not a dictionary.")

    required_keys = ["boxes", "scores", "labels"]
    for key in required_keys:
        if key not in actual_response_dict:
            logger.error(f"Response missing required key: '{key}'. Available keys: {list(actual_response_dict.keys())}")
            raise ValueError(f"Response missing required key: '{key}'.")
        if not isinstance(actual_response_dict[key], list):
            logger.error(f"Key '{key}' should be a list, but found {type(actual_response_dict[key])}.")
            raise ValueError(f"Key '{key}' should be a list, but found {type(actual_response_dict[key])}.")

    num_boxes = len(actual_response_dict["boxes"])
    if not (len(actual_response_dict["scores"]) == num_boxes and len(actual_response_dict["labels"]) == num_boxes):
        logger.warning(
            f"Mismatch in lengths of 'boxes' ({num_boxes}), "
            f"'scores' ({len(actual_response_dict['scores'])}), and 'labels' ({len(actual_response_dict['labels'])})."
        )

    logger.info(f"Detection response successfully decoded and validated. Found {num_boxes} detections.")
    return {
        "boxes": actual_response_dict["boxes"],
        "scores": actual_response_dict["scores"],
        "labels": actual_response_dict["labels"],
    }


def postprocess_segmentation_response(response: Dict[str, Any], mask_key: str = "output") -> Image.Image:
    """
    Processes JSON response from a segmentation model into a PIL Image.
    Expects a key in the response (default: 'segmentation_mask_b64') which contains
    a base64 encoded string of an image (e.g., a PNG mask).

    Args:
        response: The JSON response dictionary from the API.
        mask_key: The key in the response dictionary that holds the base64 encoded mask.

    Returns:
        A PIL.Image object of the segmentation mask.

    Raises:
        ValueError: If the response is not a dict, missing the mask_key,
                    or if decoding/image conversion fails.
    """
    logger.info(f"Attempting to postprocess segmentation response from key '{mask_key}'.")
    if not isinstance(response, dict) or mask_key not in response:
        logger.error(f"Response is not a dict or missing '{mask_key}' key. Response type: {type(response)}, Keys: {list(response.keys()) if isinstance(response, dict) else 'N/A'}")
        raise ValueError(f"Response missing '{mask_key}' key or is not a dictionary.")

    base64_encoded_mask = response[mask_key]
    if not isinstance(base64_encoded_mask, str):
        logger.error(f"'{mask_key}' should contain a base64 string, but found {type(base64_encoded_mask)}.")
        raise ValueError(f"'{mask_key}' should contain a base64 string, but found {type(base64_encoded_mask)}.")

    try:
        decoded_bytes = base64.b64decode(base64_encoded_mask)
    except base64.binascii.Error as e:
        logger.error(f"Base64 decoding failed for mask: {e}. Input (first 100 chars): '{base64_encoded_mask[:100]}'")
        raise ValueError(f"Base64 decoding failed for mask: {e}") from e

    try:
        mask_image = Image.open(io.BytesIO(decoded_bytes))
        # It's good practice to load the image data to ensure it's valid and to close the BytesIO buffer.
        mask_image.load() 
        logger.info(f"Successfully decoded base64 mask and loaded as PIL Image. Mode: {mask_image.mode}, Size: {mask_image.size}")
        return mask_image
    except PIL.UnidentifiedImageError:
        logger.error("Cannot identify image file from decoded base64 string. It might not be a supported image format or the data is corrupt.")
        # As a fallback, if it might be a raw NumPy array (like depth maps sometimes are):
        try:
            bytes_io = io.BytesIO(decoded_bytes)
            mask_array = np.load(bytes_io, allow_pickle=False)
            if mask_array.ndim == 2: # Grayscale mask
                mask_image = Image.fromarray(mask_array.astype(np.uint8), mode='L')
            elif mask_array.ndim == 3 and mask_array.shape[2] in [1, 3, 4]: # Possibly HxWx1, HxWx3, HxWx4
                if mask_array.shape[2] == 1: # HxWx1 -> squeeze to HxW
                     mask_image = Image.fromarray(mask_array.squeeze().astype(np.uint8), mode='L')
                else: # HxWx3 (RGB) or HxWx4 (RGBA)
                    mask_image = Image.fromarray(mask_array.astype(np.uint8)) # Mode will be inferred
            else:
                raise ValueError(f"Unsupported NumPy array shape for mask: {mask_array.shape}")
            logger.info(f"Successfully decoded base64 mask and loaded as PIL Image from NumPy array. Mode: {mask_image.mode}, Size: {mask_image.size}")
            return mask_image
        except Exception as np_e:
            logger.error(f"Failed to load mask as PIL Image directly and also failed as NumPy array: {np_e}")
            raise ValueError("Could not convert decoded base64 string to a PIL Image or NumPy array.") from np_e
    except Exception as e:
        logger.error(f"Could not convert decoded base64 string to PIL Image: {e}", exc_info=True)
        raise ValueError(f"Could not convert decoded base64 string to PIL Image: {e}") from e

def postprocess_generic_json_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """Generic postprocessor, returns the JSON response as is."""
    logger.info("Postprocessing generic JSON response.")
    return response
