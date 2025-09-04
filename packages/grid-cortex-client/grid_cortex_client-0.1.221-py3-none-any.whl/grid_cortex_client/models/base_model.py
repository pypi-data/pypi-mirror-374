\
"""Base model for Cortex API interactions."""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import numpy as np
from PIL import Image

class BaseModel(ABC):
    """
    Abstract base class for all models.
    Each model implementation should define how to preprocess its specific input,
    postprocess the server's response, and optionally visualize the output.
    """

    def __init__(self, model_id: str):
        """
        Initializes the BaseModel.

        Args:
            model_id: A unique identifier for the model, used in the payload to the /run endpoint.
        """
        self.model_id = model_id

    @abstractmethod
    def preprocess(self, input_data: Any, **kwargs) -> Dict[str, Any]:
        """
        Preprocesses the input data into the format expected by the Cortex API's /run endpoint.

        Args:
            input_data: The raw input data (e.g., image path, numpy array, PIL Image).
            **kwargs: Additional keyword arguments for preprocessing.

        Returns:
            A dictionary representing the JSON payload for the /run endpoint.
            This payload should include the model_id and the processed input.
        """
        pass

    @abstractmethod
    def postprocess(self, response_data: Dict[str, Any], **kwargs) -> Any:
        """
        Postprocesses the JSON response from the Cortex API.

        Args:
            response_data: The JSON response from the API.
            **kwargs: Additional keyword arguments for postprocessing.

        Returns:
            The processed output in a user-friendly format (e.g., numpy array, custom object).
        """
        pass

    def visualize(self, processed_output: Any, original_input: Optional[Any] = None, **kwargs) -> None:
        """
        Optional method to visualize the processed output.
        Implementations should handle cases where visualization is not possible
        or not requested.

        Args:
            processed_output: The output from the postprocess method.
            original_input: The original input data, if needed for context in visualization.
            **kwargs: Additional keyword arguments for visualization.
        """
        print(f"Visualization not implemented for model {self.model_id}.")
