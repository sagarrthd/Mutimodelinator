"""
Device manager for GPU/CPU detection and optimization.
Automatically configures torch for optimal performance based on available hardware.
"""

import logging
from typing import Dict

import psutil
import torch

logger = logging.getLogger(__name__)


class DeviceManager:
    """Manages device selection and optimization for inference."""

    def __init__(self):
        """Initialize device manager with hardware detection."""
        self.device = self._detect_device()
        self.device_name = self._get_device_name()
        self.vram_total = self._get_vram_total()
        self.vram_available = self._get_vram_available()
        self.ram_available = psutil.virtual_memory().available / (1024**3)  # GB
        logger.info(f"Device: {self.device_name}")
        logger.info(f"Total VRAM: {self.vram_total:.2f} GB")
        logger.info(f"Available VRAM: {self.vram_available:.2f} GB")
        logger.info(f"Available RAM: {self.ram_available:.2f} GB")

    def _detect_device(self) -> str:
        """Detect available compute device (CUDA, MPS, or CPU)."""
        if torch.cuda.is_available():
            return "cuda"
        elif torch.backends.mps.is_available():
            # Apple Silicon GPU support
            return "mps"
        else:
            return "cpu"

    def _get_device_name(self) -> str:
        """Get human-readable device name."""
        if self.device == "cuda":
            return f"NVIDIA {torch.cuda.get_device_name(0)}"
        elif self.device == "mps":
            return "Apple Metal Performance Shaders"
        else:
            return "CPU"

    def _get_vram_total(self) -> float:
        """Get total VRAM in GB. Returns 0 for CPU."""
        if self.device == "cuda":
            return torch.cuda.get_device_properties(0).total_memory / (1024**3)
        return 0

    def _get_vram_available(self) -> float:
        """Get available VRAM in GB. Returns 0 for CPU."""
        if self.device == "cuda":
            return torch.cuda.mem_get_info()[0] / (1024**3)
        return 0

    def has_sufficient_vram(self, required_vram_gb: float) -> bool:
        """Check if device has sufficient VRAM for model loading."""
        if self.device == "cpu":
            return True  # CPU uses system RAM, assume sufficient
        return self.vram_available >= required_vram_gb * 1.1  # 10% safety margin

    def optimize_pipeline(self, pipeline) -> None:
        """Apply optimization settings to a diffusion pipeline.
        
        Args:
            pipeline: Diffusion pipeline to optimize
        """
        logger.info("Applying pipeline optimizations...")

        # Enable memory-saving techniques
        if hasattr(pipeline, "enable_attention_slicing"):
            pipeline.enable_attention_slicing(slice_size="auto")
            logger.info("✓ Attention slicing enabled")

        if hasattr(pipeline, "enable_vae_slicing"):
            pipeline.enable_vae_slicing()
            logger.info("✓ VAE slicing enabled")

        if hasattr(pipeline, "enable_vae_tiling"):
            pipeline.enable_vae_tiling()
            logger.info("✓ VAE tiling enabled")

        # Model CPU offload for very low VRAM systems
        if self.vram_total < 4:
            if hasattr(pipeline, "enable_model_cpu_offload"):
                pipeline.enable_model_cpu_offload(gpu_id=0)
                logger.info("✓ Model CPU offload enabled (low VRAM mode)")

        # Torch compile for inference speedup (Python 3.11+ only)
        if hasattr(torch, "compile") and hasattr(pipeline, "unet"):
            try:
                # Only compile on capable devices and if enough VRAM
                if self.device == "cuda" and self.vram_total >= 8:
                    # torch.compile is still experimental, wrap in try-except
                    try:
                        pipeline.unet = torch.compile(
                            pipeline.unet, mode="reduce-overhead", fullgraph=False
                        )
                        logger.info("✓ UNet compiled for faster inference")
                    except Exception as e:
                        logger.warning(f"Torch compilation failed: {e}")
            except Exception as e:
                logger.debug(f"Torch.compile not available: {e}")

    def get_dtype(self) -> torch.dtype:
        """Get optimal dtype for current device."""
        if self.device == "cuda" and self.vram_available > 2:
            return torch.float16
        return torch.float32

    def get_inference_dtype(self) -> Dict[str, torch.dtype]:
        """Get dtype configuration for inference."""
        dtype = self.get_dtype()
        return {"torch_dtype": dtype}

    def clear_cache(self) -> None:
        """Clear CUDA cache to free up memory."""
        if self.device == "cuda":
            torch.cuda.empty_cache()
            logger.info("CUDA cache cleared")

    def get_status(self) -> str:
        """Get formatted device status string."""
        status = f"Device: {self.device_name}\n"
        if self.device == "cuda":
            status += f"VRAM: {self.vram_available:.2f} / {self.vram_total:.2f} GB\n"
        status += f"System RAM: {self.ram_available:.2f} GB available"
        return status
    
    def get_device_info(self) -> str:
        """Get brief device information string."""
        if self.device == "cuda":
            return f"{self.vram_available:.1f}/{self.vram_total:.1f}GB VRAM"
        elif self.device == "mps":
            return "Apple Silicon"
        else:
            return f"{self.ram_available:.1f}GB RAM"

    def estimate_inference_time(self, model_vram_gb: float, steps: int = 20) -> str:
        """Estimate inference time based on device and parameters.
        
        Args:
            model_vram_gb: Estimated VRAM requirement of model
            steps: Number of inference steps
            
        Returns:
            Estimated time string (e.g., "12-18 seconds")
        """
        if self.device == "cuda":
            # Rough estimation: each step takes ~0.5s per 10GB VRAM
            base_time = (steps * 0.5) * (model_vram_gb / 10)
            return f"{int(base_time * 0.7)}-{int(base_time * 1.3)} seconds"
        else:
            # CPU is much slower, rough 10x multiplier
            base_time = (steps * 5) * (model_vram_gb / 10)
            return f"{int(base_time * 0.7)}-{int(base_time * 1.3)} seconds"


# Global device manager instance
_device_manager = None


def get_device_manager() -> DeviceManager:
    """Get or create global device manager instance."""
    global _device_manager
    if _device_manager is None:
        _device_manager = DeviceManager()
    return _device_manager
