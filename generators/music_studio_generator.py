"""Music Studio Generator for professional music creation (Suno AI-like features)."""

import logging
import time
import random
from typing import Optional, Tuple, Any, Dict, List
import numpy as np
import torch
from utils.error_handler import InferenceError, handle_generation_error
from utils.model_cache import run_inference
from utils.validators import validate_prompt, validate_duration
from .base import BaseGenerator

logger = logging.getLogger(__name__)


class MusicStudioGenerator(BaseGenerator):
    """Advanced generator for professional music creation with full control."""

    def generate(self, **kwargs) -> Tuple[Optional[Tuple[int, np.ndarray]], str]:
        """Generate music - wrapper for generate_music.
        
        This implements the abstract method from BaseGenerator.
        Delegates to generate_music() with all kwargs.
        """
        return self.generate_music(**kwargs)

    def generate_music(
        self,
        prompt: str = "",
        genre: str = "Pop",
        mood: str = "Happy/Upbeat",
        vocals: str = "No Vocals (Instrumental)",
        tempo_bpm: int = 120,
        duration_seconds: float = 30.0,
        key: str = "C Major",
        instruments: List[str] = None,
        lyrics: str = "",
        reference_audio: Optional[np.ndarray] = None,
        structure: str = "Simple",
        production_quality: str = "High",
        seed: int = -1,
        progress_callback=None,
    ) -> Tuple[Optional[Tuple[int, np.ndarray]], str]:
        """Generate professional music with advanced controls.
        
        Args:
            prompt: Main text description (will be auto-built if empty)
            genre: Music genre
            mood: Emotional mood/vibe
            vocals: Vocal type (instrumental, male, female, etc.)
            tempo_bpm: Beats per minute (40-220)
            duration_seconds: Duration of music (10-120 seconds)
            key: Musical key (C Major, D Minor, etc.)
            instruments: List of instruments to include
            lyrics: Optional lyrics for vocal generation
            reference_audio: Optional reference audio for style transfer
            structure: Song structure (Simple, Standard, Extended)
            production_quality: Quality level (Draft, High, Studio)
            seed: Random seed (-1 for random)
            progress_callback: Optional callback for progress updates
            
        Returns:
            Tuple of ((sample_rate, audio_array), status_message)
        """
        try:
            # Build comprehensive prompt
            if not prompt:
                prompt = self._build_music_prompt(
                    genre, mood, vocals, tempo_bpm, key, instruments, lyrics
                )
            
            # Validate inputs
            valid, msg = validate_prompt(prompt, max_length=1000)
            if not valid:
                return None, f"⚠️ Prompt error: {msg}"

            valid, msg = validate_duration(
                duration_seconds,
                min_duration=10.0,
                max_duration=self.model_config.get("max_duration", 120),
            )
            if not valid:
                return None, f"⚠️ Duration error: {msg}"

            # Ensure model is loaded
            if not self.pipeline:
                self.load_model()

            # Handle random seed
            if seed == -1:
                seed = random.randint(0, 2**32 - 1)

            logger.info(f"Generating music: {prompt[:100]}...")
            start_time = time.time()

            # Prepare model-specific inference kwargs
            model_name = self.repo_id.lower()
            
            if "ace-step" in model_name or "ace_step" in model_name:
                inference_kwargs = self._prepare_ace_step_kwargs(
                    prompt, duration_seconds, tempo_bpm, key, lyrics, 
                    reference_audio, vocals, seed
                )
            elif "heartmula" in model_name:
                inference_kwargs = self._prepare_heartmula_kwargs(
                    prompt, duration_seconds, tempo_bpm, key, lyrics, 
                    reference_audio, vocals, seed
                )
            elif "qwen3-tts" in model_name or "qwen3_tts" in model_name:
                inference_kwargs = self._prepare_qwen_tts_kwargs(
                    prompt, lyrics, vocals, seed
                )
            elif "stable-audio" in model_name:
                inference_kwargs = self._prepare_stable_audio_kwargs(
                    prompt, duration_seconds, tempo_bpm, seed
                )
            elif "musicgen" in model_name:
                inference_kwargs = self._prepare_musicgen_kwargs(
                    prompt, duration_seconds, reference_audio, seed
                )
            else:
                # Generic fallback
                inference_kwargs = {
                    "prompt": prompt,
                    "duration": duration_seconds,
                    "seed": seed
                }

            # Run inference
            output = run_inference(
                self.pipeline,
                device=self.device_manager.device,
                use_amp=True,
                **inference_kwargs,
            )

            # Extract audio from output
            audio = self._extract_audio(output)
            sample_rate = self.model_config.get("sample_rate", 44100)
            
            duration = time.time() - start_time
            self._record_generation_time(duration)

            # Prepare success message
            audio_duration = audio.shape[1] / sample_rate
            status_msg = self._format_success_message(
                duration, audio_duration, sample_rate, audio.shape[0],
                genre, mood, tempo_bpm, key, seed
            )

            logger.info(f"Music generation successful: {audio.shape} @ {sample_rate}Hz")
            return (sample_rate, audio), status_msg

        except InferenceError as e:
            logger.error(f"Inference error: {e}")
            return None, f"❌ Generation failed: {str(e)}"
        except Exception as e:
            return handle_generation_error(e, logger)

    def _build_music_prompt(
        self, 
        genre: str, 
        mood: str, 
        vocals: str, 
        tempo_bpm: int, 
        key: str, 
        instruments: List[str],
        lyrics: str
    ) -> str:
        """Build a comprehensive music generation prompt."""
        parts = []
        
        # Genre and mood
        parts.append(f"{mood.lower()} {genre.lower()} music")
        
        # Tempo description
        if tempo_bpm < 80:
            parts.append("slow tempo")
        elif tempo_bpm < 120:
            parts.append("moderate tempo")
        else:
            parts.append("fast tempo")
        
        # Vocals
        if vocals != "No Vocals (Instrumental)":
            parts.append(f"with {vocals.lower()}")
        else:
            parts.append("instrumental")
        
        # Key
        parts.append(f"in {key}")
        
        # Instruments
        if instruments:
            inst_str = ", ".join(instruments[:3])  # Limit to 3 for readability
            parts.append(f"featuring {inst_str}")
        
        # Lyrics hint
        if lyrics:
            parts.append("with custom lyrics")
        
        prompt = ", ".join(parts)
        return prompt.capitalize()

    def _prepare_ace_step_kwargs(
        self,
        prompt: str,
        duration: float,
        tempo_bpm: int,
        key: str,
        lyrics: str,
        reference_audio: Optional[np.ndarray],
        vocals: str,
        seed: int
    ) -> Dict[str, Any]:
        """Prepare kwargs for ACE Step 1.5 model.
        
        ACE Step supports:
        - Text-to-music generation
        - Lyrics-to-song generation
        - Cover generation (style transfer)
        - Vocal-to-BGM conversion
        """
        kwargs = {
            "prompt": prompt,
            "duration": duration,
            "tempo": tempo_bpm,
            "seed": seed,
        }
        
        # ACE Step specific parameters
        if lyrics and self.model_config.get("supports_lyrics"):
            kwargs["lyrics"] = lyrics
            kwargs["task"] = "lyrics-to-song"
        else:
            kwargs["task"] = "text-to-music"
        
        if reference_audio is not None and self.model_config.get("supports_reference"):
            kwargs["reference_audio"] = reference_audio
            kwargs["task"] = "cover-generation"
        
        if vocals != "No Vocals (Instrumental)" and self.model_config.get("supports_vocals"):
            kwargs["vocal_style"] = vocals.lower()
            kwargs["enable_vocals"] = True
        else:
            kwargs["enable_vocals"] = False
        
        # Musical parameters
        if key:
            kwargs["key"] = key
        
        return kwargs

    def _prepare_qwen_tts_kwargs(
        self,
        prompt: str,
        lyrics: str,
        vocals: str,
        seed: int
    ) -> Dict[str, Any]:
        """Prepare kwargs for Qwen3-TTS model.
        
        Qwen3-TTS is primarily a speech synthesis model but can be used for:
        - Text-to-speech
        - Multilingual speech
        - Voice-over generation
        """
        # For TTS, the text to speak is either the lyrics or the prompt
        text_to_speak = lyrics if lyrics else prompt
        
        kwargs = {
            "text": text_to_speak,
            "task": "speech-generation",
            "seed": seed,
        }
        
        # Vocal style mapping for TTS
        if vocals and vocals != "No Vocals (Instrumental)":
            if "male" in vocals.lower():
                kwargs["voice_style"] = "male"
            elif "female" in vocals.lower():
                kwargs["voice_style"] = "female"
            elif "rap" in vocals.lower():
                kwargs["voice_style"] = "rap"
            else:
                kwargs["voice_style"] = "neutral"
        
        return kwargs

    def _prepare_heartmula_kwargs(
        self,
        prompt: str,
        duration: float,
        tempo_bpm: int,
        key: str,
        lyrics: str,
        reference_audio: Optional[np.ndarray],
        vocals: str,
        seed: int
    ) -> Dict[str, Any]:
        """Prepare kwargs for HeartMuLa model."""
        kwargs = {
            "text_prompt": prompt,
            "duration": duration,
            "tempo": tempo_bpm,
            "key": key,
            "seed": seed
        }
        
        if lyrics and self.model_config.get("supports_lyrics"):
            kwargs["lyrics"] = lyrics
        
        if reference_audio is not None and self.model_config.get("supports_reference"):
            kwargs["reference_audio"] = reference_audio
        
        if vocals != "No Vocals (Instrumental)" and self.model_config.get("supports_vocals"):
            kwargs["vocal_type"] = vocals.lower()
        
        return kwargs

    def _prepare_stable_audio_kwargs(
        self,
        prompt: str,
        duration: float,
        tempo_bpm: int,
        seed: int
    ) -> Dict[str, Any]:
        """Prepare kwargs for Stable Audio Open."""
        return {
            "prompt": prompt,
            "duration_seconds": duration,
            "tempo": tempo_bpm,
            "seed": seed
        }

    def _prepare_musicgen_kwargs(
        self,
        prompt: str,
        duration: float,
        reference_audio: Optional[np.ndarray],
        seed: int
    ) -> Dict[str, Any]:
        """Prepare kwargs for MusicGen."""
        kwargs = {
            "descriptions": [prompt],
            "duration": duration,
            "seed": seed
        }
        
        if reference_audio is not None:
            # MusicGen supports melody conditioning
            kwargs["melody_wavs"] = reference_audio
        
        return kwargs

    def _extract_audio(self, output: Any) -> np.ndarray:
        """Extract audio array from model output."""
        if hasattr(output, "audio"):
            audio = output.audio
        elif hasattr(output, "waveform"):
            audio = output.waveform
        elif isinstance(output, tuple) and len(output) > 0:
            audio = output[0]
        else:
            audio = output

        # Ensure audio is numpy array
        if not isinstance(audio, np.ndarray):
            if torch.is_tensor(audio):
                audio = audio.cpu().numpy()
            else:
                audio = np.array(audio)

        # Ensure correct shape (channels, samples)
        if len(audio.shape) == 1:
            audio = audio[np.newaxis, :]  # Add channel dimension
        elif len(audio.shape) == 2 and audio.shape[0] > audio.shape[1]:
            # Transpose if samples x channels instead of channels x samples
            audio = audio.T

        return audio

    def _format_success_message(
        self,
        gen_time: float,
        audio_duration: float,
        sample_rate: int,
        channels: int,
        genre: str,
        mood: str,
        tempo_bpm: int,
        key: str,
        seed: int
    ) -> str:
        """Format detailed success message."""
        return (
            f"✓ Music generated in {gen_time:.1f}s\n"
            f"Model: {self.repo_id.split('/')[-1]}\n"
            f"Genre: {genre} | Mood: {mood}\n"
            f"Tempo: {tempo_bpm} BPM | Key: {key}\n"
            f"Duration: {audio_duration:.1f}s | {sample_rate}Hz\n"
            f"Channels: {channels} | Seed: {seed}"
        )

    def extend_music(
        self,
        existing_audio: Tuple[int, np.ndarray],
        extension_duration: float = 15.0,
        maintain_style: bool = True,
        seed: int = -1,
    ) -> Tuple[Optional[Tuple[int, np.ndarray]], str]:
        """Extend existing music by generating continuation.
        
        Args:
            existing_audio: Tuple of (sample_rate, audio_array)
            extension_duration: How many seconds to extend
            maintain_style: Whether to match the existing style
            seed: Random seed
            
        Returns:
            Tuple of ((sample_rate, extended_audio), status_message)
        """
        try:
            sample_rate, audio = existing_audio
            
            if maintain_style:
                # Use the last portion as reference
                reference_length = min(audio.shape[1], sample_rate * 5)  # Last 5 seconds
                reference_audio = audio[:, -reference_length:]
            else:
                reference_audio = None
            
            # Generate extension using reference
            new_audio, status = self.generate_music(
                prompt="Continue the previous music",
                duration_seconds=extension_duration,
                reference_audio=reference_audio,
                seed=seed
            )
            
            if new_audio:
                ext_sample_rate, ext_audio = new_audio
                
                # Concatenate with crossfade
                combined = self._crossfade_audio(audio, ext_audio, sample_rate, fade_duration=1.0)
                
                return (sample_rate, combined), f"✓ Extended by {extension_duration}s\n{status}"
            
            return None, "❌ Extension failed"
            
        except Exception as e:
            logger.error(f"Extension error: {e}")
            return None, f"❌ Extension failed: {str(e)}"

    def _crossfade_audio(
        self,
        audio1: np.ndarray,
        audio2: np.ndarray,
        sample_rate: int,
        fade_duration: float = 1.0
    ) -> np.ndarray:
        """Crossfade two audio arrays."""
        fade_samples = int(sample_rate * fade_duration)
        
        # Create fade curves
        fade_out = np.linspace(1, 0, fade_samples).reshape(1, -1)
        fade_in = np.linspace(0, 1, fade_samples).reshape(1, -1)
        
        # Apply crossfade to overlapping region
        overlap = min(fade_samples, audio1.shape[1], audio2.shape[1])
        
        audio1_fade = audio1.copy()
        audio2_fade = audio2.copy()
        
        audio1_fade[:, -overlap:] *= fade_out[:, :overlap]
        audio2_fade[:, :overlap] *= fade_in[:, :overlap]
        
        # Combine
        combined = np.concatenate([
            audio1[:, :-overlap],
            audio1_fade[:, -overlap:] + audio2_fade[:, :overlap],
            audio2[:, overlap:]
        ], axis=1)
        
        return combined
