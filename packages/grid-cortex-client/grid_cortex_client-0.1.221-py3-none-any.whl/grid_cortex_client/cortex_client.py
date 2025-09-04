# filepath: /home/pranay/GRID/Grid-Cortex-Infra/grid-cortex-client/src/grid_cortex_client/cortex_client.py
import logging
from typing import Any, Dict, Optional, Type # Added Type

from PIL import Image # Add this import

from .client import (CortexAPIError, CortexNetworkError, HTTPClient)
from .preprocessing import load_image, encode_image_to_base64 # Add this import
from .postprocessing import postprocess_depth_response, postprocess_detection_response # Add postprocess_detection_response
from .models.base_model import BaseModel
from .models.depth import DepthModel
from .models.detection import DetectionModel
from .models.segmentation import SegmentationModel, SAM2Model
from .models.vlm import VLMModel, MoonDreamModel
from .models.matching import MatchingModel
from .models.grasp import GraspModel
from .models.stereo import FoundationStereoModel
from .models.graspgen import GraspGenModel

logger = logging.getLogger(__name__)

class CortexClient:
    """Client for interacting with Grid Cortex Ray Serve deployments."""

    # Client-side registry to map model_id keywords to handler classes
    _MODEL_ID_TO_HANDLER_CLASS: Dict[str, Type[BaseModel]] = {
        "midas": DepthModel,
        "marigold": DepthModel, # Example keyword for depth models
        "depthpro": DepthModel, # Example keyword for depth models
        "metric3d": DepthModel, # Example keyword for depth models
        "depthanything2": DepthModel, # Example keyword for depth models
        "zoedepth": DepthModel, # Example keyword for depth models
        "grounding-dino": DetectionModel,
        "owlv2": DetectionModel, # Added owlv2 mapping to DetectionModel
        "sam2": SAM2Model, # Example keyword for SAM-like models
        "clipseg": SegmentationModel, # Example keyword for LSeg
        "oneformer": SegmentationModel, # Example keyword for OneFormer
        "lseg": SegmentationModel, # Example keyword for LSeg
        "gsam2": SegmentationModel, # Example keyword for G-SAM2        # Add more mappings here as new model types are supported
        "rtdetr": DetectionModel, # Example keyword for RT-DETR
        "moondream": MoonDreamModel, # Added MoonDreamModel mapping to VLMModel
        "llava": VLMModel, # Added LLAVA mapping to VLMModel
        "molmo": VLMModel, # Added MolModel mapping to VLMModel
        "phi4": VLMModel, # Added Phi4 mapping to VLMModel
        "magma": VLMModel, # Added Magma mapping to VLMModel
        "lightglue": MatchingModel,
        "robobrain2": VLMModel, # Added RoboBrain-2 mapping to VLMModel
        "vggt": DepthModel,
        "robopoint": VLMModel, # Added RoboPoint mapping to VLMModel
        "m2t2": GraspModel,
        "foundationstereo": FoundationStereoModel, # Added FoundationStereo mapping
        "graspgen": GraspGenModel, # Added GraspGen mapping
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None, # This will be used to set HTTPClient's base_url
        timeout: float = 30.0,
    ):
        """
        Initializes the CortexClient.

        Args:
            api_key: API key. Uses GRID_CORTEX_API_KEY env var if None.
            base_url: Base URL of the Cortex API. If None, uses GRID_CORTEX_BASE_URL env var or HTTPClient's default.
            timeout: Default timeout for HTTP requests in seconds.
        """
        # Pass base_url to HTTPClient constructor
        self.http_client = HTTPClient(api_key=api_key, base_url=base_url, timeout=timeout)
        
        effective_http_base_url = self.http_client._client.base_url # Access the actual base_url used by httpx.Client
        logger.info(f"CortexClient initialized. HTTPClient target: {effective_http_base_url}")

    def _make_request(
        self,
        endpoint: str, 
        payload: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None, # Added timeout parameter
    ) -> Dict[str, Any]:
        """Helper method to make POST requests to the /run endpoint."""
        try:
            # All model interactions go through a unified /run endpoint via POST
            # Pass the timeout to the http_client.post method
            return self.http_client.post(endpoint, json=payload, timeout=timeout)
        except (CortexAPIError, CortexNetworkError) as e:
            logger.error(f"Request to {endpoint} failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during request to {endpoint}: {e}")
            raise CortexNetworkError(f"An unexpected error occurred: {e}") from e

    def run_model(
        self,
        model: BaseModel,
        input_data: Any,
        preprocess_kwargs: Optional[Dict[str, Any]] = None,
        postprocess_kwargs: Optional[Dict[str, Any]] = None,
        visualize: bool = False,
        visualization_kwargs: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None, # Added timeout parameter
    ) -> Any:
        """
        Runs a specified model with the given input data.

        This method orchestrates the preprocessing, API request, postprocessing,
        and optional visualization steps.

        Args:
            model: An instance of a BaseModel subclass (e.g., DepthModel).
            input_data: The raw input data for the model.
            preprocess_kwargs: Additional keyword arguments for the model's preprocess method.
            postprocess_kwargs: Additional keyword arguments for the model's postprocess method.
            visualize: If True, attempts to run the model's visualize method.
            visualization_kwargs: Additional keyword arguments for the model's visualize method.
            timeout: Optional timeout in seconds for the request.

        Returns:
            The processed output from the model.
            
        Raises:
            CortexAPIError: If the API returns an error.
            CortexNetworkError: If a network error occurs.
            ValueError: If preprocessing or postprocessing fails.
        """
        logger.info(f"Running model {model.model_id} with input type: {type(input_data)}")

        _preprocess_kwargs = preprocess_kwargs or {}
        _postprocess_kwargs = postprocess_kwargs or {}
        _visualization_kwargs = visualization_kwargs or {}

        try:
            payload = model.preprocess(input_data, **_preprocess_kwargs)
            # Ensure model_id from the model instance is in the payload.
            # Only warn if 'model_id' is present in the payload but incorrect.
            # If 'model_id' is missing, run_model will add it, which is expected.
            if "model_id" in payload and payload["model_id"] != model.model_id:
                logger.warning(
                    f"Payload 'model_id' ('{payload.get('model_id')}') from preprocess "
                    f"does not match model instance's model_id ('{model.model_id}'). "
                    f"Overwriting with instance's model_id."
                )
            elif "model_id" not in payload:
                logger.debug( # Log at debug level if model_id is simply missing from preprocess output
                    f"Payload from preprocess for model '{model.model_id}' does not contain 'model_id'. "
                    f"'{self.__class__.__name__}.run_model' will add it."
                )
            payload["model_id"] = model.model_id # Ensure it's there and correct.
            
        except Exception as e:
            logger.error(f"Preprocessing failed for model {model.model_id}: {e}", exc_info=True)
            raise ValueError(f"Preprocessing error for {model.model_id}: {e}") from e

        # Construct the endpoint using the model's model_id
        # e.g., /depth-anything-v2-large/run
        # The HTTPClient will prepend its base_url (e.g., https://cortex-stage.generalrobotics.dev)
        specific_model_endpoint = f"/{model.model_id}/run"
        
        logger.info(f"Requesting model execution from: {specific_model_endpoint} for model_id: {model.model_id}")
        
        # Pass timeout to _make_request
        api_response = self._make_request(specific_model_endpoint, payload=payload, timeout=timeout)
        logger.info(f"API response for model {model.model_id}: {api_response}") # Log the API response

        try:
            _postprocess_kwargs['model_name'] = model.model_id
            processed_output = model.postprocess(api_response, **_postprocess_kwargs)
        except Exception as e:
            logger.error(f"Postprocessing failed for model {model.model_id}: {e}", exc_info=True)
            # Consider re-raising a more specific error or just re-raising
            raise ValueError(f"Postprocessing error for {model.model_id}: {e}") from e

        if visualize:
            try:
                logger.info(f"Attempting visualization for model {model.model_id}.")
                # Pass original input data to visualize method if it might be needed
                model.visualize(processed_output, original_input=input_data, **_visualization_kwargs)
            except Exception as e:
                logger.error(f"Visualization failed for model {model.model_id}: {e}", exc_info=True)
                # Do not re-raise visualization errors, just log them.
        
        logger.info(f"Successfully ran model {model.model_id}.")
        return processed_output

    def run(
        self,
        model_id: str,
        timeout: Optional[float] = None,
        debug: bool = False, # Added debug parameter
        **kwargs: Any 
    ) -> Any:
        """
        Runs a model by its ID with the given input data using keyword arguments.

        This method simplifies model execution by:
        1. Identifying the appropriate model handler based on model_id.
        2. Instantiating the handler.
        3. Passing all keyword arguments (**kwargs) to the handler's preprocess method
           via the run_model method.

        Args:
            model_id: The identifier of the model to run.
            timeout: Optional timeout in seconds for the request.
            debug: If True, sets the library's logger level to DEBUG for this call.
            **kwargs: Arbitrary keyword arguments that will be passed as a dictionary
                      to the model handler's preprocess method. This should include
                      all necessary inputs for the model (e.g., image_input, text_prompts).

        Returns:
            The processed output from the model.

        Raises:
            CortexAPIError: If the API returns an error.
            CortexNetworkError: If a network error occurs.
            NotImplementedError: If no suitable model handler is found for the model_id.
            ValueError: If preprocessing or postprocessing within the handler fails.
        """
        # Store original logging level
        original_level = None
        library_logger = logging.getLogger("grid_cortex_client") # Get the library's root logger

        if debug:
            original_level = library_logger.getEffectiveLevel()
            library_logger.setLevel(logging.DEBUG)
            # Ensure there's a handler that outputs debug messages, e.g., to console for the debug session
            # This is tricky as libraries shouldn't add handlers. 
            # For a temporary debug flag, we might add a temporary console handler if none exist
            # or rely on the application to have configured one.
            # For simplicity here, we'll assume if debug=True, the user wants to see logs
            # and might have a handler. If not, they won't see them despite level change.
            # A more robust solution might involve a context manager for logging level.
            logger.info(f"Debug mode enabled for this run. Setting grid_cortex_client logger to DEBUG.")

        logger.info(f"Attempting to run model '{model_id}' with inputs: {list(kwargs.keys())}")

        HandlerClass = None
        for keyword, HClass in self._MODEL_ID_TO_HANDLER_CLASS.items():
            if keyword in model_id.lower():
                HandlerClass = HClass
                logger.info(f"Found handler {HandlerClass.__name__} for model_id '{model_id}' based on keyword '{keyword}'.")
                break
        
        if HandlerClass is None:
            logger.error(f"No suitable model handler found for model_id: {model_id}. "
                         f"Available handlers are for keywords: {list(self._MODEL_ID_TO_HANDLER_CLASS.keys())}")
            raise NotImplementedError(
                f"No model handler configured for model_id containing typical keywords for known types: '{model_id}'. "
                f"Please ensure the model_id is correct or update the client's model handler registry."
            )

        try:
            # Instantiate the handler
            model_handler = HandlerClass(model_id=model_id)
            
            # The `run_model` method expects `input_data` which will be passed to the
            # handler's `preprocess` method. We pass the collected `kwargs` directly.
            # The handler's `preprocess` method is responsible for interpreting these kwargs.
            # The `http_client.post` within `run_model` will use its own default timeout
            # if `timeout` is not explicitly managed by `run_model` or `_make_request`.
            # For now, the `timeout` parameter in `run` is not directly plumbed into `run_model`
            # as `run_model` doesn't have a top-level timeout arg.
            # The `HTTPClient.post` method, called by `_make_request`, does accept a timeout.
            # This could be a point of future refinement if per-call timeout in `run()` needs
            # to override the client's default when using `run_model`.
            # However, the original `run` method *did* pass timeout to `http_client.post`.
            # To maintain that, we'd need to adjust `run_model` or how it calls `_make_request`.

            # For simplicity and consistency with `run_model`'s current signature,
            # we are not passing the `timeout` from `run` to `run_model` here.
            # The `http_client` will use its configured default or the one passed during its init.
            # If a per-call timeout override is needed here, `run_model` or `_make_request`
            # would need modification.

            # Let's reconsider: The original `run` method's `http_client.post` call *did* use the `timeout` parameter.
            # The `_make_request` method in `run_model` does not currently accept `timeout`.
            # To honor the `timeout` parameter in `run()`, we should adjust `_make_request` or `HTTPClient.post`
            # handling within `run_model`.

            # Simplest immediate path: Modify `_make_request` to accept timeout.
            # This is a bit of a detour from just refactoring `run`, but important for functionality.
            # Let's assume for now `_make_request` will be updated or `run_model` handles it.
            # The current `run_model` calls `self._make_request(specific_model_endpoint, payload=payload)`
            # which doesn't pass timeout.

            # Given the current structure, the `timeout` in `run()` will not be used if we directly call `run_model`.
            # The original `run` method's `self.http_client.post(endpoint_path, json=payload, timeout=timeout)`
            # directly used the timeout.

            # To preserve the timeout functionality when calling from the simplified `run` method,
            # we need to ensure it's passed down.
            # One way is to make `run_model` accept a timeout.
            # Another is to bypass `run_model` if `run` is meant to be a truly simplified path
            # that handles its own HTTP call after getting the payload from the handler.
            #
            # The goal of `run_model` is to be the comprehensive orchestrator.
            # Let's stick to calling `run_model`. The `timeout` in `run` might be considered
            # an override for this specific call.
            #
            # For now, I will proceed with calling `run_model`. The `timeout` from `run`
            # will effectively be ignored by `run_model` unless `run_model` or `_make_request` is changed.
            # This is a point to clarify or address in a subsequent step if precise timeout control
            # from `run()` through `run_model()` is critical.

            # The `preprocess_kwargs` and `postprocess_kwargs` in `run_model` are for additional args
            # to those methods, not for the primary input data.
            # Pass the timeout from run to run_model
            output = self.run_model(
                model=model_handler,
                input_data=kwargs, # Pass all kwargs as the input_data dictionary
                timeout=timeout # Pass timeout here
            )
            return output

        except (CortexAPIError, CortexNetworkError, ValueError, NotImplementedError) as e:
            # Re-raise known errors
            logger.error(f"Error running model '{model_id}': {e}", exc_info=True)
            raise
        except Exception as e:
            # Catch any other unexpected errors
            logger.error(f"Unexpected error running model '{model_id}': {e}", exc_info=True)
            raise CortexNetworkError(f"An unexpected error occurred while running model {model_id}: {e}") from e
        finally:
            if debug and original_level is not None:
                library_logger.setLevel(original_level)
                logger.info(f"Debug mode disabled. Restored grid_cortex_client logger level to {logging.getLevelName(original_level)}.")

    def close(self):
        """Closes the underlying HTTP client."""
        self.http_client.close()
        logger.info("CortexClient closed.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

