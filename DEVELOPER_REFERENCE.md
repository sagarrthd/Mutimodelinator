# 🔖 Developer Quick Reference - MultiModelinator Enhanced

## Quick Links
- **Main App**: `main_enhanced.py` (630 lines)
- **Output Manager**: `utils/output_manager.py` (240 lines)
- **Model Manager**: `utils/model_manager.py` (300 lines)
- **UI Theme**: `utils/ui_theme.py` (380 lines)
- **Device Manager**: `utils/device_manager.py` (enhanced)

---

## 1️⃣ Using Output Manager

```python
from utils.output_manager import get_output_manager

# Get instance
manager = get_output_manager()

# Save image
output_manager.save_image(
    image=pil_image,
    prompt="beautiful sunset",
    model="SDXL 1.0",
    seed=42,
    metadata={"steps": 30, "guidance": 7.5}
)

# Get history
history = output_manager.get_history('image', limit=10)
# Returns: List[Dict] with all metadata

# Get stats
stats = output_manager.get_stats()
# Returns: {'total_generations': 5, 'images': 3, ...}

# Get gallery items for Gradio
items = output_manager.get_gallery_items(limit=20)
# Returns: [(image_path, caption), ...]

# Clear history
output_manager.clear_history('audio')
```

---

## 2️⃣ Using Model Manager

```python
from utils.model_manager import get_model_manager

# Get instance
manager = get_model_manager()

# Check if model loaded
if manager.is_model_loaded("image_sdxl"):
    pipe = manager.get_loaded_model("image_sdxl")
else:
    # Load from HuggingFace
    pipe = StableDiffusionXLPipeline.from_pretrained(repo_id)
    pipe = pipe.to(device)
    
    # Optimize
    manager.enable_memory_optimizations(pipe)
    
    # Register
    manager.register_model("image_sdxl", pipe, config)

# Use @track_model_load decorator
@track_model_load("image_sdxl", metadata=config)
def load_model():
    return StableDiffusionXLPipeline.from_pretrained(repo_id)

# Memory stats
stats = manager.get_memory_stats()
# Returns: {
#   'device': 'cuda',
#   'loaded_models': 1,
#   'model_keys': ['image_sdxl'],
#   'cuda_memory_allocated': '7.2GB',
#   'cuda_memory_cached': '8.0GB'
# }

# Clear cache
manager.clear_cache()
manager.unload_all_models()
```

---

## 3️⃣ Using UI Theme

```python
from utils.ui_theme import create_custom_theme, get_custom_css
import gradio as gr

# Create themed app
theme = create_custom_theme()
css = get_custom_css()

with gr.Blocks(theme=theme, css=css) as demo:
    # Your components here
    pass

demo.launch()
```

---

## 4️⃣ Generation Pipeline

```python
def generate_image(prompt, model_name, steps, guidance):
    try:
        # 1. Validate
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        # 2. Get config
        config = IMAGE_MODELS.get(model_name)
        if not config:
            raise ValueError(f"Model {model_name} not found")
        
        # 3. Load with caching
        model_key = f"image_{model_name}"
        if not model_manager.is_model_loaded(model_key):
            pipe = StableDiffusionXLPipeline.from_pretrained(
                config["repo_id"],
                torch_dtype=torch.float16,
                safety_checker=None,
            )
            pipe = pipe.to(device)
            model_manager.enable_memory_optimizations(pipe)
            model_manager.register_model(model_key, pipe, config)
        else:
            pipe = model_manager.get_loaded_model(model_key)
        
        # 4. Generate
        with torch.no_grad():
            with torch.cuda.amp.autocast():
                image = pipe(
                    prompt=prompt,
                    num_inference_steps=steps,
                    guidance_scale=guidance,
                ).images[0]
        
        # 5. Save
        path = output_manager.save_image(image, prompt, model_name)
        
        # 6. Return
        return image, f"✓ Saved to {path}"
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return None, f"❌ {str(e)}"
```

---

## 5️⃣ Common Patterns

### Pattern 1: Load Model with Caching
```python
def load_model_cached(model_key, load_fn, config):
    """Generic pattern for cached model loading"""
    if manager.is_model_loaded(model_key):
        return manager.get_loaded_model(model_key)
    else:
        model = load_fn()
        model.to(device)
        manager.enable_memory_optimizations(model)
        manager.register_model(model_key, model, config)
        return model
```

### Pattern 2: Save Output with Metadata
```python
def save_with_metadata(content, content_type, prompt, model, params):
    """Generic pattern for saving with metadata"""
    if content_type == "image":
        return output_manager.save_image(content, prompt, model, 
                                        metadata=params)
    elif content_type == "audio":
        return output_manager.save_audio(content, prompt, model,
                                        metadata=params)
```

### Pattern 3: Error Handling
```python
def generate_safe(fn, *args, **kwargs):
    """Safe generation with error handling"""
    try:
        result = fn(*args, **kwargs)
        return result, "✓ Success"
    except GenerationError as e:
        logger.error(str(e))
        return None, f"❌ {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected: {e}", exc_info=True)
        return None, f"❌ Unexpected error: {str(e)}"
```

---

## 6️⃣ Configuration Reference

### Add New Image Model
**File:** `config.py`

```python
IMAGE_MODELS = {
    "New Model": {
        "repo_id": "org/model",
        "pipeline_class": "StableDiffusionPipeline",
        "vram_estimate": 10,
        "recommended_steps": 25,
        "default_guidance": 7.5,
        "min_steps": 1,
        "max_steps": 100,
    },
}
```

### Add New Audio Model
**File:** `config.py`

```python
AUDIO_MODELS = {
    "New Audio": {
        "repo_id": "org/model",
        "task": "text-to-audio",  # or "text-to-speech"
        "vram_estimate": 5,
        "max_duration": 30,
        "sample_rate": 16000,
    },
}
```

---

## 7️⃣ UI Component Reference

### Text Input
```python
prompt_input = gr.Textbox(
    label="✨ Prompt",
    placeholder="Describe what you want...",
    lines=4,
    max_lines=8,
    info="Be specific and creative"
)
```

### Slider
```python
steps_slider = gr.Slider(
    minimum=1,
    maximum=100,
    value=30,
    step=1,
    label="📊 Steps",
    info="More = better quality but slower"
)
```

### Dropdown
```python
model_dropdown = gr.Dropdown(
    choices=list(IMAGE_MODELS.keys()),
    value=list(IMAGE_MODELS.keys())[0],
    label="🤖 Model",
    info="Choose based on VRAM"
)
```

### Image Output
```python
image_output = gr.Image(
    label="Generated Image",
    type="pil",
    show_download_button=True
)
```

### Button Click Handler
```python
button.click(
    fn=generate_image,
    inputs=[prompt, model, steps, guidance],
    outputs=[image_output, status_output]
)
```

---

## 8️⃣ Debug & Monitor

### Check Memory
```python
from utils.model_manager import get_model_manager

manager = get_model_manager()
stats = manager.get_memory_stats()
print(f"Loaded: {stats['loaded_models']} models")
print(f"Memory: {stats.get('cuda_memory_allocated', 'N/A')}")
```

### Check Outputs
```python
from utils.output_manager import get_output_manager

manager = get_output_manager()
stats = manager.get_stats()
print(f"Total: {stats['total_generations']} generations")
print(f"Size: {stats['total_size_mb']} MB")
```

### Check Logs
```bash
# Run with debug logging
export LOG_LEVEL=DEBUG
python main_enhanced.py

# Or in code
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 9️⃣ Performance Tuning

### For Low VRAM (< 4GB)
```python
# Use smaller model
model = "SD 1.5"  # 4GB

# Use smaller resolution
height, width = 512, 512  # Instead of 768

# Use fewer steps
steps = 15  # Instead of 30

# Enable all optimizations
model_manager.enable_xformers(pipe)
pipe.enable_attention_slicing()
pipe.enable_vae_tiling()
```

### For High VRAM (> 24GB)
```python
# Use larger model
model = "FLUX.1-dev"  # 16GB

# Use higher resolution
height, width = 1024, 1024

# Use more steps for quality
steps = 50

# Still enable for consistency
model_manager.enable_memory_optimizations(pipe)
```

---

## 🔟 Testing Checklist

```python
# Test 1: Output Manager
from utils.output_manager import get_output_manager
mgr = get_output_manager()
assert mgr.get_stats()['total_generations'] >= 0

# Test 2: Model Manager
from utils.model_manager import get_model_manager
mgr = get_model_manager()
assert mgr.get_memory_stats()['device'] in ['cuda', 'cpu', 'mps']

# Test 3: Device Manager
from utils.device_manager import DeviceManager
dm = DeviceManager()
assert dm.device in ['cuda', 'cpu', 'mps']

# Test 4: Theme
from utils.ui_theme import create_custom_theme, get_custom_css
theme = create_custom_theme()
css = get_custom_css()
assert 'glassmorphism' in css.lower() or 'glass' in css.lower()
```

---

## 📋 Common Tasks

### Task: Add Progress Callback
```python
def on_step(step, timestep, latents):
    print(f"Step {step}")

# With diffusers
pipe.unet.register_forward_pre_hook(on_step)
```

### Task: Custom Seed
```python
seed = 42
generator = torch.Generator(device=device).manual_seed(seed)

image = pipe(
    prompt=prompt,
    generator=generator,  # Use this
).images[0]
```

### Task: Get Model Size
```python
import torch
total = 0
for param in model.parameters():
    total += param.numel()

size_gb = total * 4 / (1024**3)  # 4 bytes per float32
print(f"Model size: {size_gb:.1f}GB")
```

### Task: Profile Generation Speed
```python
import time

start = time.time()
image = pipe(prompt=prompt)
elapsed = time.time() - start

print(f"Generation took {elapsed:.1f}s")
```

---

## 🚨 Error Codes

| Error | Cause | Solution |
|-------|-------|----------|
| `CUDA out of memory` | Model too large | Clear cache, use smaller model |
| `Model not found` | Wrong repo_id | Check config.py, verify model exists |
| `Permission denied` | Output dir | Check outputs/ has write permissions |
| `ImportError: xformers` | Not installed | `pip install xformers` (optional) |
| `No GPU detected` | Device issue | Check CUDA, nvidia-smi |

---

## 🎓 Resources

- HuggingFace Docs: https://huggingface.co/docs
- Diffusers: https://huggingface.co/docs/diffusers
- PyTorch: https://pytorch.org/docs
- Gradio: https://www.gradio.app/docs
- xformers: https://github.com/facebookresearch/xformers

---

## 💡 Pro Tips

1. **Use `@track_model_load` decorator** for automatic caching
2. **Check memory before loading** large models
3. **Always use `torch.no_grad()`** in inference
4. **Enable AMP for 15-20% speedup** on CUDA
5. **Clear cache** when switching between very different models
6. **Log important steps** for debugging
7. **Use context managers** for resource cleanup
8. **Profile before optimizing** to find actual bottleneck

---

## 📞 Quick Help

**Q: How do I add a new model?**
A: Edit `config.py`, add entry to `IMAGE_MODELS` or `AUDIO_MODELS`

**Q: How do I get generation history?**
A: `output_manager.get_history('image', limit=10)`

**Q: How do I clear memory?**
A: `model_manager.clear_cache()` or `unload_all_models()`

**Q: How do I check VRAM usage?**
A: `manager.get_memory_stats()`

**Q: Where are outputs saved?**
A: `./outputs/{images,audio,videos}` with metadata in `history.json`

---

**Version:** 2.0 Enhanced | **Last Updated:** January 25, 2026
