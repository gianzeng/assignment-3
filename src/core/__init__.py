"""
Core package containing image processing and history management modules
"""

from .image_processor import ImageProcessor, RotationAngle, FlipDirection, ImageMetadata
from .history_manager import HistoryManager

__all__ = [
    'ImageProcessor',
    'RotationAngle',
    'FlipDirection',
    'ImageMetadata',
    'HistoryManager'
]