"""
Pipeline caching and lazy loading for efficient memory management.
Ensures only one model is loaded at a time, with smart caching.
"""

import logging
from typing import Union

import torch
from diffusers import DiffusionPipeline
from transformers import AutoProcessor

logger = logging.getLogger(__name__)

# Global cache storage
_pipeline_cache: dict = {}
_processor_cache: dict = {}


def clear_all_cache() -> None:
    """Clear all cached pipelines and processors."""
    global _pipeline_cache, _processor_cache
    for pipeline in _pipeline_cache.values():
        if hasattr(pipeline, "to"):
            pipeline.to("cpu")
        del pipeline
    _pipeline_cache.clear()
    _processor_cache.clear()
    torch.cuda.empty_cache() if torch.cuda.is_available() else None
    logger.info("All cache cleared")


def load_pipeline(
    repo_id: str,
    device: str = "cuda",
    dtype: torch.dtype = torch.float16,
    use_safetensors: bool = True,
) -> DiffusionPipeline:
    """Load or retrieve cached pipeline.
    
    Args:
        repo_id: HuggingFace model repository ID
        device: Target device ('cuda', 'cpu', 'mps')
        dtype: Data type for model (torch.float16 or torch.float32)
        use_safetensors: Use safetensors format if available
        
    Returns:
        Loaded DiffusionPipeline instance
        
    Raises:
        RuntimeError: If model download fails or loading error occurs
    """
    cache_key = f"{repo_id}_{device}_{dtype}"

    # Return cached pipeline if available
    if cache_key in _pipeline_cache:
        logger.info(f"Using cached pipeline: {repo_id}")
        return _pipeline_cache[cache_key]

    logger.info(f"Loading pipeline from {repo_id}...")

    try:
        # Use generic DiffusionPipeline loader (auto-detects pipeline type)
        pipeline = DiffusionPipeline.from_pretrained(
            repo_id,
            torch_dtype=dtype,
            use_safetensors=use_safetensors,
            variant="fp16" if dtype == torch.float16 else None,
        )

        # Move to target device
        pipeline = pipeline.to(device)
        logger.info(f"✓ Pipeline loaded: {repo_id}")

        # Cache the pipeline
        _pipeline_cache[cache_key] = pipeline
        return pipeline

    except Exception as e:
        logger.error(f"Failed to load pipeline {repo_id}: {str(e)}")
        raise RuntimeError(f"Pipeline loading failed: {str(e)}") from e


def load_processor(repo_id: str) -> AutoProcessor:
    """Load or retrieve cached processor.
    
    Args:
        repo_id: HuggingFace model repository ID
        
    Returns:
        Loaded processor instance
        
    Raises:
        RuntimeError: If processor load fails
    """
    if repo_id in _processor_cache:
        logger.info(f"Using cached processor: {repo_id}")
        return _processor_cache[repo_id]

    logger.info(f"Loading processor from {repo_id}...")

    try:
        processor = AutoProcessor.from_pretrained(repo_id)
        _processor_cache[repo_id] = processor
        logger.info(f"✓ Processor loaded: {repo_id}")
        return processor

    except Exception as e:
        logger.error(f"Failed to load processor {repo_id}: {str(e)}")
        raise RuntimeError(f"Processor loading failed: {str(e)}") from e


@torch.inference_mode()
def run_inference(
    pipeline: DiffusionPipeline,
    device: str = "cuda",
    use_amp: bool = True,
    **kwargs,
) -> Union[dict, list]:
    """Run inference with automatic mixed precision and optimization.
    
    Args:
        pipeline: DiffusionPipeline to use
        device: Target device
        use_amp: Use automatic mixed precision
        **kwargs: Additional arguments to pass to pipeline
        
    Returns:
        Pipeline output (varies by pipeline type)
        
    Raises:
        RuntimeError: If inference fails or CUDA OOM
    """
    try:
        # Use automatic mixed precision for faster inference
        if use_amp and device == "cuda":
            with torch.cuda.amp.autocast(enabled=True, dtype=torch.float16):
                output = pipeline(**kwargs)
        else:
            output = pipeline(**kwargs)

        return output

    except torch.cuda.OutOfMemoryError:
        logger.error("GPU out of memory!")
        torch.cuda.empty_cache()
        raise RuntimeError(
            "GPU ran out of memory. Try a smaller model or reduce output resolution."
        )
    except Exception as e:
        logger.error(f"Inference failed: {str(e)}")
        raise RuntimeError(f"Inference error: {str(e)}") from e


def unload_pipeline(repo_id: str, device: str, dtype: torch.dtype) -> None:
    """Manually unload a cached pipeline.
    
    Args:
        repo_id: Model repository ID
        device: Device the model was loaded on
        dtype: Data type of the model
    """
    cache_key = f"{repo_id}_{device}_{dtype}"
    if cache_key in _pipeline_cache:
        del _pipeline_cache[cache_key]
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        logger.info(f"Unloaded pipeline: {repo_id}")


def get_cache_info() -> dict:
    """Get information about current cache state.
    
    Returns:
        Dictionary with cache statistics
    """
    return {
        "cached_pipelines": len(_pipeline_cache),
        "cached_processors": len(_processor_cache),
        "pipeline_keys": list(_pipeline_cache.keys()),
        "processor_keys": list(_processor_cache.keys()),
    }
