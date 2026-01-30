"""
Input validation and parameter bounds checking.
Ensures all user inputs are safe and within acceptable ranges.
"""

import logging
from typing import Tuple

logger = logging.getLogger(__name__)


def validate_prompt(prompt: str, max_length: int = 2000) -> Tuple[bool, str]:
    """Validate text prompt for generation.
    
    Args:
        prompt: User-provided prompt text
        max_length: Maximum allowed prompt length
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not prompt or not isinstance(prompt, str):
        return False, "Prompt cannot be empty"

    prompt = prompt.strip()
    if len(prompt) == 0:
        return False, "Prompt cannot be empty or whitespace-only"

    if len(prompt) > max_length:
        return False, f"Prompt exceeds maximum length of {max_length} characters"

    # Check for suspicious patterns (security)
    if any(
        pattern in prompt.lower()
        for pattern in ["<script", "javascript:", "eval(", "exec("]
    ):
        return False, "Prompt contains invalid characters"

    return True, ""


def validate_image_dimensions(
    width: int, height: int, min_size: int = 256, max_size: int = 2048
) -> Tuple[bool, str]:
    """Validate image width and height.
    
    Args:
        width: Image width in pixels
        height: Image height in pixels
        min_size: Minimum allowed dimension
        max_size: Maximum allowed dimension
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(width, (int, float)) or not isinstance(height, (int, float)):
        return False, "Dimensions must be numbers"

    width, height = int(width), int(height)

    if width < min_size or height < min_size:
        return False, f"Minimum dimension is {min_size}px"

    if width > max_size or height > max_size:
        return False, f"Maximum dimension is {max_size}px"

    # Dimensions should be multiple of 64 for diffusion models
    if width % 64 != 0 or height % 64 != 0:
        return False, "Dimensions must be multiples of 64"

    return True, ""


def validate_steps(steps: int, min_steps: int = 1, max_steps: int = 100) -> Tuple[
    bool, str
]:
    """Validate inference steps.
    
    Args:
        steps: Number of inference steps
        min_steps: Minimum allowed steps
        max_steps: Maximum allowed steps
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(steps, (int, float)):
        return False, "Steps must be a number"

    steps = int(steps)

    if steps < min_steps or steps > max_steps:
        return False, f"Steps must be between {min_steps} and {max_steps}"

    return True, ""


def validate_guidance_scale(
    guidance: float, min_guidance: float = 1.0, max_guidance: float = 20.0
) -> Tuple[bool, str]:
    """Validate guidance scale for diffusion models.
    
    Args:
        guidance: Guidance scale value
        min_guidance: Minimum allowed value
        max_guidance: Maximum allowed value
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(guidance, (int, float)):
        return False, "Guidance scale must be a number"

    if guidance < min_guidance or guidance > max_guidance:
        return False, f"Guidance scale must be between {min_guidance} and {max_guidance}"

    return True, ""


def validate_seed(seed: int) -> Tuple[bool, str]:
    """Validate random seed value.
    
    Args:
        seed: Seed value (-1 for random, or 0-2^32-1)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(seed, (int, float)):
        return False, "Seed must be an integer"

    seed = int(seed)

    if seed != -1 and (seed < 0 or seed >= 2**32):
        return False, "Seed must be -1 (random) or between 0 and 4,294,967,295"

    return True, ""


def validate_duration(
    duration: float, min_duration: float = 1.0, max_duration: float = 30.0
) -> Tuple[bool, str]:
    """Validate audio/video duration.
    
    Args:
        duration: Duration in seconds
        min_duration: Minimum allowed duration
        max_duration: Maximum allowed duration
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(duration, (int, float)):
        return False, "Duration must be a number"

    if duration < min_duration or duration > max_duration:
        return False, f"Duration must be between {min_duration} and {max_duration} seconds"

    return True, ""


def validate_temperature(
    temperature: float, min_temp: float = 0.1, max_temp: float = 2.0
) -> Tuple[bool, str]:
    """Validate temperature parameter for generation.
    
    Args:
        temperature: Temperature value
        min_temp: Minimum allowed temperature
        max_temp: Maximum allowed temperature
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(temperature, (int, float)):
        return False, "Temperature must be a number"

    if temperature < min_temp or temperature > max_temp:
        return False, f"Temperature must be between {min_temp} and {max_temp}"

    return True, ""


def validate_fps(fps: int, min_fps: int = 4, max_fps: int = 30) -> Tuple[bool, str]:
    """Validate frames per second.
    
    Args:
        fps: Frames per second
        min_fps: Minimum allowed FPS
        max_fps: Maximum allowed FPS
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(fps, (int, float)):
        return False, "FPS must be a number"

    fps = int(fps)

    if fps < min_fps or fps > max_fps:
        return False, f"FPS must be between {min_fps} and {max_fps}"

    return True, ""


def validate_motion_bucket_id(
    motion_id: int, min_id: int = 1, max_id: int = 255
) -> Tuple[bool, str]:
    """Validate motion bucket ID for video generation.
    
    Args:
        motion_id: Motion bucket ID
        min_id: Minimum allowed ID
        max_id: Maximum allowed ID
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(motion_id, (int, float)):
        return False, "Motion bucket ID must be a number"

    motion_id = int(motion_id)

    if motion_id < min_id or motion_id > max_id:
        return False, f"Motion bucket ID must be between {min_id} and {max_id}"

    return True, ""


def validate_all_image_params(
    prompt: str,
    negative_prompt: str,
    width: int,
    height: int,
    steps: int,
    guidance: float,
    seed: int,
    min_steps: int = 1,
    max_steps: int = 100,
) -> Tuple[bool, str]:
    """Validate all image generation parameters at once.
    
    Args:
        prompt: Positive prompt
        negative_prompt: Negative prompt
        width: Image width
        height: Image height
        steps: Inference steps
        guidance: Guidance scale
        seed: Random seed
        min_steps: Min allowed steps
        max_steps: Max allowed steps
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Validate prompt
    valid, msg = validate_prompt(prompt)
    if not valid:
        return False, f"Prompt: {msg}"

    # Validate dimensions
    valid, msg = validate_image_dimensions(width, height)
    if not valid:
        return False, f"Dimensions: {msg}"

    # Validate steps
    valid, msg = validate_steps(steps, min_steps, max_steps)
    if not valid:
        return False, f"Steps: {msg}"

    # Validate guidance
    valid, msg = validate_guidance_scale(guidance)
    if not valid:
        return False, f"Guidance: {msg}"

    # Validate seed
    valid, msg = validate_seed(seed)
    if not valid:
        return False, f"Seed: {msg}"

    return True, ""
