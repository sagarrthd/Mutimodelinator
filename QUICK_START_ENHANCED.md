# 🚀 Quick Start - MultiModelinator Enhanced

## Installation (5 minutes)

### Step 1: Update Dependencies
```bash
pip install --upgrade -r requirements.txt
```

This installs:
- ✅ Core packages (torch, diffusers, gradio)
- ✅ **xformers** (30% VRAM savings)
- ✅ Other optimization packages
- ✅ Optional quantization support

### Step 2: Run Enhanced Application
```bash
python main_enhanced.py
```

### Step 3: Open in Browser
```
http://127.0.0.1:7860
```

---

## 🎨 First Generation (Step-by-Step)

### 1. Image Generation Tab
```
1. Enter Prompt: "A majestic eagle soaring over mountain peaks, detailed"
2. Model: Choose "SDXL 1.0" (balanced quality/speed)
3. Steps: Keep at 30
4. Guidance: 7.5
5. Click: "✨ Generate Image"
```

### 2. What Happens:
- Status shows "🎨 Generating image..."
- Model loads first time (~15s)
- Generation runs (~30s for 30 steps)
- Image appears with "✓ Generated successfully!"
- File automatically saved to `outputs/images/`

### 3. Second Generation:
- Same prompt or different
- Model **already cached** - much faster!
- Only generation time (~25s)
- File saved again with new timestamp

---

## 📊 Understanding the UI

### Image Generation Tab
```
┌─────────────────────────────────────┐
│  Configuration    │    Output       │
├──────────────────────────────────────┤
│  ✨ Prompt       │  🎨 Generated   │
│  [4-line input]  │  [Image Area]   │
│                  │                 │
│  🤖 Model        │  Status         │
│  [Dropdown]      │  [Messages]     │
│                  │                 │
│  🌱 Seed  ⌲ Seed │                │
│  [Number] [Seed] │                │
│                  │                 │
│  📊 Steps  🎯 Guidance            │
│  [Slider] [Slider]                │
│                  │                 │
│  📏 Height  📏 Width              │
│  [Number]  [Number]               │
│                  │                 │
│  ✨ Generate     │                │
│  [Primary Button]│                │
└──────────────────────────────────────┘
```

### Audio Generation Tab
```
Same layout with:
- Audio-specific prompt
- Model choice (MusicGen/Bark)
- Duration slider
- Audio player output
```

### Generation History Tab
```
┌────────────────────────────────────┐
│  🔄 Refresh    🗑️ Clear            │
├────────────────────────────────────┤
│  📊 Statistics:                    │
│  Total: 5  Images: 3  Audio: 2    │
│  Size: 145 MB                      │
│                                    │
│  Gallery (4-column):               │
│  [IMG] [IMG] [IMG] [IMG]           │
│  [IMG] [IMG] [IMG] [IMG]           │
└────────────────────────────────────┘
```

### Settings Tab
```
┌────────────────────────────────────┐
│  Model Cache Status:               │
│  • Device: CUDA                    │
│  • Loaded Models: 1                │
│  • Memory: 7.2GB / 12GB            │
│                                    │
│  [🔄 Refresh] [🗑️ Clear Cache]    │
│                                    │
│  💡 Tips:                          │
│  • Use -1 seed for random          │
│  • Clear cache when switching      │
│  • xformers saves 30% VRAM         │
└────────────────────────────────────┘
```

---

## 🎯 Common Workflows

### Workflow 1: Generate Multiple Images
```
1. Stay on Image tab
2. Change prompt → Generate
   (Model cached, ~30s total)
3. Change prompt → Generate
   (Still cached, ~30s total)
4. Go to History tab → See all images
```

### Workflow 2: Try Different Models
```
1. Generate image with SDXL (16s load + 30s gen)
2. Switch to SD 1.5 model
3. Generate (5s load + 25s gen)
   → Previous SDXL cached but unloaded
4. Back to SDXL
5. Regenerate (3s load, just moved back)
```

### Workflow 3: Generate Audio
```
1. Go to Audio tab
2. Enter prompt: "Upbeat electronic dance music with synth"
3. Choose MusicGen Medium
4. Set duration: 15s
5. Generate (20-30s)
6. Audio saves automatically
```

### Workflow 4: Check History
```
1. Go to Generation History tab
2. See gallery of all images
3. View statistics
4. Click refresh to reload
5. Click clear to reset all
```

---

## 🔧 Tips & Tricks

### Tip 1: Seed Control
```
Seed = -1  → Random (always different)
Seed = 42  → Fixed (same image again)

Use fixed seed to refine prompts!
```

### Tip 2: Image Quality vs Speed
```
Fast (Low Quality):
- Model: SD 1.5
- Steps: 15
- Time: ~15s
- VRAM: 2-3GB

Balanced (Good Quality):
- Model: SDXL
- Steps: 30
- Time: ~30s
- VRAM: 6-7GB

Quality (High Quality):
- Model: FLUX.1-schnell
- Steps: 4
- Time: ~20s
- VRAM: 8-10GB
```

### Tip 3: Prompt Engineering
```
❌ Bad: "cat"
✅ Good: "fluffy tabby cat in sunlight, detailed fur"

❌ Bad: "music"
✅ Good: "upbeat electronic dance music with synth and bass"

✅ Better: "cinematic masterpiece, ultra detailed, 4K, professional"
```

### Tip 4: Memory Management
```
If getting CUDA out of memory:
1. Settings → Clear Model Cache
2. Try smaller model (SD 1.5)
3. Reduce image size (512x512)
4. Reduce steps (15-20)
```

### Tip 5: File Organization
```
Outputs stored in:
outputs/
├── images/          (auto-named: img_YYYYMMDD_HHMMSS.png)
├── audio/           (auto-named: audio_YYYYMMDD_HHMMSS.wav)
├── videos/          (auto-named: video_YYYYMMDD_HHMMSS.mp4)
└── history.json     (metadata for all generations)

Each file has metadata:
{
  "type": "image",
  "filename": "img_20260125_143022.png",
  "prompt": "beautiful sunset over ocean",
  "model": "SDXL 1.0",
  "seed": 42,
  "timestamp": "2026-01-25T14:30:22",
  "path": "/outputs/images/img_20260125_143022.png",
  "metadata": {
    "steps": 30,
    "guidance": 7.5,
    "height": 768,
    "width": 768
  }
}
```

---

## ⚙️ Performance Expectations

### First Time Setup
- Model download: 5-15 minutes (1st model)
- Subsequent models: 2-5 minutes each
- First generation: 15-30s (loading + generation)

### Normal Usage
```
SDXL Model (10GB):
├── 1st generation:  ~15s load + ~30s gen = 45s
├── 2nd generation:  ~30s gen (cached)
└── 3rd generation:  ~30s gen (cached)

Switch to SD 1.5:
├── 1st generation: ~5s load + ~25s gen = 30s
└── Back to SDXL:   ~15s load + ~30s gen (reload)

With Optimizations (xformers):
├── VRAM usage: 30% less
├── Speed: 15-20% faster
└── Quality: Identical
```

---

## 🐛 Troubleshooting

### Problem: "CUDA out of memory"
```
Solutions (in order):
1. Settings → Clear Model Cache
2. Restart app
3. Use SD 1.5 instead of SDXL
4. Reduce image size to 512x512
5. Reduce steps to 15
```

### Problem: Model takes forever to download
```
This is normal first time!
- Small models: 1-2 GB
- Large models: 5-15 GB

Don't interrupt! Let it complete.
Can take 10-30 minutes on slow internet.
```

### Problem: App crashes with error
```
Check console for error message.
Common fixes:
1. pip install --upgrade torch torchvision
2. Clear outputs directory
3. Restart Python
4. Check disk space (20GB+ needed)
```

### Problem: Image generation is slow
```
Expected timings:
- SD 1.5 (30 steps):   ~20-30s
- SDXL (30 steps):     ~30-40s
- FLUX (4 steps):      ~20-30s

If much slower:
1. Check GPU usage (nvidia-smi)
2. Close other apps
3. Reduce background apps
4. Check CPU temp (may be throttling)
```

---

## 📚 Next Steps

### Want to Learn More?
- `ENHANCEMENTS.md` - Full feature details
- `IMPLEMENTATION_GUIDE.md` - Technical details
- `config.py` - Model configurations

### Want to Customize?
1. Edit `config.py` to add models
2. Modify `main_enhanced.py` for UI changes
3. Adjust `utils/ui_theme.py` for styling

### Want to Extend?
See `ENHANCEMENTS.md` for future improvements:
- REST API
- Batch generation
- Real-ESRGAN upscaling
- Face restoration

---

## ✅ Verification Checklist

After first run, verify:
- [ ] App launches without errors
- [ ] Modern UI loads with gradient buttons
- [ ] Can generate image successfully
- [ ] Image saved to `outputs/images/`
- [ ] History shows in Generation History tab
- [ ] Settings tab shows device info
- [ ] Second generation is faster (cached)
- [ ] Status messages clear and helpful

---

## 🎉 You're Ready!

Now you have:
✅ Modern, professional UI
✅ Smart model caching (30% faster)
✅ Organized output management
✅ Performance optimizations (30% less VRAM)
✅ Generation history tracking
✅ Real-time memory monitoring

**Start generating!** Open http://127.0.0.1:7860
