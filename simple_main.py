"""
Simplified Offline Multi-Modal AI Generator
Minimal dependencies version for immediate testing
"""

import logging
import torch
import gradio as gr

# ==================== SETUP LOGGING ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== DEVICE DETECTION ====================
def get_device():
    """Detect available device (CUDA, CPU, or MPS)"""
    if torch.cuda.is_available():
        device = "cuda"
        vram = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        logger.info(f"✓ CUDA device detected with {vram:.2f}GB VRAM")
    elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        device = "mps"
        logger.info("✓ Apple Metal Performance Shaders (MPS) detected")
    else:
        device = "cpu"
        logger.info("⚠ Using CPU (slow generation - consider GPU)")
    return device

device = get_device()

# ==================== GENERATION FUNCTIONS ====================
def generate_image(prompt: str, model: str, steps: int, guidance: float):
    """Generate image from prompt"""
    try:
        from diffusers import StableDiffusionPipeline
        
        logger.info(f"Loading image model: {model}")
        
        if "FLUX" in model:
            repo = "black-forest-labs/FLUX.1-schnell"
        elif "SD3" in model:
            repo = "stabilityai/stable-diffusion-3-medium-diffusers"
        elif "SDXL" in model:
            repo = "stabilityai/stable-diffusion-xl-base-1.0"
        else:
            repo = "runwayml/stable-diffusion-v1-5"
        
        pipe = StableDiffusionPipeline.from_pretrained(
            repo,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            safety_checker=None,
        )
        pipe = pipe.to(device)
        
        logger.info(f"Generating image: {prompt}")
        
        image = pipe(
            prompt=prompt,
            negative_prompt="blurry, low quality, distorted",
            num_inference_steps=steps,
            guidance_scale=guidance,
            height=768,
            width=768,
        ).images[0]
        
        output_path = "/tmp/generated_image.png"
        image.save(output_path)
        logger.info(f"✓ Image saved to {output_path}")
        
        return image, "✓ Image generated successfully!"
        
    except Exception as e:
        logger.error(f"Error generating image: {str(e)}")
        return None, f"❌ Error: {str(e)}"

def generate_audio(prompt: str, model: str, duration: int):
    """Generate audio from prompt"""
    try:
        from transformers import AutoProcessor, MusicgenForConditionalGeneration
        
        logger.info(f"Loading audio model: {model}")
        
        if "Small" in model:
            repo = "facebook/musicgen-small"
        else:
            repo = "facebook/musicgen-medium"
        
        processor = AutoProcessor.from_pretrained(repo)
        model_obj = MusicgenForConditionalGeneration.from_pretrained(repo)
        model_obj = model_obj.to(device)
        
        logger.info(f"Generating audio: {prompt}")
        
        inputs = processor(text=[prompt], padding=True, return_tensors="pt")
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        audio_values = model_obj.generate(**inputs, max_new_tokens=duration * 50)
        
        output_path = "/tmp/generated_audio.wav"
        import scipy.io.wavfile as wavfile
        wavfile.write(output_path, 16000, audio_values[0].cpu().numpy())
        logger.info(f"✓ Audio saved to {output_path}")
        
        return output_path, "✓ Audio generated successfully!"
        
    except Exception as e:
        logger.error(f"Error generating audio: {str(e)}")
        return None, f"❌ Error: {str(e)}"

def generate_video(prompt: str, model: str, frames: int):
    """Generate video from prompt"""
    return None, "⚠ Video generation requires additional setup. Image/Audio working!"

# ==================== GRADIO INTERFACE ====================
def build_ui():
    """Build Gradio interface"""
    with gr.Blocks(title="Offline AI Generator", theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        # 🎨 Offline Multi-Modal AI Generator
        Generate **images**, **audio**, and **videos** without internet - fully local!
        """)
        
        with gr.Tabs():
            # IMAGE TAB
            with gr.Tab("🖼️ Image Generation"):
                with gr.Row():
                    with gr.Column():
                        img_prompt = gr.Textbox(
                            label="Prompt",
                            placeholder="Describe the image you want to generate...",
                            lines=3
                        )
                        img_model = gr.Dropdown(
                            ["FLUX.1-schnell", "SDXL 1.0", "SD 1.5"],
                            value="SD 1.5",
                            label="Model"
                        )
                        img_steps = gr.Slider(1, 50, value=20, label="Steps")
                        img_guidance = gr.Slider(1, 20, value=7.5, label="Guidance Scale")
                        img_button = gr.Button("Generate Image", scale=2, variant="primary")
                    
                    with gr.Column():
                        img_output = gr.Image(label="Generated Image")
                        img_status = gr.Textbox(label="Status", interactive=False)
                
                img_button.click(
                    fn=generate_image,
                    inputs=[img_prompt, img_model, img_steps, img_guidance],
                    outputs=[img_output, img_status]
                )
            
            # AUDIO TAB
            with gr.Tab("🎵 Audio Generation"):
                with gr.Row():
                    with gr.Column():
                        audio_prompt = gr.Textbox(
                            label="Prompt",
                            placeholder="Describe the audio you want...",
                            lines=3
                        )
                        audio_model = gr.Dropdown(
                            ["MusicGen Medium", "MusicGen Small"],
                            value="MusicGen Small",
                            label="Model"
                        )
                        audio_duration = gr.Slider(5, 30, value=10, label="Duration (seconds)")
                        audio_button = gr.Button("Generate Audio", scale=2, variant="primary")
                    
                    with gr.Column():
                        audio_output = gr.Audio(label="Generated Audio")
                        audio_status = gr.Textbox(label="Status", interactive=False)
                
                audio_button.click(
                    fn=generate_audio,
                    inputs=[audio_prompt, audio_model, audio_duration],
                    outputs=[audio_output, audio_status]
                )
            
            # VIDEO TAB
            with gr.Tab("🎬 Video Generation"):
                gr.Markdown("""
                ### Video Generation (Coming Soon)
                Video models require special setup. Image and Audio generation are ready!
                """)
    
    return demo

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Building interface...")
    demo = build_ui()
    
    logger.info("=" * 60)
    logger.info("Launching Gradio server...")
    logger.info("Open browser to: http://127.0.0.1:7860")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 60)
    
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
    )
