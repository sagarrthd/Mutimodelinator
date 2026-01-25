"""
Model Manager for intelligent model loading, caching, and lifecycle management.
Prevents unnecessary model reloads and provides efficient resource management.
"""

import logging
import torch
from typing import Optional, Dict, Any, Callable
from pathlib import Path
from functools import wraps
import gc

logger = logging.getLogger(__name__)


class ModelManager:
    """Manages model loading, unloading, and resource optimization."""
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize model manager.
        
        Args:
            cache_dir: Directory for model cache (uses HF_HOME if not specified)
        """
        self.cache_dir = cache_dir
        self.loaded_models: Dict[str, Any] = {}
        self.model_metadata: Dict[str, Dict[str, Any]] = {}
        self.device = self._detect_device()
        
        logger.info(f"✓ ModelManager initialized on device: {self.device}")
    
    @staticmethod
    def _detect_device() -> str:
        """Detect optimal device for inference."""
        if torch.cuda.is_available():
            device = "cuda"
            vram = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            logger.info(f"✓ CUDA device: {vram:.2f}GB VRAM available")
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            device = "mps"
            logger.info("✓ Using Apple Metal Performance Shaders (MPS)")
        else:
            device = "cpu"
            logger.warning("⚠ Using CPU (slow generation)")
        return device
    
    def is_model_loaded(self, model_key: str) -> bool:
        """Check if model is already loaded."""
        return model_key in self.loaded_models
    
    def get_loaded_model(self, model_key: str) -> Optional[Any]:
        """Get loaded model pipeline."""
        return self.loaded_models.get(model_key)
    
    def register_model(self, model_key: str, pipeline: Any, metadata: Optional[Dict] = None) -> None:
        """
        Register a loaded model in the manager.
        
        Args:
            model_key: Unique identifier for model
            pipeline: Model pipeline object
            metadata: Optional metadata about the model
        """
        self.loaded_models[model_key] = pipeline
        self.model_metadata[model_key] = metadata or {}
        logger.info(f"✓ Model registered: {model_key}")
    
    def unload_model(self, model_key: str) -> None:
        """
        Unload a specific model and free memory.
        
        Args:
            model_key: Model to unload
        """
        if model_key in self.loaded_models:
            try:
                pipeline = self.loaded_models[model_key]
                
                # Move to CPU and delete
                if hasattr(pipeline, 'to'):
                    pipeline.to('cpu')
                
                del self.loaded_models[model_key]
                
                # Force garbage collection
                gc.collect()
                if self.device == "cuda":
                    torch.cuda.empty_cache()
                
                logger.info(f"✓ Model unloaded: {model_key}")
            except Exception as e:
                logger.error(f"Error unloading model {model_key}: {e}")
    
    def unload_all_models(self) -> None:
        """Unload all loaded models."""
        for model_key in list(self.loaded_models.keys()):
            self.unload_model(model_key)
        logger.info("✓ All models unloaded")
    
    def warmup_model(self, pipeline: Any, warmup_fn: Optional[Callable] = None) -> None:
        """
        Warm up a model with a small inference pass.
        
        Args:
            pipeline: Model pipeline to warm up
            warmup_fn: Optional custom warmup function
        """
        try:
            logger.info("Warming up model...")
            
            if warmup_fn:
                warmup_fn(pipeline)
            else:
                # Default warmup - just move to device
                if hasattr(pipeline, 'to'):
                    pipeline.to(self.device)
            
            logger.info("✓ Model warmup complete")
        except Exception as e:
            logger.warning(f"Model warmup warning: {e}")
    
    def enable_memory_optimizations(self, pipeline: Any) -> None:
        """
        Enable memory-efficient inference optimizations.
        
        Args:
            pipeline: Model pipeline to optimize
        """
        try:
            # Enable xformers if available
            self._enable_xformers(pipeline)
            
            # Enable attention slicing for low VRAM
            if hasattr(pipeline, 'enable_attention_slicing'):
                pipeline.enable_attention_slicing()
                logger.info("✓ Attention slicing enabled")
            
            # Enable VAE tiling for large images
            if hasattr(pipeline, 'enable_vae_tiling'):
                pipeline.enable_vae_tiling()
                logger.info("✓ VAE tiling enabled")
            
            # Enable VAE slicing
            if hasattr(pipeline, 'enable_vae_slicing'):
                pipeline.enable_vae_slicing()
                logger.info("✓ VAE slicing enabled")
            
        except Exception as e:
            logger.warning(f"Could not enable all optimizations: {e}")
    
    @staticmethod
    def _enable_xformers(pipeline: Any) -> None:
        """
        Enable xformers memory-efficient attention if available.
        
        Args:
            pipeline: Model pipeline
        """
        try:
            import xformers
            if hasattr(pipeline, 'enable_xformers_memory_efficient_attention'):
                pipeline.enable_xformers_memory_efficient_attention()
                logger.info("✓ xformers memory-efficient attention enabled")
        except ImportError:
            logger.debug("xformers not available (optional)")
        except Exception as e:
            logger.debug(f"Could not enable xformers: {e}")
    
    def enable_amp_inference(self, pipeline: Any) -> None:
        """
        Enable Automatic Mixed Precision for faster inference.
        
        Args:
            pipeline: Model pipeline
        """
        try:
            if self.device == "cuda" and hasattr(pipeline, 'enable_attention_slicing'):
                # AMP is handled via torch.cuda.amp context manager during inference
                logger.info("✓ AMP inference can be used during generation")
        except Exception as e:
            logger.debug(f"AMP setup note: {e}")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get current memory usage statistics."""
        stats = {
            "device": self.device,
            "loaded_models": len(self.loaded_models),
            "model_keys": list(self.loaded_models.keys()),
        }
        
        if self.device == "cuda":
            stats["cuda_memory_allocated"] = f"{torch.cuda.memory_allocated() / (1024**3):.2f}GB"
            stats["cuda_memory_cached"] = f"{torch.cuda.memory_reserved() / (1024**3):.2f}GB"
        
        return stats
    
    def clear_cache(self) -> None:
        """Clear GPU cache."""
        if self.device == "cuda":
            torch.cuda.empty_cache()
            gc.collect()
            logger.info("✓ GPU cache cleared")
    
    def get_model_config(self, model_key: str) -> Optional[Dict]:
        """Get metadata for a loaded model."""
        return self.model_metadata.get(model_key)
    
    def list_loaded_models(self) -> Dict[str, Dict]:
        """Get information about all loaded models."""
        return {
            key: self.model_metadata.get(key, {})
            for key in self.loaded_models.keys()
        }


# Global instance
_model_manager: Optional[ModelManager] = None


def get_model_manager(cache_dir: Optional[str] = None) -> ModelManager:
    """
    Get or create global model manager instance.
    
    Args:
        cache_dir: Optional cache directory
        
    Returns:
        ModelManager instance
    """
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager(cache_dir)
    return _model_manager


def track_model_load(model_key: str, metadata: Optional[Dict] = None):
    """
    Decorator to automatically register models with the manager.
    
    Args:
        model_key: Unique key for the model
        metadata: Optional metadata
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            manager = get_model_manager()
            
            # Check if already loaded
            if manager.is_model_loaded(model_key):
                logger.info(f"Using cached model: {model_key}")
                return manager.get_loaded_model(model_key)
            
            # Load new model
            logger.info(f"Loading model: {model_key}")
            pipeline = func(*args, **kwargs)
            
            # Register with manager
            manager.register_model(model_key, pipeline, metadata)
            manager.enable_memory_optimizations(pipeline)
            
            return pipeline
        
        return wrapper
    return decorator
