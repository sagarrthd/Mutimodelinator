"""
Enhanced Offline Multi-Modal AI Generator
Features: Modern UI, Smart Model Management, Output History, Performance Optimization
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import gradio as gr
import torch

from config import AUDIO_MODELS, IMAGE_MODELS
from utils.device_manager import DeviceManager
from utils.error_handler import GenerationError
from utils.model_manager import get_model_manager

# Import our custom utilities
from utils.output_manager import get_output_manager
from utils.ui_theme import create_custom_theme, get_custom_css

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize managers
output_manager = get_output_manager()
model_manager = get_model_manager()
device_manager = DeviceManager()

# ==================== GENERATION FUNCTIONS ====================

def generate_image(
    prompt: str,
    model_name: str,
    steps: int,
    guidance: float,
    height: int = 768,
    width: int = 768,
    seed: Optional[int] = None
) -> Tuple[Optional[Any], str]:
    """
    Generate image from text prompt with enhanced error handling and caching.
    
    Args:
        prompt: Text description of image
        model_name: Selected model name
        steps: Number of inference steps
        guidance: Guidance scale
        height: Image height
        width: Image width
        seed: Optional random seed
        
    Returns:
        Tuple of (image, status_message)
    """
    try:
        if not prompt or not prompt.strip():
            return None, "❌ Error: Please enter a prompt"
        
        logger.info(f"🎨 Generating image: {prompt[:50]}...")
        
        # Get model config
        model_config = IMAGE_MODELS.get(model_name)
        if not model_config:
            return None, f"❌ Error: Model '{model_name}' not found"
        
        # Load model
        from diffusers import StableDiffusionPipeline
        
        model_key = f"image_{model_name}"
        
        # Check if already loaded
        if model_manager.is_model_loaded(model_key):
            logger.info(f"✓ Using cached model: {model_name}")
            pipe = model_manager.get_loaded_model(model_key)
        else:
            logger.info(f"Loading image model: {model_name}")
            repo_id = model_config["repo_id"]
            
            # Select pipeline class
            pipeline_class = model_config.get("pipeline_class", "StableDiffusionPipeline")
            
            # Load pipeline
            pipe = StableDiffusionPipeline.from_pretrained(
                repo_id,
                torch_dtype=torch.float16 if device_manager.device == "cuda" else torch.float32,
                safety_checker=None,
                use_safetensors=True,
            )
            
            # Move to device
            pipe = pipe.to(device_manager.device)
            
            # Enable optimizations
            model_manager.enable_memory_optimizations(pipe)
            
            # Register model
            model_manager.register_model(model_key, pipe, model_config)
        
        # Generate
        logger.info("Generating image...")
        with torch.no_grad():
            with torch.cuda.amp.autocast(enabled=device_manager.device == "cuda"):
                result = pipe(
                    prompt=prompt,
                    negative_prompt="blurry, low quality, distorted, ugly, bad",
                    num_inference_steps=steps,
                    guidance_scale=guidance,
                    height=height,
                    width=width,
                    generator=torch.Generator(device=device_manager.device).manual_seed(seed) if seed else None,
                ).images[0]
        
        # Save output
        output_path = output_manager.save_image(
            result,
            prompt=prompt,
            model=model_name,
            seed=seed,
            metadata={
                "steps": steps,
                "guidance": guidance,
                "height": height,
                "width": width,
            }
        )
        
        logger.info("✓ Image generated successfully!")
        return result, f"✓ Image generated successfully!\n📁 Saved to: {output_path}"
        
    except GenerationError as e:
        logger.error(f"Generation error: {e}")
        return None, f"❌ Error: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return None, f"❌ Unexpected error: {str(e)}"


def generate_audio(
    prompt: str,
    model_name: str,
    duration: int = 10
) -> Tuple[Optional[str], str]:
    """
    Generate audio from text prompt.
    
    Args:
        prompt: Text description
        model_name: Selected model name
        duration: Duration in seconds
        
    Returns:
        Tuple of (audio_path, status_message)
    """
    try:
        if not prompt or not prompt.strip():
            return None, "❌ Error: Please enter a prompt"
        
        logger.info(f"🎵 Generating audio: {prompt[:50]}...")
        
        # Get model config
        model_config = AUDIO_MODELS.get(model_name)
        if not model_config:
            return None, f"❌ Error: Model '{model_name}' not found"
        
        model_key = f"audio_{model_name}"
        
        if model_config.get("task") == "text-to-speech":
            # Use Bark
            from transformers import AutoProcessor, BarkModel
            
            if model_manager.is_model_loaded(model_key):
                processor, model = model_manager.get_loaded_model(model_key)
            else:
                repo_id = model_config["repo_id"]
                processor = AutoProcessor.from_pretrained(repo_id)
                model = BarkModel.from_pretrained(repo_id)
                model = model.to(device_manager.device)
                
                model_manager.enable_memory_optimizations(model)
                model_manager.register_model(model_key, (processor, model), model_config)
            
            inputs = processor(prompt, return_tensors="pt")
            inputs = {k: v.to(device_manager.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                audio_values = model.generate(**inputs, do_sample=True)
            
            sample_rate = model.generation_config.sample_rate
            audio_array = audio_values.cpu().numpy()[0]
            
        else:
            # Use MusicGen
            from transformers import AutoProcessor, MusicgenForConditionalGeneration
            
            if model_manager.is_model_loaded(model_key):
                processor, model = model_manager.get_loaded_model(model_key)
            else:
                repo_id = model_config["repo_id"]
                processor = AutoProcessor.from_pretrained(repo_id)
                model = MusicgenForConditionalGeneration.from_pretrained(repo_id)
                model = model.to(device_manager.device)
                
                model_manager.enable_memory_optimizations(model)
                model_manager.register_model(model_key, (processor, model), model_config)
            
            inputs = processor(text=[prompt], padding=True, return_tensors="pt")
            inputs = {k: v.to(device_manager.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                audio_values = model.generate(**inputs, max_new_tokens=int(duration * 50))
            
            sample_rate = model.config.sample_rate
            audio_array = audio_values.cpu().numpy()[0]
        
        # Save audio
        import tempfile

        import scipy.io.wavfile as wavfile
        
        # Create temp file first
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            temp_path = tmp.name
        
        wavfile.write(temp_path, sample_rate, audio_array)
        
        # Save to output manager
        output_path = output_manager.save_audio(
            temp_path,
            prompt=prompt,
            model=model_name,
            duration=duration
        )
        
        # Clean up temp
        Path(temp_path).unlink(missing_ok=True)
        
        logger.info("✓ Audio generated successfully!")
        return output_path, f"✓ Audio generated successfully!\n📁 Saved to: {output_path}"
        
    except Exception as e:
        logger.error(f"Error generating audio: {e}", exc_info=True)
        return None, f"❌ Error: {str(e)}"


def get_generation_history() -> Dict[str, Any]:
    """Get generation history and statistics."""
    stats = output_manager.get_stats()
    return stats


def get_gallery_items():
    """Get recent generated images for gallery."""
    return output_manager.get_gallery_items(limit=20)


def clear_all_history() -> str:
    """Clear all generation history."""
    try:
        count = output_manager.clear_history()
        return f"✓ Cleared {count} entries from history"
    except Exception as e:
        return f"❌ Error: {str(e)}"


def get_model_stats() -> Dict[str, Any]:
    """Get model management statistics."""
    return model_manager.get_memory_stats()


def clear_model_cache() -> str:
    """Clear model cache and free memory."""
    try:
        model_manager.unload_all_models()
        model_manager.clear_cache()
        return "✓ Model cache cleared and memory freed"
    except Exception as e:
        return f"❌ Error: {str(e)}"


# ==================== GRADIO INTERFACE ====================

def build_ui() -> gr.Blocks:
    """Build enhanced Gradio interface with modern styling."""
    
    theme = create_custom_theme()
    css = get_custom_css()
    
    with gr.Blocks(
        title="🎨 MultiModelinator - Offline AI Generator",
        theme=theme,
        css=css
    ) as demo:
        
        # ==================== HEADER ====================
        gr.Markdown("""
        # 🎨 MultiModelinator
        ## Offline Multi-Modal AI Generator
        
        Generate **images**, **audio**, and **videos** without internet - fully local! 
        All models run on your device with optimized performance.
        """)
        
        with gr.Row():
            with gr.Column(scale=3):
                gr.Markdown("""
                **🚀 Quick Start:**
                1. Select your preferred model
                2. Enter a creative prompt
                3. Adjust parameters as needed
                4. Click Generate
                5. Your creation is automatically saved!
                """)
            
            with gr.Column(scale=1):
                with gr.Group():
                    gr.Markdown("### ⚙️ System Status")
                    device_info = gr.Textbox(
                        label="Device",
                        value=f"{device_manager.device.upper()} - {device_manager.get_device_info()}",
                        interactive=False
                    )
                    memory_btn = gr.Button("🔄 Refresh Stats", size="sm")
        
        # ==================== MAIN TABS ====================
        with gr.Tabs():
            
            # ==================== IMAGE GENERATION TAB ====================
            with gr.Tab("🖼️ Image Generation", id="image_tab"):
                with gr.Row():
                    with gr.Column(scale=1, min_width=400):
                        gr.Markdown("### 📝 Configuration")
                        
                        img_prompt = gr.Textbox(
                            label="✨ Prompt",
                            placeholder="Describe the image you want to create...\nBe creative and specific!",
                            lines=4,
                            max_lines=8,
                            info="The more detailed, the better!"
                        )
                        
                        with gr.Row():
                            img_model = gr.Dropdown(
                                choices=list(IMAGE_MODELS.keys()),
                                value=list(IMAGE_MODELS.keys())[3],  # SDXL
                                label="🤖 Model",
                                info="Choose based on VRAM availability"
                            )
                            img_seed = gr.Number(
                                label="🌱 Seed",
                                value=-1,
                                precision=0,
                                info="Use -1 for random"
                            )
                        
                        with gr.Row():
                            img_steps = gr.Slider(
                                minimum=1,
                                maximum=100,
                                value=30,
                                step=1,
                                label="📊 Steps",
                                info="More steps = better quality but slower"
                            )
                            img_guidance = gr.Slider(
                                minimum=1,
                                maximum=20,
                                value=7.5,
                                step=0.5,
                                label="🎯 Guidance",
                                info="How closely to follow prompt"
                            )
                        
                        with gr.Row():
                            img_height = gr.Number(
                                value=768,
                                label="📏 Height",
                                precision=0,
                                minimum=256,
                                maximum=2048,
                                step=64
                            )
                            img_width = gr.Number(
                                value=768,
                                label="📏 Width",
                                precision=0,
                                minimum=256,
                                maximum=2048,
                                step=64
                            )
                        
                        img_generate_btn = gr.Button(
                            "✨ Generate Image",
                            scale=2,
                            variant="primary",
                            size="lg"
                        )
                    
                    with gr.Column(scale=1, min_width=300):
                        gr.Markdown("### 🎨 Output")
                        img_output = gr.Image(
                            label="Generated Image",
                            type="pil",
                            show_download_button=True
                        )
                        img_status = gr.Textbox(
                            label="Status",
                            interactive=False,
                            lines=3
                        )
                
                # Handle image generation
                img_generate_btn.click(
                    fn=generate_image,
                    inputs=[
                        img_prompt,
                        img_model,
                        img_steps,
                        img_guidance,
                        img_height,
                        img_width,
                        img_seed
                    ],
                    outputs=[img_output, img_status]
                )
            
            # ==================== AUDIO GENERATION TAB ====================
            with gr.Tab("🎵 Audio Generation", id="audio_tab"):
                with gr.Row():
                    with gr.Column(scale=1, min_width=400):
                        gr.Markdown("### 📝 Configuration")
                        
                        audio_prompt = gr.Textbox(
                            label="✨ Prompt",
                            placeholder="Describe the sound or music you want...",
                            lines=4,
                            info="Be specific about style, instruments, mood, etc."
                        )
                        
                        audio_model = gr.Dropdown(
                            choices=list(AUDIO_MODELS.keys()),
                            value=list(AUDIO_MODELS.keys())[1],  # MusicGen Small
                            label="🤖 Model",
                            info="MusicGen for music, Bark for speech"
                        )
                        
                        audio_duration = gr.Slider(
                            minimum=5,
                            maximum=30,
                            value=10,
                            step=1,
                            label="⏱️ Duration (seconds)"
                        )
                        
                        audio_generate_btn = gr.Button(
                            "🎵 Generate Audio",
                            scale=2,
                            variant="primary",
                            size="lg"
                        )
                    
                    with gr.Column(scale=1, min_width=300):
                        gr.Markdown("### 🎙️ Output")
                        audio_output = gr.Audio(
                            label="Generated Audio",
                            type="filepath",
                            show_download_button=True
                        )
                        audio_status = gr.Textbox(
                            label="Status",
                            interactive=False,
                            lines=3
                        )
                
                # Handle audio generation
                audio_generate_btn.click(
                    fn=generate_audio,
                    inputs=[audio_prompt, audio_model, audio_duration],
                    outputs=[audio_output, audio_status]
                )
            
            # ==================== HISTORY & GALLERY TAB ====================
            with gr.Tab("📚 Generation History", id="history_tab"):
                gr.Markdown("### 🖼️ Recent Generations")
                
                gallery = gr.Gallery(
                    label="Generated Images",
                    show_label=True,
                    columns=4,
                    rows=2,
                    object_fit="scale-down"
                )
                
                with gr.Row():
                    refresh_gallery_btn = gr.Button("🔄 Refresh Gallery", size="sm")
                    clear_history_btn = gr.Button("🗑️ Clear History", size="sm", variant="stop")
                
                gr.Markdown("### 📊 Statistics")
                stats_display = gr.Textbox(
                    label="Generation Statistics",
                    interactive=False,
                    lines=6
                )
                
                def update_gallery():
                    items = get_gallery_items()
                    return items
                
                def display_stats():
                    stats = get_generation_history()
                    text = f"""
                    📊 Generation Statistics:
                    • Total Generations: {stats['total_generations']}
                    • Images: {stats['images']}
                    • Audio Files: {stats['audio']}
                    • Videos: {stats['videos']}
                    • Total Size: {stats['total_size_mb']} MB
                    • Output Directory: {stats['output_dir']}
                    """
                    return text
                
                refresh_gallery_btn.click(
                    fn=update_gallery,
                    outputs=gallery
                )
                
                gallery.load(fn=update_gallery, outputs=gallery)
                stats_display.value = display_stats()
                
                clear_history_btn.click(
                    fn=clear_all_history,
                    outputs=gr.Textbox(label="Result")
                )
            
            # ==================== SETTINGS TAB ====================
            with gr.Tab("⚙️ System Settings", id="settings_tab"):
                gr.Markdown("### 🔧 Resource Management")
                
                with gr.Row():
                    with gr.Column():
                        model_stats = gr.Textbox(
                            label="Model Cache Status",
                            interactive=False,
                            lines=5
                        )
                        refresh_model_stats = gr.Button("🔄 Refresh Stats", size="sm")
                        clear_cache_btn = gr.Button("🗑️ Clear Model Cache", size="sm", variant="stop")
                    
                    with gr.Column():
                        gr.Markdown("""
                        ### 💡 Tips
                        - **Clear Cache** when switching between large models
                        - Use **xformers** for 20-30% memory savings
                        - **Seed = -1** for random results
                        - Enable **AMP** for faster generation
                        """)
                
                def get_model_status():
                    stats = get_model_stats()
                    text = f"""
                    Device: {stats['device'].upper()}
                    Loaded Models: {stats['loaded_models']}
                    Model Keys: {', '.join(stats['model_keys']) if stats['model_keys'] else 'None'}
                    
                    Memory Info:
                    """
                    if 'cuda_memory_allocated' in stats:
                        text += f"\n    VRAM Allocated: {stats['cuda_memory_allocated']}\n    VRAM Cached: {stats['cuda_memory_cached']}"
                    return text
                
                refresh_model_stats.click(
                    fn=get_model_status,
                    outputs=model_stats
                )
                
                clear_cache_btn.click(
                    fn=clear_model_cache,
                    outputs=gr.Textbox(label="Result")
                )
                
                model_stats.value = get_model_status()
    
    return demo


# ==================== MAIN ====================

if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("🚀 MultiModelinator - Offline AI Generator (Enhanced)")
    logger.info("=" * 70)
    logger.info(f"Device: {device_manager.device.upper()}")
    logger.info("Build UI...")
    
    demo = build_ui()
    
    logger.info("=" * 70)
    logger.info("🌐 Launching Gradio server...")
    logger.info("📱 Open browser to: http://127.0.0.1:7860")
    logger.info("⌨️ Press Ctrl+C to stop")
    logger.info("=" * 70)
    
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True,
        show_api=False,
    )
