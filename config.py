"""
Global configuration and model registry for the offline AI generator.
All model metadata is centralized here for easy maintenance and extension.
"""

# ==================== IMAGE GENERATION MODELS ====================
IMAGE_MODELS = {
    "FLUX.1-schnell (Fast, 12GB VRAM)": {
        "repo_id": "black-forest-labs/FLUX.1-schnell",
        "pipeline_class": "FluxPipeline",
        "vram_estimate": 12,
        "recommended_steps": 4,
        "default_guidance": 7.5,
        "min_steps": 1,
        "max_steps": 50,
    },
    "FLUX.1-dev (Quality, 16GB VRAM)": {
        "repo_id": "black-forest-labs/FLUX.1-dev",
        "pipeline_class": "FluxPipeline",
        "vram_estimate": 16,
        "recommended_steps": 20,
        "default_guidance": 7.5,
        "min_steps": 1,
        "max_steps": 100,
    },
    "Stable Diffusion 3 Medium (Modern, 8GB VRAM)": {
        "repo_id": "stabilityai/stable-diffusion-3-medium-diffusers",
        "pipeline_class": "StableDiffusion3Pipeline",
        "vram_estimate": 8,
        "recommended_steps": 28,
        "default_guidance": 5.0,
        "min_steps": 1,
        "max_steps": 100,
    },
    "SDXL 1.0 (Reliable, 10GB VRAM)": {
        "repo_id": "stabilityai/stable-diffusion-xl-base-1.0",
        "pipeline_class": "StableDiffusionXLPipeline",
        "vram_estimate": 10,
        "recommended_steps": 30,
        "default_guidance": 7.5,
        "min_steps": 1,
        "max_steps": 100,
    },
    "SD 1.5 (Fast, Low VRAM, 4GB)": {
        "repo_id": "runwayml/stable-diffusion-v1-5",
        "pipeline_class": "StableDiffusionPipeline",
        "vram_estimate": 4,
        "recommended_steps": 20,
        "default_guidance": 7.5,
        "min_steps": 1,
        "max_steps": 100,
    },
}

# ==================== AUDIO GENERATION MODELS ====================
AUDIO_MODELS = {
    "MusicGen Medium (Music, 6GB VRAM)": {
        "repo_id": "facebook/musicgen-medium",
        "task": "text-to-audio",
        "vram_estimate": 6,
        "max_duration": 30,
        "sample_rate": 16000,
    },
    "MusicGen Small (Music, Fast, 3GB VRAM)": {
        "repo_id": "facebook/musicgen-small",
        "task": "text-to-audio",
        "vram_estimate": 3,
        "max_duration": 30,
        "sample_rate": 16000,
    },
    "Bark (Speech + SFX, 5GB VRAM)": {
        "repo_id": "suno/bark",
        "task": "text-to-speech",
        "vram_estimate": 5,
        "max_duration": 15,
        "sample_rate": 24000,
    },
    "Bark Small (Speech, Fast, 3GB VRAM)": {
        "repo_id": "suno/bark-small",
        "task": "text-to-speech",
        "vram_estimate": 3,
        "max_duration": 15,
        "sample_rate": 24000,
    },
}

# ==================== VIDEO GENERATION MODELS ====================
VIDEO_MODELS = {
    "Stable Video Diffusion XT (img2vid, 16GB VRAM)": {
        "repo_id": "stabilityai/stable-video-diffusion-img2vid-xt",
        "pipeline_class": "StableVideoDiffusionPipeline",
        "type": "image-to-video",
        "vram_estimate": 16,
        "max_frames": 25,
        "fps": 6,
    },
    "Text-to-Video MS 1.7B (txt2vid, 12GB VRAM)": {
        "repo_id": "damo-vilab/text-to-video-ms-1.7b",
        "pipeline_class": "DiffusionPipeline",
        "type": "text-to-video",
        "vram_estimate": 12,
        "max_frames": 16,
        "fps": 8,
    },
    "ZeroScope V2 XL (txt2vid, 10GB VRAM)": {
        "repo_id": "cerspense/zeroscope_v2_XL",
        "pipeline_class": "DiffusionPipeline",
        "type": "text-to-video",
        "vram_estimate": 10,
        "max_frames": 24,
        "fps": 8,
    },
}

# ==================== DEVICE SETTINGS ====================
DEVICE_CONFIG = {
    "use_fp16": True,  # Enable float16 on CUDA for speedup
    "enable_attention_slicing": True,  # Memory optimization
    "enable_vae_slicing": True,  # For large images/videos
    "enable_vae_tiling": True,  # For extremely large resolutions
    "enable_model_cpu_offload": False,  # Set True for very low VRAM systems
    "use_torch_compile": False,  # Only on Python 3.11+, can slow down first run
}

# ==================== DEFAULT PARAMETERS ====================
DEFAULT_IMAGE_PARAMS = {
    "width": 1024,
    "height": 1024,
    "steps": 20,
    "guidance_scale": 7.5,
    "seed": -1,  # -1 means random
}

DEFAULT_AUDIO_PARAMS = {
    "duration_seconds": 10,
    "temperature": 1.0,
    "seed": -1,
}

DEFAULT_VIDEO_PARAMS = {
    "num_frames": 16,
    "fps": 8,
    "motion_bucket_id": 127,
    "seed": -1,
}

# ==================== UI CONFIGURATION ====================
GRADIO_THEME_CONFIG = {
    "primary_hue": "red",
    "secondary_hue": "slate",
    "neutral_hue": "slate",
}

# ==================== LOGGING & PATHS ====================
LOG_FILE = "generator.log"
MODEL_CACHE_DIR = None  # Will use default HF_HOME or TRANSFORMERS_CACHE

# ==================== PERFORMANCE SETTINGS ====================
MAX_CONCURRENT_OPERATIONS = 1  # Queue only 1 generation at a time
INFERENCE_TIMEOUT_SECONDS = 600  # 10 minute timeout per generation
VRAM_SAFETY_MARGIN_GB = 1  # Keep this much VRAM free

# ==================== EXAMPLE PROMPTS ====================
EXAMPLE_PROMPTS = {
    "image": [
        "A serene mountain landscape with snow-capped peaks at sunrise, golden light, photorealistic",
        "Cyberpunk city street with neon signs, flying cars, detailed, 4K",
        "A cozy bookshop interior with warm lighting and wooden shelves, atmospheric lighting",
        "Medieval fantasy castle on a cliff overlooking a misty valley",
        "Abstract geometric patterns with iridescent colors and chrome surfaces",
    ],
    "audio": [
        "Epic orchestral music with dramatic strings and powerful drums",
        "Ambient electronic lofi beats with synthesizers and chill vibes",
        "Jazz ensemble with saxophone, upright bass, and drums in a classic club",
        "Nature sounds: rain on leaves with distant thunder",
        "Upbeat pop music with catchy melody and modern production",
    ],
    "video": [
        "A rotating golden sphere with reflective surface on dark background",
        "Ocean waves crashing on a sunny beach with seagulls flying",
        "Abstract particles flowing and morphing into geometric shapes",
        "A person walking through a forest with dappled sunlight",
        "Swirling galaxy with stars and nebula clouds",
    ],
}

# ==================== NEGATIVE PROMPTS ====================
NEGATIVE_PROMPT_TEMPLATES = {
    "image": "blurry, low quality, distorted, ugly, bad anatomy, worst quality, artifacts",
    "video": "static, jerky, blurry motion, inconsistent",
}
