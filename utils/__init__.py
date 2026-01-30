"""Utility modules for the offline AI generator."""

from .device_manager import DeviceManager, get_device_manager
from .error_handler import (
    GeneratorException,
    InferenceError,
    ModelLoadError,
    ValidationError,
    VRAMError,
    handle_generation_error,
    log_performance_metrics,
    setup_logging,
)
from .model_cache import clear_all_cache, load_pipeline, load_processor, run_inference
from .validators import (
    validate_all_image_params,
    validate_duration,
    validate_fps,
    validate_guidance_scale,
    validate_image_dimensions,
    validate_motion_bucket_id,
    validate_prompt,
    validate_seed,
    validate_steps,
    validate_temperature,
)

__all__ = [
    "DeviceManager",
    "get_device_manager",
    "load_pipeline",
    "load_processor",
    "clear_all_cache",
    "run_inference",
    "setup_logging",
    "GeneratorException",
    "ModelLoadError",
    "InferenceError",
    "VRAMError",
    "ValidationError",
    "handle_generation_error",
    "log_performance_metrics",
    "validate_prompt",
    "validate_image_dimensions",
    "validate_steps",
    "validate_guidance_scale",
    "validate_seed",
    "validate_duration",
    "validate_temperature",
    "validate_fps",
    "validate_motion_bucket_id",
    "validate_all_image_params",
]
