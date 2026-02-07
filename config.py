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
    "ACE Step 1.5 (Music + Lyrics, High Quality)": {
        "repo_id": "ACE-Step/Ace-Step1.5",
        "task": "text-to-audio",
        "vram_estimate": 12,
        "max_duration": 60,
        "sample_rate": 44100,
    },
    "Qwen3-TTS 1.7B (Speech, Multilingual)": {
        "repo_id": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
        "task": "text-to-speech",
        "vram_estimate": 8,
        "max_duration": 30,
        "sample_rate": 24000,
    },
}

# ==================== MUSIC STUDIO MODELS (SUNO-LIKE) ====================
# Ordered by VRAM requirement (lowest first for easier selection)
MUSIC_STUDIO_MODELS = {
    "MusicGen Small (Low VRAM, 4GB)": {
        "repo_id": "facebook/musicgen-small",
        "task": "music-generation",
        "vram_estimate": 4,
        "max_duration": 30,
        "sample_rate": 32000,
        "supports_lyrics": False,
        "supports_vocals": False,
        "supports_reference": True,
        "quality": "good",
        "description": "Lightweight music generator. Great for low-VRAM systems.",
    },
    "MusicGen Medium (Balanced, 6GB)": {
        "repo_id": "facebook/musicgen-medium",
        "task": "music-generation",
        "vram_estimate": 6,
        "max_duration": 30,
        "sample_rate": 32000,
        "supports_lyrics": False,
        "supports_vocals": False,
        "supports_reference": True,
        "quality": "high",
        "description": "Balanced quality and speed. Good for 6GB+ VRAM systems.",
    },
    "Stable Audio Open (Fast, 8GB)": {
        "repo_id": "stabilityai/stable-audio-open-small",
        "task": "music-generation",
        "vram_estimate": 8,
        "max_duration": 47,
        "sample_rate": 44100,
        "supports_lyrics": False,
        "supports_vocals": False,
        "supports_reference": False,
        "quality": "high",
        "description": "Fast instrumental generation. Great for background music.",
    },
    "Qwen3-TTS 1.7B (Speech, 8GB)": {
        "repo_id": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
        "task": "text-to-speech",
        "vram_estimate": 8,
        "max_duration": 30,
        "sample_rate": 24000,
        "supports_lyrics": True,
        "supports_vocals": True,
        "supports_reference": False,
        "quality": "high",
        "description": "Multilingual speech synthesis for voice-overs.",
    },
    "MusicGen Large (Quality, 10GB)": {
        "repo_id": "facebook/musicgen-large",
        "task": "music-generation",
        "vram_estimate": 10,
        "max_duration": 30,
        "sample_rate": 32000,
        "supports_lyrics": False,
        "supports_vocals": False,
        "supports_reference": True,
        "quality": "high",
        "description": "High quality with melody conditioning.",
    },
    "ACE Step 1.5 (Vocals + Lyrics, 12GB)": {
        "repo_id": "ACE-Step/Ace-Step1.5",
        "task": "music-generation",
        "vram_estimate": 12,
        "max_duration": 60,
        "sample_rate": 44100,
        "supports_lyrics": True,
        "supports_vocals": True,
        "supports_reference": True,
        "quality": "commercial",
        "description": "Commercial-grade with vocals and lyrics support.",
    },
    "HeartMuLa 3B (Studio, 14GB)": {
        "repo_id": "HeartMuLa/HeartMuLa-oss-3B",
        "task": "music-generation",
        "vram_estimate": 14,
        "max_duration": 120,
        "sample_rate": 44100,
        "supports_lyrics": True,
        "supports_vocals": True,
        "supports_reference": True,
        "quality": "studio",
        "description": "Studio-grade music comparable to Suno v5.",
    },
}

# ==================== MUSIC GENERATION PARAMETERS ====================
MUSIC_GENRES = [
    "Pop", "Rock", "Hip-Hop", "Electronic/EDM", "Jazz", "Classical",
    "Country", "R&B/Soul", "Blues", "Reggae", "Metal", "Folk",
    "Latin", "K-Pop", "Indie", "Punk", "Disco", "Funk",
    "Ambient", "Lo-fi", "Trap", "House", "Techno", "Dubstep"
]

MUSIC_MOODS = [
    "Energetic", "Calm/Relaxing", "Happy/Upbeat", "Sad/Melancholic",
    "Aggressive", "Romantic", "Epic/Cinematic", "Dark/Mysterious",
    "Dreamy", "Nostalgic", "Triumphant", "Chill", "Intense",
    "Playful", "Peaceful", "Dramatic"
]

MUSIC_VOCALS = [
    "No Vocals (Instrumental)",
    "Male Vocals",
    "Female Vocals",
    "Mixed Vocals (Male & Female)",
    "Choir/Group Vocals",
    "Rap/Spoken Word",
    "Harmonized Vocals"
]

MUSIC_INSTRUMENTS = [
    "Guitar (Acoustic)", "Guitar (Electric)", "Piano", "Synthesizer",
    "Drums", "Bass", "Strings (Orchestra)", "Saxophone", "Trumpet",
    "Violin", "Flute", "Cello", "Harp", "Organ", "Banjo",
    "Ukulele", "Harmonica", "Accordion", "Tabla", "Sitar"
]

MUSIC_TEMPOS = {
    "Very Slow (Largo)": (40, 60),
    "Slow (Adagio)": (60, 80),
    "Moderate (Andante)": (80, 100),
    "Medium (Moderato)": (100, 120),
    "Fast (Allegro)": (120, 140),
    "Very Fast (Presto)": (140, 180),
    "Extremely Fast": (180, 220)
}

MUSIC_KEYS = [
    "C Major", "C Minor", "D Major", "D Minor", "E Major", "E Minor",
    "F Major", "F Minor", "G Major", "G Minor", "A Major", "A Minor",
    "B Major", "B Minor", "C# Major", "C# Minor", "F# Major", "F# Minor"
]

MUSIC_STRUCTURES = {
    "Simple": ["Intro", "Verse", "Chorus", "Outro"],
    "Standard": ["Intro", "Verse 1", "Chorus", "Verse 2", "Chorus", "Bridge", "Chorus", "Outro"],
    "Extended": ["Intro", "Verse 1", "Pre-Chorus", "Chorus", "Verse 2", "Pre-Chorus", "Chorus", "Bridge", "Final Chorus", "Outro"],
    "Custom": []  # User-defined
}

DEFAULT_MUSIC_PARAMS = {
    "genre": "Pop",
    "mood": "Happy/Upbeat",
    "vocals": "No Vocals (Instrumental)",
    "tempo_bpm": 120,
    "duration_seconds": 30,
    "key": "C Major",
    "structure": "Simple",
    "instruments": ["Piano", "Drums", "Bass"],
    "production_quality": "High",
    "seed": -1,
}

# ==================== MUSIC GENERATION PRESETS ====================
MUSIC_PRESETS = {
    "Epic Orchestral": {
        "genre": "Classical",
        "mood": "Epic/Cinematic",
        "vocals": "Choir/Group Vocals",
        "instruments": ["Strings (Orchestra)", "Trumpet", "Drums"],
        "tempo_bpm": 100,
        "key": "D Minor"
    },
    "Chill Lo-fi Study": {
        "genre": "Lo-fi",
        "mood": "Calm/Relaxing",
        "vocals": "No Vocals (Instrumental)",
        "instruments": ["Piano", "Bass", "Drums"],
        "tempo_bpm": 80,
        "key": "A Minor"
    },
    "Summer Pop Hit": {
        "genre": "Pop",
        "mood": "Happy/Upbeat",
        "vocals": "Female Vocals",
        "instruments": ["Guitar (Acoustic)", "Piano", "Drums"],
        "tempo_bpm": 125,
        "key": "G Major"
    },
    "Dark Trap Beat": {
        "genre": "Trap",
        "mood": "Dark/Mysterious",
        "vocals": "Rap/Spoken Word",
        "instruments": ["Synthesizer", "Bass", "Drums"],
        "tempo_bpm": 140,
        "key": "C Minor"
    },
    "Romantic Jazz": {
        "genre": "Jazz",
        "mood": "Romantic",
        "vocals": "No Vocals (Instrumental)",
        "instruments": ["Piano", "Saxophone", "Bass", "Drums"],
        "tempo_bpm": 90,
        "key": "F Major"
    },
    "EDM Festival Anthem": {
        "genre": "Electronic/EDM",
        "mood": "Energetic",
        "vocals": "No Vocals (Instrumental)",
        "instruments": ["Synthesizer", "Drums", "Bass"],
        "tempo_bpm": 128,
        "key": "A Minor"
    }
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
        "ACE Step: A high-energy J-pop track with female vocals about a summer adventure",
        "Qwen TTS: Welcome to the future of multi-modal artificial intelligence.",
        "ACE Step: Calm acoustic guitar melody with soft background humming",
        "Qwen TTS: The quick brown fox jumps over the lazy dog in a cheerful tone.",
        "ACE Step: Epic cinematic orchestral music with rhythmic chanting",
    ],
    "music": [
        "Upbeat summer pop song with catchy chorus and female vocals",
        "Dark atmospheric trap beat with heavy 808 bass",
        "Chill lo-fi hip hop beat perfect for studying",
        "Epic orchestral cinematic music for movie trailers",
        "Romantic jazz piano with soft saxophone accompaniment",
        "Energetic EDM festival anthem with synth drops",
    ],
}

NEGATIVE_PROMPT_TEMPLATES = {
    "image": "blurry, low quality, distorted, ugly, bad anatomy, worst quality, artifacts",
}
