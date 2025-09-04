"""FoundationStereo model handler for stereo depth estimation."""
import base64
import io
import logging
from typing import Any, Dict, Union, Optional

import numpy as np
from PIL import Image

from .base_model import BaseModel
from ..preprocessing import load_image as general_load_image


class FoundationStereoModel(BaseModel):
    """
    Model handler for FoundationStereo stereo depth estimation.

    Expected input_data keys for preprocess:
        - 'left_image' (Union[str, np.ndarray, Image.Image]): Left stereo image
        - 'right_image' (Union[str, np.ndarray, Image.Image]): Right stereo image
        - 'K' (np.ndarray): 3x3 camera intrinsics matrix
        - 'baseline' (float): Stereo baseline distance
        - 'hiera' (bool, optional): Whether to use hierarchical inference (default: False)
        - 'valid_iters' (int, optional): Number of valid iterations (default: 12)
    
    Output:
        - A numpy array representing the depth map.
    """

    def __init__(self, model_id: str):
        super().__init__(model_id)
        logging.info(f"FoundationStereoModel initialized for model_id: '{self.model_id}'")

    def preprocess(self, input_data: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """
        Preprocesses the input for FoundationStereo stereo depth estimation.

        Args:
            input_data: A dictionary containing the input data. Expected keys:
                'left_image' (Union[str, np.ndarray, Image.Image]): Left stereo image
                'right_image' (Union[str, np.ndarray, Image.Image]): Right stereo image
                'K' (np.ndarray): 3x3 camera intrinsics matrix
                'baseline' (float): Stereo baseline distance
                'hiera' (bool, optional): Whether to use hierarchical inference
                'valid_iters' (int, optional): Number of valid iterations
            **kwargs: Additional keyword arguments.

        Returns:
            A dictionary payload for the API request.
        """
        left_image = input_data.get('left_image')
        right_image = input_data.get('right_image')
        K = input_data.get('K')
        baseline = input_data.get('baseline')
        hiera = input_data.get('hiera', False)
        valid_iters = input_data.get('valid_iters', 12)

        if left_image is None or right_image is None:
            raise ValueError("'left_image' and 'right_image' must be provided in input_data for FoundationStereo preprocessing.")
        
        if K is None or baseline is None:
            raise ValueError("'K' (camera intrinsics) and 'baseline' must be provided in input_data for FoundationStereo preprocessing.")

        logging.info(f"Preprocessing for FoundationStereo (model_id='{self.model_id}').")
        
        try:
            # Load and encode left image
            left_pil = general_load_image(left_image)
            left_buffered = io.BytesIO()
            left_pil.save(left_buffered, format="JPEG")
            left_encoded = base64.b64encode(left_buffered.getvalue()).decode("utf-8")

            # Load and encode right image
            right_pil = general_load_image(right_image)
            right_buffered = io.BytesIO()
            right_pil.save(right_buffered, format="JPEG")
            right_encoded = base64.b64encode(right_buffered.getvalue()).decode("utf-8")

            # Prepare aux_args
            aux_args = {
                "K": K.tolist() if isinstance(K, np.ndarray) else K,
                "baseline": float(baseline),
                "hiera": bool(hiera),
                "valid_iters": int(valid_iters)
            }

            payload = {
                "left_image": left_encoded,
                "right_image": right_encoded,
                "aux_args": aux_args
            }
            
            logging.debug(f"FoundationStereo preprocess payload created.")
            return payload

        except Exception as e:
            logging.error(f"Error during FoundationStereo preprocessing: {e}")
            raise ValueError(f"Failed to preprocess FoundationStereo input: {e}") from e

    def postprocess(self, response_data: Dict[str, Any], **kwargs: Any) -> np.ndarray:
        """
        Postprocesses the FoundationStereo model's response.

        Args:
            response_data: The raw JSON response from the API.
            **kwargs: Additional keyword arguments.

        Returns:
            A numpy array representing the depth map.
        """
        logging.info(f"Postprocessing for FoundationStereo (model_id='{self.model_id}')")
        try:
            # The response contains a base64-encoded depth map
            depth_b64 = response_data["output"]
            depth_bytes = base64.b64decode(depth_b64)
            
            # Load the depth map from the decoded bytes
            depth_map = np.load(io.BytesIO(depth_bytes))
            
            logging.debug(f"FoundationStereo postprocess successful for model_id='{self.model_id}'.")
            return depth_map
            
        except KeyError as e:
            logging.error(f"Postprocessing failed for FoundationStereo (model_id='{self.model_id}'): Missing key {e}")
            raise ValueError(f"Postprocessing failed, missing key in response: {e}") from e
        except Exception as e:
            logging.error(f"Unexpected error during postprocessing for FoundationStereo (model_id='{self.model_id}'): {e}", exc_info=True)
            raise ValueError(f"Unexpected postprocessing error: {e}") from e

    def visualize(self, processed_output: np.ndarray, original_input: Any = None, **kwargs: Any) -> None:
        """
        Visualizes the depth map using Rerun.

        Args:
            processed_output: The depth map (NumPy array) to visualize.
            original_input: Optional original stereo images for context.
            **kwargs: Additional arguments for visualization.
        """
        try:
            import rerun as rr  # type: ignore
            rr.log("depth_map", rr.DepthImage(processed_output))
            
            if original_input is not None:
                # Log the stereo images if available
                if isinstance(original_input, dict):
                    left_img = original_input.get('left_image')
                    right_img = original_input.get('right_image')
                    
                    if left_img is not None:
                        left_pil = general_load_image(left_img)
                        rr.log("left_image", rr.Image(np.array(left_pil)))
                    
                    if right_img is not None:
                        right_pil = general_load_image(right_img)
                        rr.log("right_image", rr.Image(np.array(right_pil)))
            
            print("Depth map visualized. Check your Rerun viewer.")
        except ImportError:
            print("Rerun SDK not installed. Skipping visualization.")
        except Exception as e:
            print(f"Error during Rerun visualization: {e}")
