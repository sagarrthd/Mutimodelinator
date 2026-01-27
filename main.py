"""
Production-grade Offline Multi-Modal AI Generator
Main entry point with Gradio interface for image, audio, and video generation
"""

import logging
import time
import os
import shutil
import tempfile
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
from generators import ImageGenerator, AudioGenerator, VideoGenerator

# ==================== SETUP ====================
logger = setup_logging(log_file=config.LOG_FILE)
device_manager = get_device_manager()

# Store generator instances
current_generators = {"image": None, "audio": None, "video": None}

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
        elif file_type == "audio":
            # file_data is (sample_rate, audio_array)
            sample_rate, audio_array = file_data
            scipy.io.wavfile.write(filepath, sample_rate, audio_array)
        elif file_type == "video":
            # file_data is path to temp file
            shutil.copy2(file_data, filepath)

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


def generate_video(
    model_name: str,
    prompt: str,
    frames: int,
    fps: int,
    input_image: Optional[Image.Image] = None,
    motion_bucket_id: int = 127,
    seed: int = -1,
    progress: gr.Progress = gr.Progress(),
) -> Tuple[Optional[list], str]:
    """Generate video from prompt or image."""
    try:
        progress(0.1, desc="Loading model...")

        if model_name not in config.VIDEO_MODELS:
            return None, f"❌ Model not found: {model_name}"

        model_config = config.VIDEO_MODELS[model_name]

        # Create generator
        generator = VideoGenerator(model_config)
        current_generators["video"] = generator

        progress(0.3, desc="Initializing model...")
        generator.load_model()

        progress(0.5, desc="Generating video...")

        # Generate
        frames_list, status = generator.generate(
            prompt=prompt,
            num_frames=frames,
            fps=fps,
            conditioning_image=input_image,
            motion_bucket_id=motion_bucket_id,
            seed=seed,
        )

        if frames_list:
            progress(0.9, desc="Saving video...")
            # Create temporary video file
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
                success, save_status = generator.frames_to_video_file(
                    frames_list, tmp.name, fps=fps
                )
                if success:
                    status += f"\n{save_status}"

                    # Save to persistent storage
                    saved_path = save_generated_file(tmp.name, "video", "mp4")
                    if saved_path:
                        status += f"\nSaved to: {os.path.basename(saved_path)}"

                    # Return video path for Gradio Video widget
                    return tmp.name, status
                else:
                    return None, f"❌ {save_status}"

        progress(1.0, desc="Complete!")
        return None, status

    except Exception as e:
        logger.exception("Video generation error")
        return handle_generation_error(e, logger)


def toggle_interfaces(mode: str):
    """Toggle visibility of interface sections based on selected mode."""
    image_visible = mode == "🖼️ Image"
    audio_visible = mode == "🎵 Audio"
    video_visible = mode == "🎬 Video"
    gallery_visible = mode == "📂 Gallery"

    return (
        gr.update(visible=image_visible),
        gr.update(visible=audio_visible),
        gr.update(visible=video_visible),
        gr.update(visible=gallery_visible),
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
            
            Generate images, audio, and video using powerful open-source models running locally on your machine.
            """
        )

        # Mode selector
        with gr.Row():
            mode_selector = gr.Radio(
                ["🖼️ Image", "🎵 Audio", "🎬 Video", "📂 Gallery"],
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

        # ==================== VIDEO GENERATION ====================
        with gr.Column(visible=False) as video_interface:
            gr.Markdown("### 🎬 Video Generation")

            with gr.Row():
                video_model = gr.Dropdown(
                    choices=list(config.VIDEO_MODELS.keys()),
                    value=list(config.VIDEO_MODELS.keys())[0],
                    label="Model",
                    info="Generate video from text or animate an image",
                )

            with gr.Row():
                video_prompt = gr.Textbox(
                    lines=3,
                    placeholder="A rotating golden sphere with reflective surface on dark background...",
                    label="Prompt",
                    info="Describe the video scene",
                )

            with gr.Row():
                video_input = gr.Image(
                    type="pil",
                    label="Input Image (required for img2vid, optional for txt2vid)",
                    scale=1,
                )

            with gr.Row():
                video_frames = gr.Slider(8, 48, value=16, step=1, label="Frames")
                video_fps = gr.Slider(4, 30, value=8, step=1, label="FPS")

            with gr.Row():
                video_motion = gr.Slider(
                    1, 255, value=127, step=1, label="Motion Bucket ID (img2vid only)"
                )
                video_seed = gr.Number(
                    value=-1, label="Seed (-1 = random)", precision=0
                )

            with gr.Row():
                video_generate_btn = gr.Button("Generate Video", variant="primary")

            video_output = gr.Video(label="Generated Video")
            video_status = gr.Textbox(label="Status", interactive=False, lines=4)

            # Example prompts for video
            gr.Examples(
                examples=config.EXAMPLE_PROMPTS["video"],
                inputs=video_prompt,
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

        # Mode toggle
        mode_selector.change(
            fn=toggle_interfaces,
            inputs=[mode_selector],
            outputs=[
                image_interface,
                audio_interface,
                video_interface,
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

        # Video generation
        video_generate_btn.click(
            fn=generate_video,
            inputs=[
                video_model,
                video_prompt,
                video_frames,
                video_fps,
                video_input,
                video_motion,
                video_seed,
            ],
            outputs=[video_output, video_status],
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
    )
