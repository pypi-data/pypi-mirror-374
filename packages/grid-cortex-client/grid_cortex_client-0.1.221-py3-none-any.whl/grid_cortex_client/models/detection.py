from typing import Any, Dict, List, Optional, Union
import logging

from PIL import Image

from .base_model import BaseModel
from ..preprocessing import load_image, encode_image_to_base64
from ..postprocessing import postprocess_detection_response # This will be created next

logger = logging.getLogger(__name__)

class DetectionModel(BaseModel):
    """
    Model handler for detection models.

    Input:
        - image: Path (str), URL (str), or PIL.Image object.
        - prompt: List of text strings.
        - box_threshold: Float value for confidence threshold.
    Output:
        - Dictionary with 'boxes', 'scores', 'labels'.
    """

    def __init__(self, model_id: str, default_box_threshold: float = 0.1):
        super().__init__(model_id)
        self.default_box_threshold = default_box_threshold
        logger.info(f"DetectionModel initialized for model_id: '{model_id}' with default_box_threshold: {default_box_threshold}")

    def preprocess(
        self,
        input_data: Dict[str, Any], # Changed: expects a single dictionary
        **kwargs: Any # Kept for BaseModel consistency, though not directly used here
    ) -> Dict[str, Any]:
        """
        Preprocesses the input for a detection model.

        Args:
            input_data: A dictionary containing the input data. Expected keys:
                'image_input' (Union[str, Image.Image]): Image path, URL, or PIL.Image object. (Required)
                'prompt' (List[str]): A list of text prompt. (Required)
                'box_threshold' (Optional[float]): Optional box threshold to override the instance default.
            **kwargs: Additional keyword arguments (currently not used by this implementation).


        Returns:
            A dictionary payload for the API request.
            
        Raises:
            ValueError: If required keys ('image_input', 'prompt') are missing from input_data,
                        or if image loading/encoding fails.
        """
        image_input = input_data.get('image_input')
        prompt = input_data.get('prompt')
        
        if image_input is None:
            raise ValueError("'image_input' not found in input_data for DetectionModel preprocessing.")
        if prompt is None:
            raise ValueError("'prompt' not found in input_data for DetectionModel preprocessing.")

        # Use box_threshold from input_data if provided, otherwise use the model's default
        box_threshold = input_data.get('box_threshold', self.default_box_threshold)

        logger.info(f"Preprocessing for DetectionModel (model_id='{self.model_id}'). Input image type: {type(image_input)}")
        
        try:
            image = load_image(image_input)
            encoded_image = encode_image_to_base64(image)
        except Exception as e:
            logger.error(f"Error during image loading/encoding for DetectionModel: {e}")
            raise ValueError(f"Failed to load or encode image: {e}") from e

        # current_box_threshold = box_threshold if box_threshold is not None else self.default_box_threshold # This line is now handled by the .get with default

        payload = {
            # "model_id": self.model_id, # Removed as per user feedback; CortexClient.run_model will add it if necessary
            "image_input": encoded_image,
            "prompt": prompt,
            "box_threshold": box_threshold, # Use the resolved box_threshold
        }
        # Ensure model_id is not part of this payload, as it's handled by the client/URL
        logger.debug(f"DetectionModel Preprocess payload (excluding image data): {{'prompt': {payload['prompt']}, 'box_threshold': {payload['box_threshold']}}}")
        return payload

    def postprocess(self, response_data: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """
        Postprocesses the detection model's response.

        Args:
            response_data: The raw JSON response from the API.
            **kwargs: Additional keyword arguments.

        Returns:
            A dictionary containing 'boxes', 'scores', and 'labels'.
        """
        logger.info(f"Postprocessing for DetectionModel (model_id='{self.model_id}')")
        try:
            # This function will perform the necessary validations
            processed_output = postprocess_detection_response(response_data)
            logger.debug(f"DetectionModel Postprocess successful for model_id='{self.model_id}'.")
            return processed_output
        except ValueError as e:
            logger.error(f"Postprocessing failed for DetectionModel (model_id='{self.model_id}'): {e}")
            raise # Re-raise the ValueError to be caught by CortexClient
        except Exception as e:
            logger.error(f"Unexpected error during postprocessing for DetectionModel (model_id='{self.model_id}'): {e}", exc_info=True)
            raise ValueError(f"Unexpected postprocessing error: {e}") from e


    def visualize(self, processed_output: Dict[str, Any], original_input: Any = None, **kwargs: Any) -> None:
        """
        (Optional) Visualizes the detection output.
        Placeholder for now.
        """
        logger.info(f"Visualize called for DetectionModel (model_id='{self.model_id}'). Output keys: {list(processed_output.keys())}")
        # Example:
        # if isinstance(original_input, Image.Image) and 'boxes' in processed_output:
        #     from PIL import ImageDraw
        #     image_to_draw = original_input.copy()
        #     draw = ImageDraw.Draw(image_to_draw)
        #     for box in processed_output['boxes']:
        #         draw.rectangle(box, outline="red", width=2)
        #     image_to_draw.show()
        # else:
        #     print("Visualization for detection model needs a PIL Image as original_input and 'boxes' in processed_output.")
        print(f"Visualization for {self.model_id} not yet implemented. Data: {processed_output}")

