"""Segmentation model handler."""
import base64
import json
import logging
from typing import Any, Dict, List, Union

from PIL import Image

from .base_model import BaseModel
from ..preprocessing import load_image, encode_image_to_base64
from ..postprocessing import postprocess_segmentation_response

logger = logging.getLogger(__name__)

class SegmentationModel(BaseModel):
    """
    Model handler for segmentation models.

    Expected input_data keys for preprocess:
        - 'image_input' (Union[str, Image.Image]): Image path, URL, or PIL.Image object. (Required)
        - 'prompt' (List[str]): A list of text prompt. (Required for some segmentation models)
                                   Can be points, boxes, or text depending on the model.
    Output:
        - PIL.Image: Segmentation mask.
    """

    def __init__(self, model_id: str):
        super().__init__(model_id)
        logger.info(f"SegmentationModel initialized for model_id: '{model_id}'")

    def preprocess(self, input_data: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """
        Preprocesses the input for a segmentation model.

        Args:
            input_data: A dictionary containing the input data. Expected keys:
                'image_input' (Union[str, Image.Image]): Image path, URL, or PIL.Image object. (Required)
                'prompt' (Optional[List[str]]): A list of prompt (text, points, boxes).
                                                 The exact nature of prompt depends on the specific model.
            **kwargs: Additional keyword arguments.

        Returns:
            A dictionary payload for the API request.
        """
        image_input = input_data.get('image_input')
        prompt = input_data.get('prompt') # prompt are optional for some segmentation models

        if image_input is None:
            raise ValueError("'image_input' not found in input_data for SegmentationModel preprocessing.")

        logger.info(f"Preprocessing for SegmentationModel (model_id='{self.model_id}'). Input image type: {type(image_input)}")
        
        try:
            image = load_image(image_input)
            encoded_image = encode_image_to_base64(image)
        except Exception as e:
            logger.error(f"Error during image loading/encoding for SegmentationModel: {e}")
            raise ValueError(f"Failed to load or encode image: {e}") from e

        payload = {
            "image_input": encoded_image,
        }
        if prompt is not None: # Only include prompt if provided
            payload["prompt"] = prompt
        
        # model_id is not included here; CortexClient handles it.
        logger.debug(f"SegmentationModel Preprocess payload (excluding image data): {payload}")
        return payload

    def postprocess(self, response_data: Dict[str, Any], **kwargs: Any) -> Image.Image:
        """
        Postprocesses the segmentation model's response.

        Args:
            response_data: The raw JSON response from the API.
            **kwargs: Additional keyword arguments. Can include 'mask_key' if the
                      base64 mask is under a non-default key in the response.

        Returns:
            A PIL.Image object representing the segmentation mask.
        """
        logger.info(f"Postprocessing for SegmentationModel (model_id='{self.model_id}')")
        mask_key = kwargs.get("mask_key", "output") # Default key for the mask
        try:
            mask_image = postprocess_segmentation_response(response_data, mask_key=mask_key)
            logger.debug(f"SegmentationModel Postprocess successful for model_id='{self.model_id}'.")
            return mask_image
        except ValueError as e:
            logger.error(f"Postprocessing failed for SegmentationModel (model_id='{self.model_id}'): {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during postprocessing for SegmentationModel (model_id='{self.model_id}'): {e}", exc_info=True)
            raise ValueError(f"Unexpected postprocessing error: {e}") from e

    def visualize(self, processed_output: Image.Image, original_input: Any = None, **kwargs: Any) -> None:
        """
        (Optional) Visualizes the segmentation mask.
        """
        logger.info(f"Visualize called for SegmentationModel (model_id='{self.model_id}').")
        if not isinstance(processed_output, Image.Image):
            logger.warning("Visualization input is not a PIL Image. Skipping.")
            return

        try:
            import rerun as rr # type: ignore
            rr.log_image("segmentation_mask", processed_output)
            if original_input:
                try:
                    original_pil_image = load_image(original_input.get('image_input')) if isinstance(original_input, dict) else load_image(original_input)
                    rr.log_image("original_image_for_segmentation", original_pil_image)
                except Exception as e:
                    logger.warning(f"Could not log original image for segmentation visualization: {e}")
            print(f"Segmentation mask for model '{self.model_id}' sent to Rerun viewer.")
        except ImportError:
            print("Rerun SDK not installed. Skipping visualization of segmentation mask.")
            # Fallback to simple display if possible and if tkinter is available
            try:
                processed_output.show(title=f"Segmentation Mask - {self.model_id}")
            except Exception as e:
                logger.warning(f"Failed to show image using PIL's default viewer: {e}")
        except Exception as e:
            print(f"Error during Rerun visualization of segmentation mask: {e}")


class SAM2Model(SegmentationModel):
    """
    Model handler for SAM2 segmentation models, with special prompt handling.
    """

    def preprocess(self, input_data: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """
        Preprocesses the input for a SAM2 model.

        The 'prompts' are expected to be a list of points, which will be
        JSON-encoded and then base64-encoded.
        """
        if "prompts" in input_data and isinstance(input_data["prompts"], list):
            prompts_json = json.dumps(input_data["prompts"])
            # The payload expects the key to be "prompts", so we re-assign it.
            input_data["prompts"] = base64.b64encode(prompts_json.encode()).decode()

        # The base class preprocess will handle adding the image and the prompt to the payload
        payload = super().preprocess(input_data, **kwargs)
        if "labels" not in input_data:
            payload['labels'] = input_data.get("labels", [0])  # Ensure labels are included if provided

        # After calling the parent, ensure the 'prompts' key from the input_data is in the final payload
        if "prompts" in input_data:
            payload["prompts"] = input_data["prompts"]
            # If the parent method added a 'prompt' key, remove it to avoid confusion
            if "prompt" in payload:
                del payload["prompt"]
        
        return payload
