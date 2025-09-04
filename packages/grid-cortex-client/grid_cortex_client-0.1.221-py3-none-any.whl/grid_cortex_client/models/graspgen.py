"""GraspGen model handler for grasp generation from depth and segmentation images."""

import base64
import gzip
import io
import logging
import numpy as np
from typing import Dict, Any

from .base_model import BaseModel


def pack_npz(**arrays) -> bytes:
    """Pack numpy arrays into a gzipped-npz byte stream."""
    buf = io.BytesIO()
    np.savez_compressed(buf, **arrays)
    return gzip.compress(buf.getvalue())


class GraspGenModel(BaseModel):
    """
    Model handler for GraspGen grasp generation.
    
    This model generates 6-DoF grasps from depth images, segmentation images,
    and camera intrinsics. It returns grasp poses and confidence scores.
    """

    def __init__(self, model_id: str = "graspgen"):
        super().__init__(model_id)
        logging.info(f"GraspGenModel initialized for model_id: '{self.model_id}'")

    def preprocess(self, input_data: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """
        Preprocesses the input for GraspGen grasp generation.
        
        Args:
            input_data: Dictionary containing:
                - depth_image: numpy array of depth image
                - seg_image: numpy array of segmentation image  
                - camera_intrinsics: numpy array of camera intrinsics matrix
                - aux_args: dictionary with num_grasps, gripper_config, camera_extrinsics
            **kwargs: Additional keyword arguments
            
        Returns:
            Dictionary with base64-encoded payload for the API
            
        Raises:
            ValueError: If required inputs are missing
        """
        try:
            # Extract required inputs
            depth_image = input_data.get("depth_image")
            seg_image = input_data.get("seg_image")
            camera_intrinsics = input_data.get("camera_intrinsics")
            aux_args = input_data.get("aux_args", {})
            
            if depth_image is None:
                raise ValueError("'depth_image' must be provided in input_data for GraspGen preprocessing.")
            if seg_image is None:
                raise ValueError("'seg_image' must be provided in input_data for GraspGen preprocessing.")
            if camera_intrinsics is None:
                raise ValueError("'camera_intrinsics' must be provided in input_data for GraspGen preprocessing.")
            
            logging.info(f"Preprocessing for GraspGen (model_id='{self.model_id}').")
            
            # Convert numpy arrays to base64 strings
            def array_to_base64(arr):
                if isinstance(arr, np.ndarray):
                    return base64.b64encode(arr.tobytes()).decode('utf-8')
                return arr
            
            # Convert aux_args dict to base64-encoded npz
            aux_args_encoded = base64.b64encode(pack_npz(**aux_args)).decode('utf-8')
            
            # Create payload
            payload = {
                "depth_image": array_to_base64(depth_image),
                "seg_image": array_to_base64(seg_image),
                "camera_intrinsics": array_to_base64(camera_intrinsics),
                "aux_args": aux_args_encoded
            }
            
            logging.debug(f"GraspGen preprocess payload created.")
            return payload
            
        except Exception as e:
            logging.error(f"Error during GraspGen preprocessing: {e}")
            raise ValueError(f"Failed to preprocess GraspGen input: {e}") from e

    def postprocess(self, api_response: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Postprocesses the GraspGen model's response.
        
        Args:
            api_response: Raw API response containing output and confidence
            **kwargs: Additional keyword arguments
            
        Returns:
            Dictionary with processed grasps and confidence scores
            
        Raises:
            ValueError: If response is missing required keys
        """
        try:
            logging.info(f"Postprocessing for GraspGen (model_id='{self.model_id}')")
            
            # Extract grasps and confidence from response
            grasps = api_response.get("output", [])
            confidence = api_response.get("confidence", [])
            latency_ms = api_response.get("latency_ms", 0)
            
            if not grasps:
                logging.warning(f"No grasps returned from GraspGen API")
                return {
                    "grasps": np.array([]),
                    "confidence": np.array([]),
                    "latency_ms": latency_ms
                }
            
            # Convert to numpy arrays
            grasps_array = np.array(grasps)
            confidence_array = np.array(confidence)
            
            logging.debug(f"GraspGen postprocess successful for model_id='{self.model_id}'.")
            
            return {
                "grasps": grasps_array,
                "confidence": confidence_array,
                "latency_ms": latency_ms
            }
            
        except KeyError as e:
            logging.error(f"Postprocessing failed for GraspGen (model_id='{self.model_id}'): Missing key {e}")
            raise ValueError(f"Missing required key in GraspGen response: {e}")
        except Exception as e:
            logging.error(f"Unexpected error during postprocessing for GraspGen (model_id='{self.model_id}'): {e}", exc_info=True)
            raise ValueError(f"Failed to postprocess GraspGen response: {e}") from e

    def visualize(self, output: Any, **kwargs) -> None:
        """
        Optional visualization for GraspGen output.
        
        Args:
            output: Processed output from postprocess
            **kwargs: Additional keyword arguments
        """
        if hasattr(output, 'get'):
            grasps = output.get('grasps', [])
            confidence = output.get('confidence', [])
            latency_ms = output.get('latency_ms', 0)
            
            print(f"GraspGen Results:")
            print(f"  Number of grasps: {len(grasps)}")
            if len(confidence) > 0:
                print(f"  Confidence range: [{confidence.min():.3f}, {confidence.max():.3f}]")
            print(f"  Latency: {latency_ms:.2f} ms")
        else:
            print(f"GraspGen output: {output}")
