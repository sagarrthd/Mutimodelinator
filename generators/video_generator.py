"""Video generation module for creating videos from text and images."""

import logging
import random
import time
from typing import Any, Dict, Optional, Tuple

import numpy as np
import torch
from PIL import Image

from utils.error_handler import InferenceError, handle_generation_error
from utils.model_cache import run_inference
from utils.validators import validate_fps, validate_motion_bucket_id, validate_prompt

from .base import BaseGenerator

logger = logging.getLogger(__name__)


class VideoGenerator(BaseGenerator):
    """Generator for video creation (text-to-video and image-to-video)."""

    def generate(
        self,
        prompt: str,
        num_frames: int = 16,
        fps: int = 8,
        conditioning_image: Optional[Image.Image] = None,
        motion_bucket_id: int = 127,
        seed: int = -1,
        progress_callback=None,
    ) -> Tuple[Optional[list], str]:
        """Generate video from text or image.
        
        Args:
            prompt: Text prompt describing the video
            num_frames: Number of frames to generate (8-48)
            fps: Frames per second (4-30)
            conditioning_image: Optional input image for img2vid mode
            motion_bucket_id: Motion intensity for img2vid (1-255, default 127)
            seed: Random seed (-1 for random)
            progress_callback: Optional callback for progress updates
            
        Returns:
            Tuple of (list_of_frame_images, status_message)
        """
        try:
            # Validate input
            valid, msg = validate_prompt(prompt, max_length=500)
            if not valid:
                return None, f"⚠️ Prompt error: {msg}"

            valid, msg = validate_fps(fps)
            if not valid:
                return None, f"⚠️ FPS error: {msg}"

            if conditioning_image and "img2vid" in self.model_config.get("type", ""):
                valid, msg = validate_motion_bucket_id(motion_bucket_id)
                if not valid:
                    return None, f"⚠️ Motion bucket error: {msg}"

            # Ensure model is loaded
            if not self.pipeline:
                self.load_model()

            # Handle random seed
            if seed == -1:
                seed = random.randint(0, 2**32 - 1)

            logger.info(f"Generating video: {prompt[:50]}...")
            start_time = time.time()

            # Prepare inference kwargs based on model type
            if self.model_config.get("type") == "image-to-video":
                # Image-to-video generation (e.g., Stable Video Diffusion)
                if not conditioning_image:
                    return (
                        None,
                        "⚠️ Image-to-video requires an input image",
                    )

                inference_kwargs = {
                    "image": conditioning_image,
                    "num_frames": num_frames,
                    "fps": fps,
                    "motion_bucket_id": motion_bucket_id,
                    "generator": torch.Generator(
                        device=self.device_manager.device
                    ).manual_seed(seed),
                }
                logger.info("Using image-to-video mode")
            else:
                # Text-to-video generation
                inference_kwargs = {
                    "prompt": prompt,
                    "num_frames": num_frames,
                    "height": 576,  # Standard video resolution
                    "width": 1024,
                    "num_inference_steps": 30,
                    "generator": torch.Generator(
                        device=self.device_manager.device
                    ).manual_seed(seed),
                }
                logger.info("Using text-to-video mode")

            # Run inference
            output = run_inference(
                self.pipeline,
                device=self.device_manager.device,
                use_amp=True,
                **inference_kwargs,
            )

            # Extract frames from output
            if hasattr(output, "frames"):
                frames = output.frames[0]  # Get first video from batch
            elif isinstance(output, tuple) and len(output) > 0:
                frames = output[0]
            else:
                frames = output

            # Ensure frames are PIL Images
            if isinstance(frames, np.ndarray):
                # Convert numpy array to PIL Images
                frames = self._numpy_to_pil_frames(frames)
            elif not isinstance(frames, list):
                frames = [frames]

            duration = time.time() - start_time
            self._record_generation_time(duration)

            # Prepare success message
            status_msg = (
                f"✓ Generated in {duration:.1f}s\n"
                f"Model: {self.repo_id.split('/')[-1]}\n"
                f"Frames: {len(frames)}\n"
                f"FPS: {fps}\n"
                f"Duration: {len(frames)/fps:.1f}s\n"
                f"Seed: {seed}\n"
                f"Device: {self.device_manager.device_name}"
            )

            logger.info(f"Video generation successful: {len(frames)} frames @ {fps}fps")
            return frames, status_msg

        except InferenceError as e:
            logger.error(f"Inference error: {e}")
            return None, f"❌ Generation failed: {str(e)}"
        except Exception as e:
            return handle_generation_error(e, logger)

    def _numpy_to_pil_frames(self, numpy_array: np.ndarray) -> list:
        """Convert numpy array to list of PIL Images.
        
        Args:
            numpy_array: Array of shape (frames, height, width, channels) with values 0-255
            
        Returns:
            List of PIL Image objects
        """
        frames = []
        if numpy_array.dtype != np.uint8:
            # Normalize to 0-255 range
            numpy_array = ((numpy_array + 1) / 2 * 255).astype(np.uint8)

        for i in range(numpy_array.shape[0]):
            frame_array = numpy_array[i]
            if frame_array.shape[2] == 3:  # RGB
                frame = Image.fromarray(frame_array, mode="RGB")
            elif frame_array.shape[2] == 4:  # RGBA
                frame = Image.fromarray(frame_array, mode="RGBA")
            else:
                # Grayscale
                frame = Image.fromarray(frame_array[:, :, 0], mode="L")
            frames.append(frame)

        return frames

    def frames_to_video_file(
        self,
        frames: list,
        output_path: str,
        fps: int = 8,
        codec: str = "mp4v",
    ) -> Tuple[bool, str]:
        """Save frames as video file using moviepy.
        
        Args:
            frames: List of PIL Images
            output_path: Path to save video
            fps: Frames per second
            codec: Video codec ('mp4v', 'libx264', etc.)
            
        Returns:
            Tuple of (success, status_message)
        """
        try:
            import moviepy.editor as mpy

            # Convert PIL images to numpy arrays
            video_array = np.array([np.array(frame) for frame in frames])

            # Create video clip
            clip = mpy.ImageSequenceClip(list(video_array), fps=fps)

            # Write to file
            clip.write_videofile(
                output_path,
                codec=codec,
                audio=False,
                verbose=False,
                logger=None,
            )

            file_size_mb = (
                __import__("os").path.getsize(output_path) / (1024 * 1024)
            )
            logger.info(f"Video saved: {output_path} ({file_size_mb:.1f}MB)")
            return True, f"✓ Video saved: {output_path} ({file_size_mb:.1f}MB)"

        except ImportError:
            return (
                False,
                "❌ moviepy not installed. Install with: pip install moviepy",
            )
        except Exception as e:
            logger.error(f"Video save failed: {e}")
            return False, f"❌ Failed to save video: {str(e)}"

    def get_recommended_settings(self) -> Dict[str, Any]:
        """Get recommended settings for this model.
        
        Returns:
            Dictionary with recommended parameters
        """
        return {
            "max_frames": self.model_config.get("max_frames", 24),
            "default_fps": self.model_config.get("fps", 8),
            "video_type": self.model_config.get("type", "text-to-video"),
        }
