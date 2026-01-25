"""Image generation module using diffusion models."""

import logging
import time
import random
from typing import Optional, Tuple, Any, Dict
import torch
from PIL import Image
from utils.error_handler import InferenceError, handle_generation_error
from utils.model_cache import run_inference
from utils.validators import validate_all_image_params
from .base import BaseGenerator

logger = logging.getLogger(__name__)


class ImageGenerator(BaseGenerator):
    """Generator for image creation using diffusion models."""

    def generate(
        self,
        prompt: str,
        negative_prompt: str = "",
        steps: int = 20,
        guidance_scale: float = 7.5,
        width: int = 1024,
        height: int = 1024,
        seed: int = -1,
        img2img_image: Optional[Image.Image] = None,
        img2img_strength: float = 0.75,
        progress_callback=None,
    ) -> Tuple[Optional[Image.Image], str]:
        """Generate image from text prompt.
        
        Args:
            prompt: Positive prompt describing the image
            negative_prompt: Negative prompt for filtering
            steps: Number of inference steps (1-100)
            guidance_scale: Guidance scale (1.0-20.0)
            width: Image width in pixels (256-2048, multiple of 64)
            height: Image height in pixels (256-2048, multiple of 64)
            seed: Random seed (-1 for random)
            img2img_image: Optional input image for img2img mode
            img2img_strength: Strength of img2img transformation (0-1)
            progress_callback: Optional callback for progress updates
            
        Returns:
            Tuple of (generated_image, status_message)
        """
        try:
            # Validate all parameters
            steps_for_validation = steps
            if img2img_image:
                max_steps = 100
            else:
                max_steps = 100

            valid, error_msg = validate_all_image_params(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                steps=steps_for_validation,
                guidance=guidance_scale,
                seed=seed,
                max_steps=max_steps,
            )

            if not valid:
                return None, f"⚠️ Validation error: {error_msg}"

            # Ensure model is loaded
            if not self.pipeline:
                self.load_model()

            # Handle random seed
            if seed == -1:
                seed = random.randint(0, 2**32 - 1)

            logger.info(f"Generating image: {prompt[:50]}...")
            start_time = time.time()

            # Prepare inference kwargs based on model type
            inference_kwargs = {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "num_inference_steps": steps,
                "guidance_scale": guidance_scale,
                "generator": torch.Generator(device=self.device_manager.device).manual_seed(
                    seed
                ),
            }

            # Add img2img parameters if image provided
            if img2img_image:
                inference_kwargs["image"] = img2img_image
                inference_kwargs["strength"] = img2img_strength
                # For img2img, dimensions come from input image
                logger.info("Using img2img mode")
            else:
                # For txt2img, add explicit dimensions
                inference_kwargs["height"] = height
                inference_kwargs["width"] = width

            # Run inference with memory optimization
            output = run_inference(
                self.pipeline,
                device=self.device_manager.device,
                use_amp=True,
                **inference_kwargs,
            )

            # Extract image from pipeline output
            if hasattr(output, "images"):
                image = output.images[0]
            else:
                image = output[0]  # Some pipelines return tuple

            duration = time.time() - start_time
            self._record_generation_time(duration)

            # Prepare success message with metadata
            status_msg = (
                f"✓ Generated in {duration:.1f}s\n"
                f"Model: {self.repo_id.split('/')[-1]}\n"
                f"Seed: {seed}\n"
                f"Resolution: {image.width}x{image.height}\n"
                f"Device: {self.device_manager.device_name}"
            )

            logger.info(f"Image generation successful: {image.size}")
            return image, status_msg

        except InferenceError as e:
            logger.error(f"Inference error: {e}")
            return None, f"❌ Generation failed: {str(e)}"
        except Exception as e:
            return handle_generation_error(e, logger)

    def generate_batch(
        self,
        prompts: list,
        num_images_per_prompt: int = 1,
        **kwargs,
    ) -> Tuple[list, str]:
        """Generate multiple images for multiple prompts.
        
        Args:
            prompts: List of prompts
            num_images_per_prompt: Number of variations per prompt
            **kwargs: Additional generation parameters
            
        Returns:
            Tuple of (list_of_images, status_message)
        """
        try:
            if not self.pipeline:
                self.load_model()

            all_images = []
            start_time = time.time()

            for i, prompt in enumerate(prompts):
                logger.info(f"Generating prompt {i+1}/{len(prompts)}")
                for j in range(num_images_per_prompt):
                    image, status = self.generate(prompt=prompt, seed=-1, **kwargs)
                    if image:
                        all_images.append(image)

            duration = time.time() - start_time
            status_msg = (
                f"✓ Batch generation complete\n"
                f"Generated {len(all_images)} images in {duration:.1f}s"
            )
            return all_images, status_msg

        except Exception as e:
            return [], f"❌ Batch generation failed: {str(e)}"

    def get_recommended_settings(self) -> Dict[str, Any]:
        """Get recommended settings for this model.
        
        Returns:
            Dictionary with recommended parameters
        """
        return {
            "recommended_steps": self.model_config.get("recommended_steps", 20),
            "default_guidance": self.model_config.get("default_guidance", 7.5),
            "min_steps": self.model_config.get("min_steps", 1),
            "max_steps": self.model_config.get("max_steps", 100),
        }
