"""
Centralized error handling and logging for the application.
Provides graceful error messages and comprehensive logging.
"""

import logging
import sys
import traceback
from typing import Optional, Tuple

# Configure logging
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(log_file: str = "generator.log") -> logging.Logger:
    """Set up logging configuration with file and console handlers.
    
    Args:
        log_file: Path to log file
        
    Returns:
        Configured root logger
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Console handler (INFO level)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (DEBUG level)
    try:
        file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not set up file logging: {e}")

    return logger


class GeneratorException(Exception):
    """Base exception for generator errors."""

    def __init__(self, message: str, user_message: Optional[str] = None):
        """Initialize exception with technical and user-friendly messages.
        
        Args:
            message: Technical error message for logs
            user_message: User-friendly message for UI display
        """
        self.message = message
        self.user_message = user_message or message
        super().__init__(message)


class ModelLoadError(GeneratorException):
    """Raised when model loading fails."""

    pass


class InferenceError(GeneratorException):
    """Raised when inference fails."""

    pass


class VRAMError(GeneratorException):
    """Raised when insufficient VRAM is available."""

    pass


class ValidationError(GeneratorException):
    """Raised when input validation fails."""

    pass


def handle_generation_error(
    exception: Exception, logger: logging.Logger
) -> Tuple[None, str]:
    """Handle generation errors and return user-friendly message.
    
    Args:
        exception: The exception that occurred
        logger: Logger instance
        
    Returns:
        Tuple of (None, error_message_string)
    """
    logger.exception("Generation error occurred")

    # Map specific errors to user-friendly messages
    if isinstance(exception, GeneratorException):
        return None, f"❌ {exception.user_message}"

    elif "out of memory" in str(exception).lower():
        return (
            None,
            "❌ GPU out of memory. Try:\n"
            "  • Smaller model\n"
            "  • Lower resolution\n"
            "  • Fewer inference steps",
        )

    elif "model" in str(exception).lower():
        return (
            None,
            "❌ Error loading model. Check internet for download, then retry.",
        )

    elif "cuda" in str(exception).lower():
        return None, "❌ GPU error. Try restarting the app or using CPU mode."

    else:
        # Generic error with truncated traceback
        error_summary = str(exception)[:100]
        return None, f"❌ Unexpected error: {error_summary}"


def log_performance_metrics(
    logger: logging.Logger,
    operation: str,
    duration_seconds: float,
    output_size_mb: Optional[float] = None,
    vram_used_gb: Optional[float] = None,
) -> None:
    """Log performance metrics for an operation.
    
    Args:
        logger: Logger instance
        operation: Name of operation (e.g., "image_generation")
        duration_seconds: Time taken in seconds
        output_size_mb: Size of output in MB (optional)
        vram_used_gb: VRAM used in GB (optional)
    """
    msg = f"✓ {operation} completed in {duration_seconds:.2f}s"
    if output_size_mb:
        msg += f" | Output: {output_size_mb:.1f}MB"
    if vram_used_gb:
        msg += f" | VRAM: {vram_used_gb:.2f}GB"
    logger.info(msg)


def format_traceback() -> str:
    """Format current traceback for debugging.
    
    Returns:
        Formatted traceback string
    """
    return "".join(traceback.format_exc())
