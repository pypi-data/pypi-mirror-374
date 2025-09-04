import base64
from io import BytesIO
from typing import Any, Dict

import numpy as np
from PIL import Image

from ..preprocessing import encode_image_to_base64, load_image
from .base_model import BaseModel
import json 
from typing import Optional


class VLMModel(BaseModel):
    """
    Handles VLM (Vision Language Model) models.
    """

    def preprocess(
        self,
        input_data: Dict[str, Any],
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Preprocesses the input data for a VLM model.

        Args:
            input_data: A dictionary containing:
                - "image_input": Path to the image, a PIL Image, or a base64 encoded string.
                - "prompt": A text prompt.
            **kwargs: Additional keyword arguments.

        Returns:
            A dictionary with the preprocessed data, including the base64 encoded image
            and the prompt.
        """
        image_input = input_data.get("image_input")
        prompt = input_data.get("prompt")

        if image_input is None or prompt is None:
            raise ValueError("Input data must contain 'image_input' and 'prompt'")

        image = load_image(image_input)
        encoded_image = encode_image_to_base64(image)

        payload = {
            "image_input": encoded_image,
            "prompt": prompt,
            "max_new_tokens": kwargs.get("max_new_tokens", 256),
        }

        return payload

    def postprocess(
        self,
        response: Dict[str, Any],
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Postprocesses the API response for a VLM model.

        Args:
            response: The raw JSON response from the API.
            **kwargs: Additional keyword arguments, including "model_name".

        Returns:
            The postprocessed response.
        """
        model_name = kwargs.get("model_name")
        if model_name == "robopoint" and "output" in response:
            try:
                points_data = base64.b64decode(response["output"])
                points = np.array(Image.open(BytesIO(points_data)))
                response["output"] = points
            except Exception as e:
                # Handle potential decoding errors
                response["decoding_error"] = str(e)

        return response

class MoonDreamModel(VLMModel):
    """
    Client helper for the MoonDream‑2 multi‑task endpoint.
    Supports tasks: vqa | caption | detect | point.
    """

    SUPPORTED_TASKS = {"vqa", "caption", "detect", "point"}

    # ------------- preprocessing ----------------------------------------- #
    def preprocess(  # type: ignore[override]
        self,
        input_data: Dict[str, Any],
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Builds the JSON payload expected by the MoonDream server.

        Required keys in *input_data*:
            - "image_input" : path / PIL.Image / base64 string
            - "task"        : one of SUPPORTED_TASKS
        Optional:
            - "prompt"      : string prompt (task‑dependent)
            - "length"      : "short" | "normal" (for caption)
            - "max_new_tokens" : int
        """
        # --- validate -----------------------------------------------------
        task: str = input_data.get("task", "vqa").lower()

        image = load_image(input_data["image_input"])
        encoded_image = encode_image_to_base64(image)

        payload: Dict[str, Any] = {
            "image_input": encoded_image,
            "task": task,
            "max_new_tokens": int(input_data.get("max_new_tokens", 256)),
        }

        # task‑specific extras
        if task in {"vqa", "detect", "point"}:
            payload["prompt"] = input_data.get("prompt", "")
        if task == "caption":
            payload["length"] = input_data.get("length", "short")

        return payload

    # ------------- post‑processing --------------------------------------- #
    def postprocess(  # type: ignore[override]
        self,
        response: Dict[str, Any],
        *,
        task: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Decodes the server response into Python / NumPy objects.

        Args
        ----
        response : raw JSON from the API
        task     : (optional) duplicate of the task you sent; if not given,
                   it is inferred from response structure.

        Returns
        -------
        Dict with the same keys as server but `output` converted to
        * str        for vqa / caption
        * dict       with np.ndarrays for detect
        * np.ndarray (N,2) uint8 for point
        """
        if "output" not in response:
            return response  # pass‑through on error payloads

        # If caller didn't provide task, infer (cheap heuristic)
        if task is None:
            task = kwargs.get("task")

        # vqa / caption → already plain text
        if task in {"vqa", "caption"} or not isinstance(response["output"], str):
            return response

        # detect / point → base64‑encoded JSON
        try:
            decoded = json.loads(base64.b64decode(response["output"]))
        except Exception as e:
            response["decoding_error"] = str(e)
            return response

        if task == "point" or ("points" in decoded and "boxes" not in decoded):
            pts = np.asarray(decoded["points"], dtype=np.uint8)
            response["output"] = pts
        else:  # detect
            decoded["boxes"]  = np.asarray(decoded["boxes"], dtype=np.float32)
            decoded["scores"] = np.asarray(decoded["scores"], dtype=np.float32)
            decoded["labels"] = np.asarray(decoded["labels"])
            response["output"] = decoded

        return response