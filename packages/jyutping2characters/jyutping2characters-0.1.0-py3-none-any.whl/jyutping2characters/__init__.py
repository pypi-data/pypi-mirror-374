"""
Jyutping Transcriber - Convert Jyutping romanization to Traditional Chinese characters.

This package provides a high-performance transcriber that uses dynamic programming
to find the most probable sequence of Chinese characters for a given Jyutping input.
"""

import logging
import threading
from typing import Optional

from .transcriber import JyutpingTranscriber
from .data_builder import ensure_data_available, clear_cached_data

# Set up logging for the package
logger = logging.getLogger(__name__)

__version__ = "0.1.0"
__all__ = ["transcribe", "warmup", "clear_cache", "JyutpingTranscriber"]

# Global singleton instance for performance optimization
_transcriber_instance: Optional[JyutpingTranscriber] = None
_transcriber_lock = threading.Lock()


def _get_global_transcriber() -> JyutpingTranscriber:
    """
    Get or create the global transcriber instance (thread-safe).
    
    This function implements the singleton pattern to avoid the 1-second
    initialization cost on every transcription call.
    """
    global _transcriber_instance
    
    if _transcriber_instance is None:
        with _transcriber_lock:
            # Double-check locking pattern
            if _transcriber_instance is None:
                logger.info("Initializing Jyutping transcriber")
                try:
                    data_path = ensure_data_available()
                    _transcriber_instance = JyutpingTranscriber.from_file(data_path)
                    logger.info("Transcriber initialized successfully")
                except Exception as e:
                    logger.error(f"Failed to initialize transcriber: {e}")
                    raise
    
    return _transcriber_instance


def transcribe(text: str) -> str:
    """
    Transcribe Jyutping romanization to Chinese characters.
    
    This function uses a global transcriber instance for optimal performance.
    The first call may take 1-2 minutes to download and process data, but
    subsequent calls are instant.
    
    Args:
        text: Jyutping romanization string (e.g., "ngo5oi3nei5")
        
    Returns:
        Traditional Chinese characters (e.g., "我愛你")
        
    Example:
        >>> from jyutping_transcriber import transcribe
        >>> transcribe("ngo5oi3nei5")
        '我愛你'
        >>> transcribe("gam1jat6")
        '今日'
    """
    if not text:
        return ""
    
    return _get_global_transcriber().transcribe(text)


def warmup() -> None:
    """
    Pre-initialize the global transcriber instance.
    
    Call this function to ensure the transcriber is ready for use,
    which will download and process data if needed. This is useful
    if you want to handle the initialization time explicitly.
    
    Example:
        >>> from jyutping_transcriber import warmup, transcribe
        >>> warmup()  # Takes 1-2 minutes on first run
        >>> result = transcribe("gam1jat6")  # Instant
    """
    _get_global_transcriber()


def clear_cache() -> None:
    """
    Clear cached mapping data and reset the global transcriber instance.
    
    After calling this function, the next transcription will rebuild
    the data from online sources.
    
    Example:
        >>> from jyutping_transcriber import clear_cache, transcribe
        >>> clear_cache()
        >>> transcribe("gam1jat6")  # Will rebuild data first
    """
    global _transcriber_instance
    _transcriber_instance = None
    clear_cached_data()


# For backwards compatibility and advanced usage
__doc__ += """

Advanced Usage:
    For custom data or multiple transcriber instances:
    
    >>> from jyutping_transcriber import JyutpingTranscriber
    >>> custom_data = [("你好", "neihou", 1000), ("好", "hou", 500)]
    >>> transcriber = JyutpingTranscriber(custom_data)
    >>> result = transcriber.transcribe("neihou")
"""
