"""Audio generation module for music and speech synthesis."""

import logging
import time
import random
from typing import Optional, Tuple, Any, Dict
import numpy as np
import torch
from utils.error_handler import InferenceError, handle_generation_error
from utils.model_cache import run_inference
from utils.validators import validate_prompt, validate_duration, validate_temperature
from .base import BaseGenerator

logger = logging.getLogger(__name__)


class AudioGenerator(BaseGenerator):
    """Generator for audio creation (music and speech synthesis)."""

    def generate(
        self,
        prompt: str,
        duration_seconds: float = 10.0,
        temperature: float = 1.0,
        seed: int = -1,
        progress_callback=None,
    ) -> Tuple[Optional[Tuple[int, np.ndarray]], str]:
        """Generate audio from text prompt.
        
        Args:
            prompt: Text prompt describing the audio to generate
            duration_seconds: Duration of audio to generate (1-30 seconds)
            temperature: Sampling temperature for generation (0.1-2.0)
            seed: Random seed (-1 for random)
            progress_callback: Optional callback for progress updates
            
        Returns:
            Tuple of ((sample_rate, audio_array), status_message)
            audio_array is numpy array of shape (channels, samples)
        """
        try:
            # Validate input
            valid, msg = validate_prompt(prompt, max_length=500)
            if not valid:
                return None, f"⚠️ Prompt error: {msg}"

            valid, msg = validate_duration(
                duration_seconds,
                min_duration=1.0,
                max_duration=self.model_config.get("max_duration", 30),
            )
            if not valid:
                return None, f"⚠️ Duration error: {msg}"

            valid, msg = validate_temperature(temperature)
            if not valid:
                return None, f"⚠️ Temperature error: {msg}"

            # Ensure model is loaded
            if not self.pipeline:
                self.load_model()

            # Handle random seed
            if seed == -1:
                seed = random.randint(0, 2**32 - 1)

            logger.info(f"Generating audio: {prompt[:50]}...")
            start_time = time.time()

            # Prepare inference kwargs based on model type
            if "musicgen" in self.repo_id.lower():
                # MusicGen parameters
                inference_kwargs = {
                    "descriptions": [prompt],
                    "max_new_tokens": int(duration_seconds * 50),  # Approximate token count
                    "temperature": temperature,
                }
            elif "bark" in self.repo_id.lower():
                # Bark parameters
                inference_kwargs = {
                    "text": prompt,
                    "voice_preset": "v2/en_speaker_6",  # Default voice
                }
            else:
                # Generic audio generation
                inference_kwargs = {"prompt": prompt}

            # Run inference
            output = run_inference(
                self.pipeline,
                device=self.device_manager.device,
                use_amp=True,
                **inference_kwargs,
            )

            # Extract audio from output
            if hasattr(output, "audio"):
                audio = output.audio
            elif isinstance(output, tuple) and len(output) > 0:
                audio = output[0]
            else:
                audio = output

            # Ensure audio is numpy array
            if not isinstance(audio, np.ndarray):
                audio = np.array(audio)

            # Ensure correct shape
            if len(audio.shape) == 1:
                audio = audio[np.newaxis, :]  # Add channel dimension

            sample_rate = self.model_config.get("sample_rate", 16000)
            duration = time.time() - start_time
            self._record_generation_time(duration)

            # Prepare success message
            audio_duration = audio.shape[1] / sample_rate
            status_msg = (
                f"✓ Generated in {duration:.1f}s\n"
                f"Model: {self.repo_id.split('/')[-1]}\n"
                f"Duration: {audio_duration:.1f}s\n"
                f"Sample Rate: {sample_rate} Hz\n"
                f"Channels: {audio.shape[0]}\n"
                f"Seed: {seed}"
            )

            logger.info(f"Audio generation successful: {audio.shape} @ {sample_rate}Hz")
            return (sample_rate, audio), status_msg

        except InferenceError as e:
            logger.error(f"Inference error: {e}")
            return None, f"❌ Generation failed: {str(e)}"
        except Exception as e:
            return handle_generation_error(e, logger)

    def generate_batch(
        self,
        prompts: list,
        **kwargs,
    ) -> Tuple[list, str]:
        """Generate audio for multiple prompts sequentially.
        
        Args:
            prompts: List of prompts
            **kwargs: Additional generation parameters
            
        Returns:
            Tuple of (list_of_audio_arrays, status_message)
        """
        try:
            if not self.pipeline:
                self.load_model()

            all_audio = []
            start_time = time.time()

            for i, prompt in enumerate(prompts):
                logger.info(f"Generating audio {i+1}/{len(prompts)}")
                audio_data, status = self.generate(prompt=prompt, seed=-1, **kwargs)
                if audio_data:
                    all_audio.append(audio_data)

            duration = time.time() - start_time
            status_msg = (
                f"✓ Batch generation complete\n"
                f"Generated {len(all_audio)} audio files in {duration:.1f}s"
            )
            return all_audio, status_msg

        except Exception as e:
            return [], f"❌ Batch generation failed: {str(e)}"

    def get_recommended_settings(self) -> Dict[str, Any]:
        """Get recommended settings for this model.
        
        Returns:
            Dictionary with recommended parameters
        """
        return {
            "max_duration": self.model_config.get("max_duration", 30),
            "default_temperature": 1.0,
            "sample_rate": self.model_config.get("sample_rate", 16000),
            "task": self.model_config.get("task", "text-to-audio"),
        }
