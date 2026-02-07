"""Unit tests for generator modules and core functions."""

import pytest
from unittest import mock

from config import IMAGE_MODELS, AUDIO_MODELS, MUSIC_STUDIO_MODELS
from generators import ImageGenerator, AudioGenerator, MusicStudioGenerator
from utils import (
    validate_prompt,
    validate_image_dimensions,
    validate_steps,
    validate_guidance_scale,
    validate_seed,
    validate_all_image_params,
)


# ==================== VALIDATION TESTS ====================


class TestValidators:
    """Test input validation functions."""

    def test_validate_prompt_valid(self):
        """Test valid prompt validation."""
        valid, msg = validate_prompt("A beautiful landscape")
        assert valid is True
        assert msg == ""

    def test_validate_prompt_empty(self):
        """Test empty prompt validation."""
        valid, msg = validate_prompt("")
        assert valid is False

    def test_validate_prompt_too_long(self):
        """Test prompt length limit."""
        long_prompt = "a" * 3000
        valid, msg = validate_prompt(long_prompt)
        assert valid is False

    def test_validate_image_dimensions_valid(self):
        """Test valid image dimensions."""
        valid, msg = validate_image_dimensions(1024, 1024)
        assert valid is True

    def test_validate_image_dimensions_not_multiple_64(self):
        """Test dimension must be multiple of 64."""
        valid, msg = validate_image_dimensions(1000, 1024)
        assert valid is False

    def test_validate_steps_valid(self):
        """Test valid steps."""
        valid, msg = validate_steps(20)
        assert valid is True

    def test_validate_steps_out_of_range(self):
        """Test steps out of range."""
        valid, msg = validate_steps(150)
        assert valid is False

    def test_validate_guidance_scale(self):
        """Test guidance scale validation."""
        valid, msg = validate_guidance_scale(7.5)
        assert valid is True

        valid, msg = validate_guidance_scale(25.0)
        assert valid is False

    def test_validate_seed_valid(self):
        """Test valid seed values."""
        valid, msg = validate_seed(-1)  # Random seed
        assert valid is True

        valid, msg = validate_seed(12345)
        assert valid is True

    def test_validate_all_image_params(self):
        """Test batch validation of image parameters."""
        valid, msg = validate_all_image_params(
            prompt="A test image",
            negative_prompt="blurry",
            width=1024,
            height=1024,
            steps=20,
            guidance=7.5,
            seed=-1,
        )
        assert valid is True


# ==================== GENERATOR TESTS ====================


class TestImageGenerator:
    """Test image generation."""

    def test_generator_creation(self):
        """Test creating an image generator."""
        config = IMAGE_MODELS[list(IMAGE_MODELS.keys())[0]]
        generator = ImageGenerator(config)
        assert generator.repo_id == config["repo_id"]
        assert generator.vram_estimate == config["vram_estimate"]

    def test_invalid_config(self):
        """Test generator with invalid config."""
        with pytest.raises(ValueError):
            ImageGenerator({})  # Missing repo_id

    def test_get_model_info(self):
        """Test getting model info."""
        config = IMAGE_MODELS[list(IMAGE_MODELS.keys())[0]]
        generator = ImageGenerator(config)
        info = generator.get_model_info()
        assert "repo_id" in info
        assert "vram_estimate" in info
        assert "loaded" in info


class TestAudioGenerator:
    """Test audio generation."""

    def test_generator_creation(self):
        """Test creating an audio generator."""
        config = AUDIO_MODELS[list(AUDIO_MODELS.keys())[0]]
        generator = AudioGenerator(config)
        assert generator.repo_id == config["repo_id"]


class TestMusicStudioGenerator:
    """Test music studio generation."""

    def test_generator_creation(self):
        """Test creating a music studio generator."""
        config = MUSIC_STUDIO_MODELS[list(MUSIC_STUDIO_MODELS.keys())[0]]
        generator = MusicStudioGenerator(config)
        assert generator.repo_id == config["repo_id"]

    def test_build_prompt_includes_core_attributes(self):
        """Test prompt builder contains major user options."""
        config = MUSIC_STUDIO_MODELS[list(MUSIC_STUDIO_MODELS.keys())[0]]
        generator = MusicStudioGenerator(config)

        prompt = generator._build_music_prompt(
            genre="Jazz",
            mood="Calm/Relaxing",
            vocals="No Vocals (Instrumental)",
            tempo_bpm=95,
            key="F Major",
            instruments=["Piano", "Bass"],
            lyrics="",
        )

        assert "jazz" in prompt.lower()
        assert "f major" in prompt.lower()
        assert "instrumental" in prompt.lower()


# ==================== PERFORMANCE TESTS ====================


class TestDeviceOptimization:
    """Test device optimization and detection."""

    def test_device_detection(self):
        """Test that device detection works."""
        from utils import get_device_manager

        dm = get_device_manager()
        assert dm.device in ["cuda", "cpu", "mps"]

    def test_vram_checking(self):
        """Test VRAM checking (if GPU available)."""
        from utils import get_device_manager

        dm = get_device_manager()
        if dm.device == "cuda":
            assert dm.vram_total > 0
            assert dm.vram_available > 0


# ==================== OFFLINE TESTS ====================


@pytest.mark.skip(reason="Requires network isolation")
class TestOfflineOperation:
    """Test that app works without internet."""

    def test_generation_offline(self):
        """Verify generation works with network disabled."""
        with mock.patch("socket.socket"):  # Block network
            # This would require a loaded model in cache
            pass


# ==================== INTEGRATION TESTS ====================


@pytest.mark.integration
class TestIntegration:
    """Integration tests for the full pipeline."""

    def test_import_all_modules(self):
        """Test that all modules import correctly."""
        import config
        import main
        from generators import ImageGenerator, AudioGenerator, MusicStudioGenerator
        from utils import get_device_manager

        assert config is not None
        assert main is not None
        assert ImageGenerator is not None
        assert get_device_manager() is not None


if __name__ == "__main__":
    # Run tests: pytest tests/test_generators.py -v
    pytest.main([__file__, "-v"])
