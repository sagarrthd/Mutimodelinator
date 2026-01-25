"""Abstract base class for all generators."""

import logging
import time
from abc import ABC, abstractmethod
from typing import Optional, Any, Dict
from utils.device_manager import get_device_manager
from utils.model_cache import load_pipeline, clear_all_cache
from utils.error_handler import ModelLoadError, InferenceError

logger = logging.getLogger(__name__)


class BaseGenerator(ABC):
    """Abstract base class for content generators."""

    def __init__(self, model_config: Dict[str, Any]):
        """Initialize generator with model configuration.
        
        Args:
            model_config: Configuration dictionary for the model
                Expected keys: repo_id, vram_estimate, etc.
                
        Raises:
            ValueError: If configuration is invalid
        """
        if not model_config or "repo_id" not in model_config:
            raise ValueError("Invalid model configuration")

        self.model_config = model_config
        self.repo_id = model_config["repo_id"]
        self.vram_estimate = model_config.get("vram_estimate", 4)
        self.device_manager = get_device_manager()
        self.pipeline = None
        self.last_generation_time = 0.0

    def load_model(self) -> bool:
        """Load the model pipeline.
        
        Returns:
            True if loading successful, False otherwise
            
        Raises:
            ModelLoadError: If model loading fails
        """
        try:
            # Check VRAM availability
            if not self.device_manager.has_sufficient_vram(self.vram_estimate):
                raise ModelLoadError(
                    f"Insufficient VRAM. Required: {self.vram_estimate}GB, "
                    f"Available: {self.device_manager.vram_available:.2f}GB",
                    user_message=f"Not enough GPU memory for this model. "
                    f"Requires {self.vram_estimate}GB, have {self.device_manager.vram_available:.2f}GB",
                )

            # Load pipeline
            dtype = self.device_manager.get_dtype()
            self.pipeline = load_pipeline(
                repo_id=self.repo_id,
                device=self.device_manager.device,
                dtype=dtype,
                use_safetensors=True,
            )

            # Apply optimizations
            self.device_manager.optimize_pipeline(self.pipeline)
            logger.info(f"Model loaded: {self.repo_id}")
            return True

        except Exception as e:
            logger.error(f"Model loading failed: {str(e)}")
            raise ModelLoadError(
                f"Failed to load {self.repo_id}: {str(e)}",
                user_message="Model loading failed. Check internet connection and try again.",
            ) from e

    def unload_model(self) -> None:
        """Unload the model to free VRAM."""
        if self.pipeline:
            try:
                # Clear caches
                clear_all_cache()
                self.pipeline = None
                logger.info(f"Model unloaded: {self.repo_id}")
            except Exception as e:
                logger.warning(f"Error unloading model: {e}")

    @abstractmethod
    def generate(self, **kwargs) -> Any:
        """Generate content. Must be implemented by subclass.
        
        Args:
            **kwargs: Generation parameters
            
        Returns:
            Generated content (varies by generator type)
            
        Raises:
            InferenceError: If generation fails
        """
        pass

    def _record_generation_time(self, seconds: float) -> None:
        """Record generation time for logging.
        
        Args:
            seconds: Duration of generation in seconds
        """
        self.last_generation_time = seconds
        logger.info(f"Generation completed in {seconds:.2f}s")

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded model.
        
        Returns:
            Dictionary with model information
        """
        return {
            "repo_id": self.repo_id,
            "vram_estimate": self.vram_estimate,
            "device": self.device_manager.device_name,
            "dtype": str(self.device_manager.get_dtype()),
            "loaded": self.pipeline is not None,
            "last_generation_time": self.last_generation_time,
        }
