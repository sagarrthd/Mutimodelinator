# 🚀 QUICK START REFERENCE

## Installation (5 minutes)

```bash
cd MultiModelinator
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Open browser: **http://127.0.0.1:7860**

---

## File Structure Overview

```
MultiModelinator/
├── main.py                 ← RUN THIS (Gradio interface)
├── config.py              ← All models & settings
├── setup.py               ← Download models interactively
├── requirements.txt       ← pip install this
├── README.md              ← User documentation
│
├── generators/            ← Generation logic
│   ├── base.py           ← Abstract base class
│   ├── image_generator.py ← Image generation (txt2img, img2img)
│   ├── audio_generator.py ← Audio generation (music, speech)
│   └── video_generator.py ← Video generation (txt2vid, img2vid)
│
├── utils/                 ← Support modules
│   ├── device_manager.py  ← GPU/CPU optimization
│   ├── model_cache.py     ← Model loading & caching
│   ├── error_handler.py   ← Error handling & logging
│   └── validators.py      ← Input validation
│
├── tests/                 ← Unit tests
│   └── test_generators.py ← Test suite
│
└── assets/examples/       ← Example prompts
    └── prompts.py
```

---

## Model Selection by VRAM

| VRAM | Best Models | Notes |
|------|------------|-------|
| 4GB | SD 1.5 (image), Bark Small (audio) | Very basic, CPU mostly |
| 8GB | SDXL, SD3, MusicGen Small | Good for single mode |
| 12GB | FLUX.1-schnell, all audio, light video | Recommended minimum |
| 16GB+ | FLUX.1-dev, all models, batch ops | No limitations |

---

## How to Use Each Mode

### 🖼️ Image Generation
1. Select "Image" mode
2. Enter prompt: *"A futuristic cyberpunk city..."*
3. Adjust: Steps (10-50), Guidance (1-20), Size (256-2048)
4. Generate!

### 🎵 Audio Generation
1. Select "Audio" mode
2. Choose model: MusicGen (music) or Bark (speech)
3. Enter prompt: *"Epic orchestral music..."*
4. Set duration (1-30 seconds)
5. Generate!

### 🎬 Video Generation
1. Select "Video" mode
2. Enter prompt or upload image (for img2vid)
3. Set frames (8-48) and FPS (4-30)
4. Generate!

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Out of Memory** | Reduce resolution, lower steps, use smaller model |
| **Models won't download** | Check internet, run `python setup.py` |
| **Slow generation** | Expected on CPU (2-10min). Use GPU if available |
| **Port in use** | Change port in main.py line 400 |

---

## Key Files to Edit

### Add Custom Model
**Edit: `config.py`**
```python
IMAGE_MODELS["My Model"] = {
    "repo_id": "user/model-name",
    "vram_estimate": 8,
    "recommended_steps": 20,
}
```

### Change UI Theme
**Edit: `config.py`**
```python
GRADIO_THEME_CONFIG = {
    "primary_hue": "red",    # Change to "blue", "green", etc.
}
```

### Enable Optimizations
**Edit: `config.py`**
```python
DEVICE_CONFIG = {
    "use_fp16": True,              # Speedup
    "enable_torch_compile": True,  # Python 3.11+ only
}
```

---

## Command Reference

```bash
# Run app
python main.py

# Download models interactively
python setup.py

# Run tests
pytest tests/ -v

# Check device
python -c "import torch; print(f'GPU: {torch.cuda.is_available()}')"

# View logs
tail -f generator.log
```

---

## Features at a Glance

| Feature | Support |
|---------|---------|
| **Image Models** | 5 (SD 1.5, SDXL, SD3, FLUX schnell/dev) |
| **Audio Models** | 4 (MusicGen, Bark variations) |
| **Video Models** | 3 (SVD, Text-to-Video MS, ZeroScope) |
| **GPU Support** | NVIDIA CUDA, Apple Metal, CPU |
| **Offline** | ✅ Yes (after initial download) |
| **Telemetry** | ✅ None (fully private) |
| **Web UI** | ✅ Gradio (local only) |
| **Batch Gen** | ✅ Image & Audio |

---

## Example Prompts

**Image:** "A serene mountain landscape with snow-capped peaks at sunrise, golden light, photorealistic, national geographic style"

**Audio:** "Epic orchestral music with dramatic strings, french horns, and powerful drums, cinematic"

**Video:** "Abstract particles flowing and morphing into geometric shapes, smooth motion, vibrant colors"

---

## Documentation Files

- **README.md** - Complete user guide (15+ pages)
- **IMPLEMENTATION_GUIDE.md** - Technical reference (12+ pages)
- **PROJECT_MANIFEST.md** - Project inventory & specs
- **generator.log** - Runtime logs (auto-created)

---

## Performance Tips

1. **Faster Generation:** Lower steps (10 vs 20), smaller resolution (512 vs 1024)
2. **Better Quality:** More steps (50), larger resolution, higher guidance (15)
3. **Lower VRAM:** Disable attention slicing, enable CPU offload in config
4. **Batch Mode:** Generate multiple prompts at once to be efficient

---

## Common Commands

```python
# Python: Create generator manually
from generators import ImageGenerator
from config import IMAGE_MODELS

config = IMAGE_MODELS["FLUX.1-schnell (Fast, 12GB VRAM)"]
gen = ImageGenerator(config)
gen.load_model()
image, status = gen.generate(
    prompt="A beautiful landscape",
    steps=4,
    seed=-1
)
```

---

## Offline Mode

App works completely offline after:
1. `pip install -r requirements.txt`
2. First run downloads models (needs internet)
3. Then works 100% offline - no internet needed!

Verify: Disconnect internet, run `python main.py` ✓

---

## Status Check

```bash
# What Python version?
python --version  # Need 3.10+

# GPU available?
python -c "import torch; print(f'GPU: {torch.cuda.is_available()}')"

# How much VRAM?
python -c "import torch; print(f'VRAM: {torch.cuda.mem_get_info()[1]/(1024**3):.1f}GB')"
```

---

## Getting Help

1. **Check logs:** `cat generator.log`
2. **Read README:** Full troubleshooting guide included
3. **See examples:** Visit http://127.0.0.1:7860 and look at "Example Prompts"
4. **Test code:** Run `pytest tests/` to verify installation

---

## What's Included

✅ Production-ready code (3200+ lines)  
✅ 12 AI models ready to use  
✅ Offline operation (zero API calls)  
✅ Complete documentation  
✅ Unit tests included  
✅ Security & privacy built-in  
✅ Error handling & logging  
✅ Type hints throughout  

---

**Version:** 1.0.0 | **Status:** Production Ready ✅  
**Last Updated:** 2026-01-24 | **Ready to Deploy:** YES ✅
