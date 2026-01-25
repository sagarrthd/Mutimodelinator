"""Setup script for downloading models on first run."""

import os
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from utils import setup_logging, get_device_manager
from config import IMAGE_MODELS, AUDIO_MODELS, VIDEO_MODELS

logger = setup_logging("setup.log")


def download_model(repo_id: str, description: str):
    """Download a model from HuggingFace.
    
    Args:
        repo_id: HuggingFace repository ID
        description: Human-readable description
    """
    try:
        from diffusers import DiffusionPipeline
        from transformers import AutoModel

        logger.info(f"Downloading {description}...")
        print(f"📥 {description}...")

        # Try to load diffusion pipeline
        try:
            pipeline = DiffusionPipeline.from_pretrained(
                repo_id,
                use_safetensors=True,
            )
            logger.info(f"✓ Downloaded: {repo_id}")
            print(f"   ✓ Complete")
        except Exception:
            # Try as regular model
            model = AutoModel.from_pretrained(repo_id)
            logger.info(f"✓ Downloaded: {repo_id}")
            print(f"   ✓ Complete")

    except Exception as e:
        logger.warning(f"Failed to download {repo_id}: {e}")
        print(f"   ⚠️  Failed: {e}")


def main():
    """Main setup function."""
    print("\n" + "=" * 60)
    print("Offline AI Generator - Model Setup")
    print("=" * 60)

    device_manager = get_device_manager()
    print(f"\nDevice: {device_manager.device_name}")
    print(f"Available VRAM: {device_manager.vram_available:.2f}GB")
    print(f"Available RAM: {device_manager.ram_available:.2f}GB")

    print("\n" + "=" * 60)
    print("Select models to download:")
    print("=" * 60)

    models_to_download = []

    # Image models
    print("\n📸 IMAGE MODELS:")
    for i, (name, config) in enumerate(IMAGE_MODELS.items(), 1):
        print(
            f"  {i}. {name} ({config['vram_estimate']}GB VRAM) - "
            f"{config['repo_id']}"
        )
    
    image_choice = input("\nDownload image models? (y=all, n=none, numbers=specific): ").lower()
    if image_choice == "y":
        models_to_download.extend(IMAGE_MODELS.values())
    elif image_choice != "n":
        try:
            indices = [int(x) - 1 for x in image_choice.split(",")]
            for idx in indices:
                if 0 <= idx < len(IMAGE_MODELS):
                    models_to_download.append(list(IMAGE_MODELS.values())[idx])
        except ValueError:
            pass

    # Audio models
    print("\n🎵 AUDIO MODELS:")
    for i, (name, config) in enumerate(AUDIO_MODELS.items(), 1):
        print(f"  {i}. {name} ({config['vram_estimate']}GB) - {config['repo_id']}")

    audio_choice = input("\nDownload audio models? (y/n): ").lower()
    if audio_choice == "y":
        models_to_download.extend(AUDIO_MODELS.values())

    # Video models
    print("\n🎬 VIDEO MODELS:")
    for i, (name, config) in enumerate(VIDEO_MODELS.items(), 1):
        print(f"  {i}. {name} ({config['vram_estimate']}GB) - {config['repo_id']}")

    video_choice = input("\nDownload video models? (y/n): ").lower()
    if video_choice == "y":
        models_to_download.extend(VIDEO_MODELS.values())

    if not models_to_download:
        print("\n⏭️  No models selected. Exiting.")
        return

    # Download selected models
    print("\n" + "=" * 60)
    print(f"Downloading {len(models_to_download)} model(s)...")
    print("=" * 60)

    for config in models_to_download:
        download_model(config["repo_id"], config["repo_id"].split("/")[-1])

    print("\n" + "=" * 60)
    print("✓ Setup complete!")
    print("=" * 60)
    print("\nNow run: python main.py")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Setup cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.exception("Setup error")
        print(f"\n❌ Error: {e}")
        sys.exit(1)
