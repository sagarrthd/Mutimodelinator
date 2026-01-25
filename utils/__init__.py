"""Utility modules for the offline AI generator."""

from .device_manager import DeviceManager, get_device_manager
from .model_cache import load_pipeline, load_processor, clear_all_cache, run_inference
from .error_handler import (
    setup_logging,
    GeneratorException,
    ModelLoadError,
    InferenceError,
    VRAMError,
    ValidationError,
    handle_generation_error,
    log_performance_metrics,
)
from .validators import (
    validate_prompt,
    validate_image_dimensions,
    validate_steps,
    validate_guidance_scale,
    validate_seed,
    validate_duration,
    validate_temperature,
    validate_fps,
    validate_motion_bucket_id,
    validate_all_image_params,
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
