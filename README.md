# Offline Multi-Modal AI Generator

A **production-grade, fully offline Python application** that generates images, audio, and video using powerful local Hugging Face models. Zero external dependencies after initial setup—no API calls, telemetry, or internet connectivity required during runtime.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

---

## ✨ Features

- ✅ **100% Offline After Setup** - No internet required for generation
- ✅ **Zero Telemetry** - No data collection, no tracking, fully private
- ✅ **No API Keys** - Runs completely locally, no account needed
- ✅ **5 Image Models** - From fast (4GB) to high-quality (16GB)
- ✅ **4 Audio Models** - Music generation and speech synthesis
- ✅ **3 Video Models** - Text-to-video and image-to-video
- ✅ **Automatic Optimization** - GPU/CPU detection with memory management
- ✅ **Production Quality** - Type hints, comprehensive error handling, extensive logging
- ✅ **Simple Installation** - One command setup with `pip install -r requirements.txt`

---

## 📋 System Requirements

### Minimum (CPU-only, slow)
- **CPU:** 4 cores
- **RAM:** 8GB (16GB recommended)
- **Storage:** 50GB for all models
- **Python:** 3.10+

### Recommended (GPU acceleration)
- **GPU:** NVIDIA RTX 3060 (12GB VRAM) or better
- **CPU:** 8+ cores
- **RAM:** 16GB+
- **Storage:** 100GB SSD
- **Python:** 3.11+

### Supported Hardware
- ✅ NVIDIA GPUs (CUDA enabled, RTX/GTX 1000+ series)
- ✅ Apple Silicon (M1/M2/M3 with Metal)
- ✅ CPU (all platforms, slower)
- ❌ AMD GPUs (limited support - use CPU)

---

## 🚀 Quick Start

### 1. Clone & Setup
```bash
cd MultiModelinator
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Application
```bash
python main.py
```

The interface will be available at: **http://127.0.0.1:7860**

---

## 📊 Model VRAM Guide

| Model | VRAM | Type | Speed | Quality | Recommended For |
|-------|------|------|-------|---------|-----------------|
| **SD 1.5** | 4GB | Image | ⚡⚡⚡ Very Fast | Good | Low-end GPUs, CPU |
| **SDXL 1.0** | 10GB | Image | ⚡⚡ Fast | Excellent | Mid-range GPUs |
| **SD 3 Medium** | 8GB | Image | ⚡⚡ Fast | Excellent | Standard setup |
| **FLUX.1-schnell** | 12GB | Image | ⚡⚡ Fast | Excellent | Balanced |
| **FLUX.1-dev** | 16GB | Image | ⚡ Slow | Best | High-end GPUs |
| **MusicGen Small** | 3GB | Audio | ⚡⚡⚡ Very Fast | Good | Music generation |
| **MusicGen Medium** | 6GB | Audio | ⚡⚡ Fast | Excellent | Music generation |
| **Bark Small** | 3GB | Audio | ⚡⚡⚡ Very Fast | Good | Speech synthesis |
| **Bark** | 5GB | Audio | ⚡⚡ Fast | Excellent | Speech synthesis |
| **ZeroScope V2 XL** | 10GB | Video | ⚡ Slow | Good | Text-to-video |
| **Text-to-Video MS** | 12GB | Video | 🐢 Very Slow | Good | Text-to-video |
| **Stable Video SVD** | 16GB | Video | 🐢 Very Slow | Excellent | Image-to-video |

### Hardware-Model Matching

**For 4GB VRAM:**
- Only SD 1.5 recommended
- Use CPU fallback for others

**For 8GB VRAM:**
- SDXL 1.0, SD 3, smaller audio models
- Not recommended for video

**For 12GB VRAM (RTX 3060):**
- All SD/SDXL models
- FLUX.1-schnell
- Most audio models
- Light video generation

**For 16GB+ VRAM:**
- All models supported
- Batch generation possible

---

## 📖 Usage Guide

### Image Generation

#### Text-to-Image (txt2img)
1. Select **🖼️ Image** mode
2. Choose model based on your VRAM
3. Enter prompt: *"A serene mountain landscape at sunrise..."*
4. Adjust:
   - **Steps:** 20 (standard) to 50 (high quality)
   - **Guidance:** 7.5 (balanced) to 15 (more prompt-following)
   - **Size:** 512x512 (fast) to 1024x1024 (detailed)
5. Click **Generate Image**

#### Image-to-Image (img2img)
1. Upload input image in "Input Image" field
2. Strength slider controls transformation:
   - 0.0 = Keep original image
   - 0.5 = Balanced modification
   - 1.0 = Fully regenerate from image
3. Lower steps for faster modification

### Audio Generation

1. Select **🎵 Audio** mode
2. Choose between **MusicGen** (music) or **Bark** (speech)
3. Enter prompt: *"Epic orchestral music with dramatic strings..."*
4. Adjust:
   - **Duration:** 10-30 seconds
   - **Temperature:** 0.1 (deterministic) to 2.0 (creative)
5. Click **Generate Audio**

### Video Generation

1. Select **🎬 Video** mode
2. For **img2vid:** Upload start frame (required)
3. For **txt2vid:** Just text prompt
4. Adjust:
   - **Frames:** 8-24 (more = longer, slower)
   - **FPS:** 8 (standard) to 30 (smooth)
5. Click **Generate Video**

---

## 🔧 Advanced Configuration

Edit `config.py` to customize:

```python
# Enable/disable optimizations
DEVICE_CONFIG = {
    "use_fp16": True,                    # Float16 for speedup
    "enable_attention_slicing": True,    # Memory optimization
    "enable_model_cpu_offload": False,   # For very low VRAM
    "use_torch_compile": False,          # Python 3.11+ only
}

# Change UI theme
GRADIO_THEME_CONFIG = {
    "primary_hue": "red",       # Accent color
    "secondary_hue": "slate",
    "neutral_hue": "slate",
}

# Add custom models to registries
IMAGE_MODELS["Custom Model"] = {
    "repo_id": "user/custom-model",
    "vram_estimate": 8,
    "recommended_steps": 20,
}
```

---

## 🛠️ Troubleshooting

### **CUDA Out of Memory (OOM)**
```
❌ GPU ran out of memory
```
**Solution:**
- Reduce resolution: 512x512 instead of 1024x1024
- Lower inference steps: 10 instead of 20
- Use smaller model: SD 1.5 instead of SDXL
- Enable model CPU offload in `config.py`

### **Models Not Downloading**
```
RuntimeError: Model loading failed
```
**Solution:**
- Check internet connection
- Increase timeout: `INFERENCE_TIMEOUT_SECONDS = 900` in `config.py`
- Manual download: `huggingface-cli download <repo_id>`
- Check disk space: needs 5-20GB per model

### **Slow Generation on CPU**
**Solution:**
- Expected: 2-10 minutes for CPU
- Use GPU if available
- Reduce resolution and steps
- Close other applications

### **Gradio Port Already in Use**
```
Address already in use
```
**Solution:**
Change port in `main.py`:
```python
demo.launch(server_port=7861)  # Use different port
```

### **Python Version Issues**
```
SyntaxError: walrus operator
```
**Solution:**
- Requires Python 3.10+
- Check: `python --version`
- Update Python if needed

---

## 📁 Project Structure

```
multi-modal-ai-generator/
├── main.py                          # Entry point, Gradio UI
├── config.py                        # Model registry & settings
├── requirements.txt                 # Dependencies
├── README.md                        # Documentation
├── generator.log                    # Runtime logs
│
├── generators/
│   ├── __init__.py
│   ├── base.py                      # Abstract base class
│   ├── image_generator.py           # Image generation
│   ├── audio_generator.py           # Audio generation
│   └── video_generator.py           # Video generation
│
├── utils/
│   ├── __init__.py
│   ├── device_manager.py            # GPU/CPU optimization
│   ├── model_cache.py               # Pipeline caching
│   ├── error_handler.py             # Error handling & logging
│   └── validators.py                # Input validation
│
├── tests/
│   └── test_generators.py           # Unit tests
│
└── assets/
    └── examples/                    # Example prompts
```

---

## 🧪 Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_generators.py::TestImageGenerator -v

# Coverage report
pytest tests/ --cov=. --cov-report=html
```

---

## 🚀 Performance Tips

### Inference Speed

| Setting | Effect | Impact |
|---------|--------|--------|
| ↓ Steps | 10→5 | 2x faster, lower quality |
| ↓ Resolution | 1024→512 | 4x faster, less detail |
| FP16 enabled | On GPU | 20-30% speedup |
| Attention slicing | Enabled | Slower but lower VRAM |
| Compile UNet | Python 3.11+ | 10-20% speedup |

### Memory Optimization

```python
# In config.py for very low VRAM
DEVICE_CONFIG = {
    "enable_attention_slicing": True,    # 30% VRAM saving
    "enable_vae_slicing": True,
    "enable_vae_tiling": True,
    "enable_model_cpu_offload": True,    # 50% VRAM but slower
}
```

### Batch Generation

```python
# Generate multiple images efficiently
for i in range(5):
    image, status = generator.generate(
        prompt=prompts[i],
        seed=-1
    )
```

---

## 🔒 Security & Privacy

- ✅ **No External Calls:** All computation local
- ✅ **No Data Collection:** Logs saved locally only
- ✅ **No Telemetry:** Gradio analytics disabled
- ✅ **Input Validation:** All inputs sanitized
- ✅ **Safe File Handling:** Temporary files auto-cleaned

### Network Isolation Verification
```bash
# Test offline operation
# 1. Disconnect from internet
# 2. Run: python main.py
# 3. Generate content - should work fine
```

---

## 📚 Example Prompts

### Image Prompts
- "A futuristic cyberpunk city with neon signs and flying cars, ultra detailed, 4K"
- "Oil painting of a serene Japanese garden with koi pond at sunset"
- "Underwater scene with colorful coral reef and tropical fish, cinematic lighting"

### Audio Prompts
- "Epic orchestral music with dramatic strings, french horns, and timpani drums"
- "Lo-fi hip hop beats with chill vibes and vinyl crackle"
- "Natural sounds: rain on leaves with distant thunderstorm"

### Video Prompts
- "Abstract particles swirling and morphing into geometric shapes"
- "Person walking through misty forest with dappled sunlight"
- "Ocean waves crashing on beach with sunset, slow motion"

---

## 🔌 Extending with New Models

### Add Custom Image Model

Edit `config.py`:
```python
IMAGE_MODELS["Custom Model"] = {
    "repo_id": "user/custom-model",
    "pipeline_class": "StableDiffusionPipeline",
    "vram_estimate": 8,
    "recommended_steps": 20,
    "default_guidance": 7.5,
    "min_steps": 1,
    "max_steps": 100,
}
```

### Create Custom Generator

```python
# In generators/custom_generator.py
from generators.base import BaseGenerator

class CustomGenerator(BaseGenerator):
    def generate(self, **kwargs):
        # Your custom implementation
        pass
```

---

## 📊 Logging & Debugging

All operations logged to `generator.log`:

```
2026-01-24 10:30:15 - utils.device_manager - INFO - Device: NVIDIA RTX 3060
2026-01-24 10:30:16 - generators.image_generator - INFO - Generating image...
2026-01-24 10:30:42 - generators.image_generator - INFO - Image generation successful: (1024, 1024)
```

Enable debug mode in `utils/error_handler.py`:
```python
logger.setLevel(logging.DEBUG)  # More detailed output
```

---

## 🤝 Contributing

To add features or improve the codebase:

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Make changes with tests
4. Run: `pytest tests/` to verify
5. Commit: `git commit -m "Add new feature"`
6. Push & create pull request

---

## ⚖️ License

MIT License - Free for personal and commercial use

---

## 📞 Support

### Common Issues

**Q: How do I use this completely offline?**  
A: Download all models on first run (with internet), then disconnect. App works perfectly offline after that.

**Q: Can I use multiple GPUs?**  
A: Currently optimized for single GPU. Multi-GPU support in roadmap.

**Q: How do I delete cached models?**  
A: Models stored in `~/.cache/huggingface/`. Delete folder to reclaim space.

**Q: Can I customize the UI colors?**  
A: Yes! Edit `GRADIO_THEME_CONFIG` in `config.py`.

### Documentation Links
- [Diffusers](https://huggingface.co/docs/diffusers)
- [Transformers](https://huggingface.co/docs/transformers)
- [Gradio](https://www.gradio.app/)

---

## 🎯 Roadmap

- [ ] Multi-GPU support for batch operations
- [ ] Web UI deployment options
- [ ] Model quantization for faster inference
- [ ] Custom LoRA model support
- [ ] Video upscaling and enhancement
- [ ] Real-time streaming generation
- [ ] REST API interface
- [ ] Model fine-tuning tools

---

## 📝 Version History

**v1.0.0** (2026-01-24)
- Initial release
- 5 image, 4 audio, 3 video models
- Full offline support
- Production-ready code

---

**Last Updated:** 2026-01-24  
**Status:** Production Ready ✅  
**Built with:** PyTorch • Diffusers • Gradio • Transformers

