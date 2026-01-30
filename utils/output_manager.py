"""
Output Manager for handling file saves, organization, and generation history.
Provides a centralized system for managing generated content with metadata.
"""

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class OutputManager:
    """Manages output files and generation history."""
    
    def __init__(self, base_dir: str = "./outputs"):
        """
        Initialize output manager.
        
        Args:
            base_dir: Base directory for all outputs
        """
        self.base_dir = Path(base_dir)
        self.history_file = self.base_dir / "history.json"
        self.images_dir = self.base_dir / "images"
        self.audio_dir = self.base_dir / "audio"
        self.video_dir = self.base_dir / "videos"
        self.models_dir = self.base_dir / "models"
        
        # Create directories
        self._setup_directories()
        self._load_history()
    
    def _setup_directories(self) -> None:
        """Create output directory structure."""
        for directory in [self.base_dir, self.images_dir, self.audio_dir, 
                         self.video_dir, self.models_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"✓ Output directories initialized at {self.base_dir}")
    
    def _load_history(self) -> None:
        """Load generation history from file."""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
            else:
                self.history = []
        except Exception as e:
            logger.error(f"Failed to load history: {e}")
            self.history = []
    
    def _save_history(self) -> None:
        """Persist generation history to file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save history: {e}")
    
    def save_image(self, image, prompt: str, model: str, seed: Optional[int] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Save generated image with metadata.
        
        Args:
            image: PIL Image object
            prompt: Generation prompt
            model: Model name used
            seed: Random seed (if any)
            metadata: Additional metadata
            
        Returns:
            Path to saved image
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"img_{timestamp}.png"
        filepath = self.images_dir / filename
        
        try:
            image.save(filepath)
            
            # Add to history
            history_entry = {
                "type": "image",
                "filename": filename,
                "prompt": prompt,
                "model": model,
                "seed": seed,
                "timestamp": datetime.now().isoformat(),
                "path": str(filepath),
                "metadata": metadata or {}
            }
            self.history.append(history_entry)
            self._save_history()
            
            logger.info(f"✓ Image saved: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Failed to save image: {e}")
            raise
    
    def save_audio(self, audio_path: str, prompt: str, model: str, duration: int,
                  metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Save generated audio with metadata.
        
        Args:
            audio_path: Path to temporary audio file
            prompt: Generation prompt
            model: Model name used
            duration: Duration in seconds
            metadata: Additional metadata
            
        Returns:
            Path to saved audio
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"audio_{timestamp}.wav"
        filepath = self.audio_dir / filename
        
        try:
            if Path(audio_path).exists():
                shutil.copy(audio_path, filepath)
            
            # Add to history
            history_entry = {
                "type": "audio",
                "filename": filename,
                "prompt": prompt,
                "model": model,
                "duration": duration,
                "timestamp": datetime.now().isoformat(),
                "path": str(filepath),
                "metadata": metadata or {}
            }
            self.history.append(history_entry)
            self._save_history()
            
            logger.info(f"✓ Audio saved: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Failed to save audio: {e}")
            raise
    
    def save_video(self, video_path: str, prompt: str, model: str, frames: int,
                  metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Save generated video with metadata.
        
        Args:
            video_path: Path to temporary video file
            prompt: Generation prompt
            model: Model name used
            frames: Number of frames
            metadata: Additional metadata
            
        Returns:
            Path to saved video
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"video_{timestamp}.mp4"
        filepath = self.video_dir / filename
        
        try:
            if Path(video_path).exists():
                shutil.copy(video_path, filepath)
            
            # Add to history
            history_entry = {
                "type": "video",
                "filename": filename,
                "prompt": prompt,
                "model": model,
                "frames": frames,
                "timestamp": datetime.now().isoformat(),
                "path": str(filepath),
                "metadata": metadata or {}
            }
            self.history.append(history_entry)
            self._save_history()
            
            logger.info(f"✓ Video saved: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Failed to save video: {e}")
            raise
    
    def get_history(self, content_type: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """
        Get generation history.
        
        Args:
            content_type: Filter by type ('image', 'audio', 'video', or None for all)
            limit: Maximum number of entries to return
            
        Returns:
            List of history entries
        """
        if content_type:
            filtered = [h for h in self.history if h.get("type") == content_type]
        else:
            filtered = self.history
        
        # Return most recent first
        return filtered[-limit:][::-1]
    
    def get_gallery_items(self, limit: int = 20) -> List[tuple]:
        """
        Get image history as gallery items for Gradio Gallery component.
        
        Returns:
            List of (image_path, caption) tuples
        """
        items = []
        image_history = self.get_history("image", limit)
        
        for entry in image_history:
            try:
                path = Path(entry["path"])
                if path.exists():
                    caption = f"{entry['prompt'][:50]}... ({entry['model']})"
                    items.append((str(path), caption))
            except Exception as e:
                logger.error(f"Error loading gallery item: {e}")
        
        return items
    
    def clear_history(self, content_type: Optional[str] = None) -> int:
        """
        Clear generation history.
        
        Args:
            content_type: Clear only specific type, or None for all
            
        Returns:
            Number of entries cleared
        """
        if content_type:
            original_len = len(self.history)
            self.history = [h for h in self.history if h.get("type") != content_type]
            cleared = original_len - len(self.history)
        else:
            cleared = len(self.history)
            self.history = []
        
        self._save_history()
        logger.info(f"✓ Cleared {cleared} history entries")
        return cleared
    
    def get_stats(self) -> Dict[str, Any]:
        """Get generation statistics."""
        stats = {
            "total_generations": len(self.history),
            "images": len([h for h in self.history if h.get("type") == "image"]),
            "audio": len([h for h in self.history if h.get("type") == "audio"]),
            "videos": len([h for h in self.history if h.get("type") == "video"]),
            "output_dir": str(self.base_dir),
            "total_size_mb": self._get_directory_size_mb()
        }
        return stats
    
    def _get_directory_size_mb(self) -> float:
        """Calculate total size of output directory in MB."""
        total_size = 0
        for path in self.base_dir.rglob('*'):
            if path.is_file():
                total_size += path.stat().st_size
        return round(total_size / (1024 * 1024), 2)


# Global instance
_output_manager: Optional[OutputManager] = None


def get_output_manager() -> OutputManager:
    """Get or create global output manager instance."""
    global _output_manager
    if _output_manager is None:
        _output_manager = OutputManager()
    return _output_manager
