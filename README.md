# Offline Multi-Modal AI Generator (MultiModelinator)

A **production-grade, fully offline Python application** that generates images, audio, and video using powerful local Hugging Face models. Zero external dependencies after initial setup—no API calls, telemetry, or internet connectivity required during runtime.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

> **Topics:** offline-ai, stable-diffusion, multimodal, gradio, huggingface, local-ai

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
- ✅ **Simple Installation** - pip installable or run from source

---

## 📸 Screenshots

![Gradio UI](https://via.placeholder.com/800x400?text=Gradio+UI+Screenshot+Placeholder)

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
git clone https://github.com/sagarrthd/Mutimodelinator.git
cd Mutimodelinator
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

### 3. Download Models
```bash
python scripts/download_models.py
```

### 4. Run Application
```bash
python main.py
```

The interface will be available at: **http://127.0.0.1:7860**

---

## 📖 Documentation

Detailed documentation has been moved to the `docs/` directory:

- [Quick Start](docs/QUICK_START.md)
- [Technical Architecture](docs/TECHNICAL_ARCHITECTURE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Developer Reference](docs/DEVELOPER_REFERENCE.md)
- [Implementation Guide](docs/IMPLEMENTATION_GUIDE.md)

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

---

## 📁 Project Structure

```
multi-modal-ai-generator/
├── main.py                          # Entry point, Gradio UI
├── config.py                        # Model registry & settings
├── requirements.txt                 # Dependencies
├── pyproject.toml                   # Project metadata & build
├── README.md                        # Documentation
├── LICENSE                          # License file
├── scripts/
│   └── download_models.py           # Model downloader
├── docs/                            # Detailed documentation
├── generators/                      # Generation logic
├── utils/                           # Utilities
└── tests/                           # Tests
```

---

## ⚖️ License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

See [docs/DEVELOPER_REFERENCE.md](docs/DEVELOPER_REFERENCE.md) for contribution guidelines.
