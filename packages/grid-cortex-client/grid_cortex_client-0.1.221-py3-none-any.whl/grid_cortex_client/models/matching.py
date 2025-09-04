"""
Model handlers for matching models.
"""
import base64
import io
import json
from typing import Any, Dict, List, Union

import numpy as np
from PIL import Image

from .base_model import BaseModel
from ..utils import ( # Relative import from sibling module
    decode_base64_to_array,
    image_to_base64,
    visualize_matches,
)

class MatchingModel(BaseModel):
    """
    Handles requests for feature matching models like LightGlue.

    This class preprocesses a pair of images into the required base64 format
    and postprocesses the API response, decoding matched keypoints.
    """

    def preprocess(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Preprocesses a pair of images for the matching model.

        Args:
            input_data: A dictionary containing two image inputs.
                        Expected keys are 'image0_input' and 'image1_input'.
                        The values can be file paths, PIL Images, or numpy arrays.
            **kwargs: Additional keyword arguments (not used).

        Returns:
            A dictionary containing the base64-encoded images.
        """
        image0_input = input_data.get("image0_input")
        image1_input = input_data.get("image1_input")

        if image0_input is None or image1_input is None:
            raise ValueError("Input data must contain 'image0_input' and 'image1_input'")

        # Convert images to base64
        image0_b64 = image_to_base64(image0_input)
        image1_b64 = image_to_base64(image1_input)

        return {
            "image0_input": image0_b64,
            "image1_input": image1_b64,
        }

    def postprocess(self, api_response: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """
        Postprocesses the response from the matching model API.

        Args:
            api_response: The JSON response from the API.
            **kwargs: Additional keyword arguments (not used).

        Returns:
            A dictionary containing the decoded keypoints, matches, and latency.
        """
        return {
            "matches": decode_base64_to_array(api_response["matches"]),
            "points0": decode_base64_to_array(api_response["points0"]),
            "points1": decode_base64_to_array(api_response["points1"]),
            "latency_ms": api_response.get("latency_ms"),
        }

    def visualize(
        self, 
        processed_output: Dict[str, Any], 
        original_input: Dict[str, Any], 
        **kwargs
    ) -> None:
        """
        Visualizes the matches on the original images.

        Args:
            processed_output: The postprocessed output from the model.
            original_input: The original input data containing the images.
            **kwargs: Additional arguments for visualization (e.g., 'save_path').
        """
        image0 = Image.open(original_input['image0_input'])
        image1 = Image.open(original_input['image1_input'])
        points0 = processed_output['points0']
        points1 = processed_output['points1']
        
        save_path = kwargs.get("save_path")

        visualize_matches(image0, image1, points0, points1, save_path)
