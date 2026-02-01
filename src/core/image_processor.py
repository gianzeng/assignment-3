"""
Image Processing Core Module
Handles all OpenCV image processing operations

This module implements the ImageProcessor class which encapsulates
all image processing functionality using OpenCV.
"""

import cv2
import numpy as np
from typing import Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum


class RotationAngle(Enum):
    """Enumeration for rotation angles"""
    ROTATE_90 = cv2.ROTATE_90_CLOCKWISE
    ROTATE_180 = cv2.ROTATE_180
    ROTATE_270 = cv2.ROTATE_90_COUNTERCLOCKWISE


class FlipDirection(Enum):
    """Enumeration for flip directions"""
    HORIZONTAL = 0
    VERTICAL = 1
    BOTH = -1


@dataclass
class ImageMetadata:
    """Data class to store image metadata"""
    filename: str
    width: int
    height: int
    channels: int
    dtype: str

    def __str__(self) -> str:
        return f"{self.filename} - {self.width}x{self.height}px, {self.channels} channels"


class ImageProcessor:
    """
    Core image processing class that handles all OpenCV operations.

    This class encapsulates all image processing functionality and maintains
    the current image state. It implements all 8 required filters for the assignment.

    Attributes:
        _current_image: The current image being processed
        _original_image: The original loaded image (for reset operations)
        _metadata: Metadata about the current image
    """

    def __init__(self):
        """Initialize the ImageProcessor with empty state"""
        self._current_image: Optional[np.ndarray] = None
        self._original_image: Optional[np.ndarray] = None
        self._metadata: Optional[ImageMetadata] = None
        self._blur_intensity = 5  # Default blur kernel size

    @property
    def current_image(self) -> Optional[np.ndarray]:
        """Get the current image (read-only)"""
        return self._current_image

    @property
    def metadata(self) -> Optional[ImageMetadata]:
        """Get the current image metadata (read-only)"""
        return self._metadata

    @property
    def has_image(self) -> bool:
        """Check if an image is loaded"""
        return self._current_image is not None

    def load_image(self, filepath: str) -> bool:
        """
        Load an image from file

        Args:
            filepath: Path to the image file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Load image using OpenCV
            image = cv2.imread(filepath)
            if image is None:
                return False

            # Convert BGR to RGB for display
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Store the image and create metadata
            self._original_image = image.copy()
            self._current_image = image.copy()

            # Extract metadata
            height, width = image.shape[:2]
            channels = image.shape[2] if len(image.shape) > 2 else 1

            self._metadata = ImageMetadata(
                filename=filepath.split('/')[-1],
                width=width,
                height=height,
                channels=channels,
                dtype=str(image.dtype)
            )

            return True

        except Exception as e:
            print(f"Error loading image: {e}")
            return False

    def save_image(self, filepath: str) -> bool:
        """
        Save the current image to file

        Args:
            filepath: Path where to save the image

        Returns:
            True if successful, False otherwise
        """
        if not self.has_image:
            return False

        try:
            # Convert RGB back to BGR for OpenCV
            image_bgr = cv2.cvtColor(self._current_image, cv2.COLOR_RGB2BGR)
            success = cv2.imwrite(filepath, image_bgr)
            return success

        except Exception as e:
            print(f"Error saving image: {e}")
            return False

    def reset_image(self) -> bool:
        """Reset the current image to the original"""
        if self._original_image is not None:
            self._current_image = self._original_image.copy()
            return True
        return False

    def get_image_for_display(self) -> Optional[np.ndarray]:
        """Get the current image ready for display in GUI"""
        return self._current_image

    # === Image Processing Filters (All 8 Required) ===

    def apply_grayscale(self) -> bool:
        """
        Filter 1: Convert image to grayscale (black and white)

        Returns:
            True if successful, False otherwise
        """
        if not self.has_image:
            return False

        try:
            # Convert to grayscale
            gray = cv2.cvtColor(self._current_image, cv2.COLOR_RGB2GRAY)
            # Convert back to RGB format for consistent display
            self._current_image = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
            return True

        except Exception as e:
            print(f"Error applying grayscale: {e}")
            return False

    def apply_blur(self, intensity: int = None) -> bool:
        """
        Filter 2: Apply Gaussian blur with adjustable intensity

        Args:
            intensity: Kernel size for blur (must be odd number)

        Returns:
            True if successful, False otherwise
        """
        if not self.has_image:
            return False

        if intensity is None:
            intensity = self._blur_intensity
        else:
            self._blur_intensity = intensity

        # Ensure intensity is odd and at least 1
        if intensity % 2 == 0:
            intensity += 1
        intensity = max(1, intensity)

        try:
            self._current_image = cv2.GaussianBlur(
                self._current_image,
                (intensity, intensity),
                0
            )
            return True

        except Exception as e:
            print(f"Error applying blur: {e}")
            return False

    def apply_edge_detection(self, low_threshold: int = 50, high_threshold: int = 150) -> bool:
        """
        Filter 3: Apply Canny edge detection algorithm

        Args:
            low_threshold: Lower threshold for edge detection
            high_threshold: Upper threshold for edge detection

        Returns:
            True if successful, False otherwise
        """
        if not self.has_image:
            return False

        try:
            # Convert to grayscale first for edge detection
            gray = cv2.cvtColor(self._current_image, cv2.COLOR_RGB2GRAY)

            # Apply Canny edge detection
            edges = cv2.Canny(gray, low_threshold, high_threshold)

            # Convert back to RGB format
            self._current_image = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
            return True

        except Exception as e:
            print(f"Error applying edge detection: {e}")
            return False

    def adjust_brightness(self, value: int) -> bool:
        """
        Filter 4: Adjust image brightness

        Args:
            value: Brightness adjustment (-100 to +100)

        Returns:
            True if successful, False otherwise
        """
        if not self.has_image:
            return False

        try:
            # Ensure value is within reasonable range
            value = max(-100, min(100, value))

            # Adjust brightness by adding/subtracting value
            if value >= 0:
                self._current_image = cv2.add(self._current_image, value)
            else:
                self._current_image = cv2.subtract(self._current_image, abs(value))

            return True

        except Exception as e:
            print(f"Error adjusting brightness: {e}")
            return False

    def adjust_contrast(self, value: float) -> bool:
        """
        Filter 5: Adjust image contrast

        Args:
            value: Contrast multiplier (0.5 to 3.0, where 1.0 is original)

        Returns:
            True if successful, False otherwise
        """
        if not self.has_image:
            return False

        try:
            # Ensure value is within reasonable range
            value = max(0.5, min(3.0, value))

            # Apply contrast adjustment
            self._current_image = cv2.convertScaleAbs(
                self._current_image,
                alpha=value,
                beta=0
            )
            return True

        except Exception as e:
            print(f"Error adjusting contrast: {e}")
            return False

    def rotate_image(self, angle: RotationAngle) -> bool:
        """
        Filter 6: Rotate image by 90°, 180°, or 270°

        Args:
            angle: Rotation angle from RotationAngle enum

        Returns:
            True if successful, False otherwise
        """
        if not self.has_image:
            return False

        try:
            self._current_image = cv2.rotate(self._current_image, angle.value)

            # Update metadata after rotation
            if self._metadata:
                height, width = self._current_image.shape[:2]
                self._metadata.width = width
                self._metadata.height = height

            return True

        except Exception as e:
            print(f"Error rotating image: {e}")
            return False

    def flip_image(self, direction: FlipDirection) -> bool:
        """
        Filter 7: Flip image horizontally or vertically

        Args:
            direction: Flip direction from FlipDirection enum

        Returns:
            True if successful, False otherwise
        """
        if not self.has_image:
            return False

        try:
            self._current_image = cv2.flip(self._current_image, direction.value)
            return True

        except Exception as e:
            print(f"Error flipping image: {e}")
            return False

    def resize_image(self, width: int, height: int, maintain_aspect: bool = True) -> bool:
        """
        Filter 8: Resize/scale the image

        Args:
            width: Target width in pixels
            height: Target height in pixels
            maintain_aspect: Whether to maintain aspect ratio

        Returns:
            True if successful, False otherwise
        """
        if not self.has_image:
            return False

        try:
            if maintain_aspect:
                # Calculate the aspect ratio
                current_h, current_w = self._current_image.shape[:2]
                aspect_ratio = current_w / current_h

                # Adjust dimensions to maintain aspect ratio
                if width / height > aspect_ratio:
                    width = int(height * aspect_ratio)
                else:
                    height = int(width / aspect_ratio)

            # Resize the image
            self._current_image = cv2.resize(
                self._current_image,
                (width, height),
                interpolation=cv2.INTER_AREA
            )

            # Update metadata
            if self._metadata:
                self._metadata.width = width
                self._metadata.height = height

            return True

        except Exception as e:
            print(f"Error resizing image: {e}")
            return False

    def get_image_copy(self) -> Optional[np.ndarray]:
        """Get a copy of the current image for undo/redo operations"""
        if self.has_image:
            return self._current_image.copy()
        return None

    def set_image(self, image: np.ndarray) -> None:
        """Set the current image (used for undo/redo)"""
        self._current_image = image.copy()

        # Update metadata
        if image is not None:
            height, width = image.shape[:2]
            channels = image.shape[2] if len(image.shape) > 2 else 1

            if self._metadata:
                self._metadata.width = width
                self._metadata.height = height
                self._metadata.channels = channels