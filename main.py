"""
Production-grade Offline Multi-Modal AI Generator
Main entry point with Gradio interface for image and audio generation
"""

import logging
import time
import os
import datetime
from typing import Optional, Tuple, List
from pathlib import Path

import gradio as gr
import torch
import numpy as np
import scipy.io.wavfile
from PIL import Image

import config
from utils import (
    setup_logging,
    get_device_manager,
    handle_generation_error,
    log_performance_metrics,
)
from generators import ImageGenerator, AudioGenerator, MusicStudioGenerator

# ==================== SETUP ====================
logger = setup_logging(log_file=config.LOG_FILE)
device_manager = get_device_manager()

# Store generator instances
current_generators = {"image": None, "audio": None, "music_studio": None}

# Output directory
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def save_generated_file(
    file_data, file_type: str, extension: str, metadata: dict = None
) -> str:
    """Save generated content to persistent storage."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # Use part of seed if available, else random
    unique_id = str(get_random_seed())[:8]
    filename = f"{file_type}_{timestamp}_{unique_id}.{extension}"
    filepath = os.path.join(OUTPUT_DIR, filename)

    try:
        if file_type == "image":
            # file_data is PIL Image
            file_data.save(filepath)
        elif file_type in ("audio", "music"):
            # file_data is (sample_rate, audio_array)
            sample_rate, audio_array = file_data
            scipy.io.wavfile.write(filepath, sample_rate, audio_array)

        logger.info(f"Saved {file_type} to {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Failed to save file: {e}")
        return None


def get_gallery_files() -> List[str]:
    """Get list of files in output directory sorted by creation time."""
    files = []
    if not os.path.exists(OUTPUT_DIR):
        return []

    for f in os.listdir(OUTPUT_DIR):
        # Only show images in the gallery component
        if f.lower().endswith((".png", ".jpg", ".jpeg")):
            files.append(os.path.join(OUTPUT_DIR, f))

    # Sort by modification time (newest first)
    files.sort(key=os.path.getmtime, reverse=True)
    return files


logger.info("=" * 60)
logger.info("Offline Multi-Modal AI Generator Started")
logger.info(f"Device: {device_manager.device_name}")
logger.info(f"VRAM Available: {device_manager.vram_available:.2f}GB")
logger.info("=" * 60)


# ==================== GENERATION FUNCTIONS ====================


def generate_image(
    model_name: str,
    prompt: str,
    negative_prompt: str,
    steps: int,
    guidance: float,
    width: int,
    height: int,
    seed: int,
    input_image: Optional[Image.Image] = None,
    img2img_strength: float = 0.75,
    progress: gr.Progress = gr.Progress(),
) -> Tuple[Optional[Image.Image], str]:
    """Generate image from prompt."""
    try:
        progress(0.1, desc="Loading model...")

        # Load model configuration
        if model_name not in config.IMAGE_MODELS:
            return None, f"❌ Model not found: {model_name}"

        model_config = config.IMAGE_MODELS[model_name]

        # Create generator
        generator = ImageGenerator(model_config)
        current_generators["image"] = generator

        progress(0.3, desc="Initializing model...")
        generator.load_model()

        progress(0.5, desc="Generating image...")

        # Generate
        image, status = generator.generate(
            prompt=prompt,
            negative_prompt=negative_prompt,
            steps=steps,
            guidance_scale=guidance,
            width=width,
            height=height,
            seed=seed,
            img2img_image=input_image,
            img2img_strength=img2img_strength,
        )

        if image:
            saved_path = save_generated_file(image, "image", "png")
            if saved_path:
                status += f"\nSaved to: {os.path.basename(saved_path)}"

        progress(1.0, desc="Complete!")
        return image, status

    except Exception as e:
        logger.exception("Image generation error")
        return handle_generation_error(e, logger)


def generate_audio(
    model_name: str,
    prompt: str,
    duration: float,
    temperature: float,
    seed: int,
    progress: gr.Progress = gr.Progress(),
) -> Tuple[Optional[Tuple], str]:
    """Generate audio from prompt."""
    try:
        progress(0.1, desc="Loading model...")

        if model_name not in config.AUDIO_MODELS:
            return None, f"❌ Model not found: {model_name}"

        model_config = config.AUDIO_MODELS[model_name]

        # Create generator
        generator = AudioGenerator(model_config)
        current_generators["audio"] = generator

        progress(0.3, desc="Initializing model...")
        generator.load_model()

        progress(0.5, desc="Generating audio...")

        # Generate
        audio_data, status = generator.generate(
            prompt=prompt,
            duration_seconds=duration,
            temperature=temperature,
            seed=seed,
        )

        if audio_data:
            saved_path = save_generated_file(audio_data, "audio", "wav")
            if saved_path:
                status += f"\nSaved to: {os.path.basename(saved_path)}"

        progress(1.0, desc="Complete!")
        return audio_data, status

    except Exception as e:
        logger.exception("Audio generation error")
        return handle_generation_error(e, logger)



def generate_music_studio(
    model_name: str,
    prompt: str,
    preset: str,
    genre: str,
    mood: str,
    vocals: str,
    tempo_bpm: int,
    duration: float,
    key: str,
    instruments: List[str],
    lyrics: str,
    seed: int,
    progress: gr.Progress = gr.Progress(),
) -> Tuple[Optional[Tuple], str]:
    """Generate professional music with advanced controls."""
    try:
        progress(0.1, desc="Loading music model...")

        if model_name not in config.MUSIC_STUDIO_MODELS:
            return None, f"❌ Model not found: {model_name}"

        model_config = config.MUSIC_STUDIO_MODELS[model_name]

        # Create generator
        generator = MusicStudioGenerator(model_config)
        current_generators["music_studio"] = generator

        progress(0.3, desc="Initializing model...")
        generator.load_model()

        # Apply preset if selected
        if preset and preset != "Custom":
            preset_config = config.MUSIC_PRESETS.get(preset, {})
            genre = preset_config.get("genre", genre)
            mood = preset_config.get("mood", mood)
            vocals = preset_config.get("vocals", vocals)
            tempo_bpm = preset_config.get("tempo_bpm", tempo_bpm)
            key = preset_config.get("key", key)
            instruments = preset_config.get("instruments", instruments)

        progress(0.5, desc="Generating music...")

        # Generate music with full control
        audio_data, status = generator.generate_music(
            prompt=prompt if prompt else "",
            genre=genre,
            mood=mood,
            vocals=vocals,
            tempo_bpm=tempo_bpm,
            duration_seconds=duration,
            key=key,
            instruments=instruments,
            lyrics=lyrics if lyrics else "",
            seed=seed,
        )

        if audio_data:
            saved_path = save_generated_file(audio_data, "music", "wav")
            if saved_path:
                status += f"\nSaved to: {os.path.basename(saved_path)}"

        progress(1.0, desc="Complete!")
        return audio_data, status

    except Exception as e:
        logger.exception("Music generation error")
        return handle_generation_error(e, logger)



def toggle_interfaces(mode: str):
    """Toggle visibility of interface sections based on selected mode."""
    return (
        gr.update(visible=(mode == "🖼️ Image")),
        gr.update(visible=(mode == "🎵 Audio")),
        gr.update(visible=(mode == "🎸 Music Studio")),
        gr.update(visible=(mode == "📂 Gallery")),
    )


def get_random_seed() -> int:
    """Generate random seed."""
    import random

    return random.randint(0, 2**32 - 1)


# ==================== GRADIO INTERFACE ====================


def build_ui():
    """Build the Gradio interface."""

    theme = gr.themes.Base(
        primary_hue="red",
        secondary_hue="slate",
        neutral_hue="slate",
    ).set(
        body_background_fill="*neutral_950",
        block_background_fill="*neutral_900",
        button_primary_background_fill="*primary_600",
    )

    css = """
    @media (max-width: 768px) {
        .gradio-container { padding: 10px !important; }
    }
    """

    with gr.Blocks(theme=theme, title="Offline AI Generator", css=css) as demo:
        # Header
        gr.Markdown(
            """
            # 🎨 Local Multi-Modal AI Generator
            **Fully offline • No telemetry • No API calls • No account needed**
            
            Generate images and audio using powerful open-source models running locally on your machine.
            """
        )

        # Mode selector
        with gr.Row():
            mode_selector = gr.Radio(
                ["🖼️ Image", "🎵 Audio", "🎸 Music Studio", "📂 Gallery"],
                value="🖼️ Image",
                label="Generation Mode",
                scale=1,
            )

        with gr.Row():
            gr.Markdown(
                f"""
                **Device Status:** {device_manager.device_name}  
                **VRAM:** {device_manager.vram_available:.2f}GB available
                """
            )

        # ==================== IMAGE GENERATION ====================
        with gr.Column(visible=True) as image_interface:
            gr.Markdown("### 🖼️ Image Generation")

            with gr.Row():
                with gr.Column(scale=1):
                    image_model = gr.Dropdown(
                        choices=list(config.IMAGE_MODELS.keys()),
                        value=list(config.IMAGE_MODELS.keys())[0],
                        label="Model",
                        info="Choose based on your VRAM. Lower VRAM = faster but lower quality.",
                    )

            with gr.Row():
                image_prompt = gr.Textbox(
                    lines=3,
                    placeholder="A serene mountain landscape with snow-capped peaks at sunrise...",
                    label="Positive Prompt",
                    info="Describe what you want to generate",
                )

            with gr.Row():
                image_negative = gr.Textbox(
                    lines=2,
                    placeholder="blurry, low quality, distorted, ugly, artifacts",
                    label="Negative Prompt",
                    value=config.NEGATIVE_PROMPT_TEMPLATES["image"],
                    info="Describe what to avoid",
                )

            with gr.Row():
                image_input = gr.Image(
                    type="pil",
                    label="Input Image (optional - for img2img mode)",
                    scale=1,
                )

            with gr.Row():
                image_width = gr.Slider(
                    256, 2048, value=1024, step=64, label="Width (pixels)"
                )
                image_height = gr.Slider(
                    256, 2048, value=1024, step=64, label="Height (pixels)"
                )

            with gr.Row():
                image_steps = gr.Slider(
                    1, 100, value=20, step=1, label="Steps (more = better but slower)"
                )
                image_guidance = gr.Slider(
                    1.0, 20.0, value=7.5, step=0.5, label="Guidance Scale"
                )

            with gr.Row():
                image_strength = gr.Slider(
                    0.0,
                    1.0,
                    value=0.75,
                    step=0.05,
                    label="Img2Img Strength (only if image uploaded)",
                )
                image_seed = gr.Number(
                    value=-1, label="Seed (-1 = random)", precision=0
                )
                image_random_btn = gr.Button("🎲 Random Seed", scale=0)

            with gr.Row():
                image_generate_btn = gr.Button("Generate Image", variant="primary")

            image_output = gr.Image(label="Generated Image", scale=1)
            image_status = gr.Textbox(label="Status", interactive=False, lines=4)

            # Example prompts for images
            gr.Examples(
                examples=config.EXAMPLE_PROMPTS["image"],
                inputs=image_prompt,
                label="Example Prompts",
            )

        # ==================== AUDIO GENERATION ====================
        with gr.Column(visible=False) as audio_interface:
            gr.Markdown("### 🎵 Audio Generation")

            with gr.Row():
                audio_model = gr.Dropdown(
                    choices=list(config.AUDIO_MODELS.keys()),
                    value=list(config.AUDIO_MODELS.keys())[0],
                    label="Model",
                    info="Music generation or speech synthesis",
                )

            with gr.Row():
                audio_prompt = gr.Textbox(
                    lines=2,
                    placeholder="Epic orchestral music with dramatic strings and powerful drums...",
                    label="Prompt",
                    info="Describe the audio to generate",
                )

            with gr.Row():
                audio_duration = gr.Slider(
                    1, 30, value=10, step=1, label="Duration (seconds)"
                )
                audio_temperature = gr.Slider(
                    0.1, 2.0, value=1.0, step=0.1, label="Temperature"
                )
                audio_seed = gr.Number(value=-1, label="Seed (-1 = random)", precision=0)

            with gr.Row():
                audio_generate_btn = gr.Button("Generate Audio", variant="primary")

            audio_output = gr.Audio(label="Generated Audio", type="numpy")
            audio_status = gr.Textbox(label="Status", interactive=False, lines=4)

            # Example prompts for audio
            gr.Examples(
                examples=config.EXAMPLE_PROMPTS["audio"],
                inputs=audio_prompt,
                label="Example Prompts",
            )

        # ==================== MUSIC STUDIO (SUNO-LIKE) ====================
        with gr.Column(visible=False) as music_studio_interface:
            gr.Markdown("### 🎸 Music Studio - Professional Music Generation")
            gr.Markdown("*Create studio-quality music with full creative control*")
            
            with gr.Row():
                music_model = gr.Dropdown(
                    choices=list(config.MUSIC_STUDIO_MODELS.keys()),
                    value=list(config.MUSIC_STUDIO_MODELS.keys())[0] if config.MUSIC_STUDIO_MODELS else None,
                    label="AI Model",
                    info="HeartMuLa for vocals/lyrics, Stable Audio for fast generation",
                )
            
            with gr.Row():
                music_preset = gr.Dropdown(
                    choices=["Custom"] + list(config.MUSIC_PRESETS.keys()),
                    value="Custom",
                    label="🎯 Quick Preset",
                    info="Select a preset or use Custom for manual control",
                )
            
            with gr.Row():
                music_prompt = gr.Textbox(
                    lines=2,
                    placeholder="Describe your music (optional - will auto-generate from settings)...",
                    label="Custom Prompt (Optional)",
                    info="Leave empty to auto-generate from genre/mood settings",
                )
            
            with gr.Row():
                with gr.Column():
                    music_genre = gr.Dropdown(
                        choices=config.MUSIC_GENRES,
                        value="Pop",
                        label="🎵 Genre",
                    )
                    music_mood = gr.Dropdown(
                        choices=config.MUSIC_MOODS,
                        value="Happy/Upbeat",
                        label="💫 Mood",
                    )
                with gr.Column():
                    music_vocals = gr.Dropdown(
                        choices=config.MUSIC_VOCALS,
                        value="No Vocals (Instrumental)",
                        label="🎤 Vocals",
                    )
                    music_key = gr.Dropdown(
                        choices=config.MUSIC_KEYS,
                        value="C Major",
                        label="🎹 Musical Key",
                    )
            
            with gr.Row():
                music_tempo = gr.Slider(
                    40, 220, value=120, step=1,
                    label="🥁 Tempo (BPM)",
                )
                music_duration = gr.Slider(
                    10, 120, value=30, step=5,
                    label="⏱️ Duration (seconds)",
                )
            
            with gr.Row():
                music_instruments = gr.CheckboxGroup(
                    choices=config.MUSIC_INSTRUMENTS,
                    value=["Piano", "Drums", "Bass"],
                    label="🎸 Instruments",
                )
            
            with gr.Accordion("📝 Lyrics (Optional)", open=False):
                music_lyrics = gr.Textbox(
                    lines=4,
                    placeholder="Enter custom lyrics here (only works with HeartMuLa model)...",
                    label="Custom Lyrics",
                )
            
            with gr.Row():
                music_seed = gr.Number(value=-1, label="Seed (-1 = random)", precision=0)
                music_random_btn = gr.Button("🎲 Random Seed", scale=0)
            
            with gr.Row():
                music_generate_btn = gr.Button("🎵 Generate Music", variant="primary", size="lg")
            
            music_output = gr.Audio(label="Generated Music", type="numpy")
            music_status = gr.Textbox(label="Status", interactive=False, lines=6)
            
            # Example prompts for music
            gr.Examples(
                examples=config.EXAMPLE_PROMPTS.get("music", []),
                inputs=music_prompt,
                label="Example Prompts",
            )

        # ==================== GALLERY ====================
        with gr.Column(visible=False) as gallery_interface:
            gr.Markdown("### 📂 Gallery")

            with gr.Row():
                refresh_btn = gr.Button("🔄 Refresh Gallery")

            gallery = gr.Gallery(
                label="Generated Content",
                show_label=False,
                elem_id="gallery",
                columns=[3],
                rows=[2],
                object_fit="contain",
                height="auto",
            )

            refresh_btn.click(fn=get_gallery_files, inputs=None, outputs=gallery)
            # Load gallery on start
            demo.load(fn=get_gallery_files, inputs=None, outputs=gallery)

        # ==================== EVENT HANDLERS ====================

        mode_selector.change(
            fn=toggle_interfaces,
            inputs=[mode_selector],
            outputs=[
                image_interface,
                audio_interface,
                music_studio_interface,
                gallery_interface,
            ],
        )

        # Image generation
        image_random_btn.click(fn=get_random_seed, outputs=image_seed)
        image_generate_btn.click(
            fn=generate_image,
            inputs=[
                image_model,
                image_prompt,
                image_negative,
                image_steps,
                image_guidance,
                image_width,
                image_height,
                image_seed,
                image_input,
                image_strength,
            ],
            outputs=[image_output, image_status],
        )

        # Audio generation
        audio_generate_btn.click(
            fn=generate_audio,
            inputs=[
                audio_model,
                audio_prompt,
                audio_duration,
                audio_temperature,
                audio_seed,
            ],
            outputs=[audio_output, audio_status],
        )

        # Music Studio generation
        music_random_btn.click(fn=get_random_seed, outputs=music_seed)
        music_generate_btn.click(
            fn=generate_music_studio,
            inputs=[
                music_model,
                music_prompt,
                music_preset,
                music_genre,
                music_mood,
                music_vocals,
                music_tempo,
                music_duration,
                music_key,
                music_instruments,
                music_lyrics,
                music_seed,
            ],
            outputs=[music_output, music_status],
        )

    return demo


# ==================== LAUNCH ====================
if __name__ == "__main__":
    logger.info("Building interface...")
    demo = build_ui()

    logger.info("Launching Gradio server...")
    logger.info("Open browser to: http://127.0.0.1:7860")
    logger.info("Press Ctrl+C to stop")

    # Auth config
    auth = None
    if os.environ.get("GRADIO_USERNAME") and os.environ.get("GRADIO_PASSWORD"):
        auth = (os.environ.get("GRADIO_USERNAME"), os.environ.get("GRADIO_PASSWORD"))
        logger.info("Basic authentication enabled")

    share = os.environ.get("GRADIO_SHARE", "False").lower() == "true"
    if share:
        logger.info("Sharing enabled")

    demo.launch(
        server_name=os.environ.get("GRADIO_SERVER_NAME", "127.0.0.1"),
        server_port=int(os.environ.get("GRADIO_SERVER_PORT", "7860")),
        share=share,
        auth=auth,
        enable_queue=True,
        analytics_enabled=False,  # Disable telemetry
    )
