"""
Control Panel GUI Module
Implements the side control panel with filter buttons and sliders

This module contains the ControlPanel class which provides
the user interface for applying filters and adjustments.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict, Any


class ControlPanel(ttk.LabelFrame):
    """
    Control panel widget for image editing controls

    This class creates a side panel with buttons and sliders
    for applying various image filters and adjustments.

    Attributes:
        parent_app: Reference to the main application
        sliders: Dictionary of slider widgets
        buttons: Dictionary of button widgets
    """

    def __init__(self, parent: tk.Widget, parent_app: Any):
        """
        Initialize the Control Panel

        Args:
            parent: Parent widget
            parent_app: Reference to main application (ImageEditorApp)
        """
        super().__init__(parent, text="Controls", padding=10)
        self.parent_app = parent_app

        # State tracking
        self.controls_enabled = False

        # Widget references
        self.sliders: Dict[str, ttk.Scale] = {}
        self.buttons: Dict[str, ttk.Button] = {}
        self.entries: Dict[str, ttk.Entry] = {}

        # Initialize label attributes
        self.blur_value_label = None
        self.brightness_value_label = None
        self.contrast_value_label = None

        # Resize aspect ratio tracking
        self.current_aspect_ratio = 1.0
        self._updating_size = False

        # Create the control sections
        self._create_filter_section()
        self._create_adjustment_section()
        self._create_transform_section()
        self._create_resize_section()

        # Initially disable all controls
        self.disable_controls()

    def _create_filter_section(self) -> None:
        """Create the filter buttons section"""
        # Filter section frame
        filter_frame = ttk.LabelFrame(self, text="Filters", padding=5)
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        # Grayscale button
        self.buttons['grayscale'] = ttk.Button(
            filter_frame,
            text="Grayscale",
            command=lambda: self.parent_app.apply_filter("grayscale")
        )
        self.buttons['grayscale'].pack(fill=tk.X, pady=2)

        # Edge Detection button
        self.buttons['edge'] = ttk.Button(
            filter_frame,
            text="Edge Detection",
            command=lambda: self.parent_app.apply_filter("edge_detection")
        )
        self.buttons['edge'].pack(fill=tk.X, pady=2)

        # Blur section with slider
        blur_container = ttk.Frame(filter_frame)
        blur_container.pack(fill=tk.X, pady=5)

        ttk.Label(blur_container, text="Blur Intensity:").pack(anchor=tk.W)

        # Blur intensity slider
        blur_slider_frame = ttk.Frame(blur_container)
        blur_slider_frame.pack(fill=tk.X)

        self.sliders['blur'] = ttk.Scale(
            blur_slider_frame,
            from_=1,
            to=31,
            orient=tk.HORIZONTAL,
            command=self._on_blur_change
        )
        self.sliders['blur'].set(5)
        self.sliders['blur'].pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.blur_value_label = ttk.Label(blur_slider_frame, text="5")
        self.blur_value_label.pack(side=tk.RIGHT, padx=(5, 0))

        # Blur apply button
        self.buttons['blur'] = ttk.Button(
            blur_container,
            text="Apply Blur",
            command=self._apply_blur
        )
        self.buttons['blur'].pack(fill=tk.X, pady=(5, 0))

    def _create_adjustment_section(self) -> None:
        """Create the adjustment sliders section"""
        # Adjustment section frame
        adjust_frame = ttk.LabelFrame(self, text="Adjustments", padding=5)
        adjust_frame.pack(fill=tk.X, pady=(0, 10))

        # Brightness adjustment
        brightness_container = ttk.Frame(adjust_frame)
        brightness_container.pack(fill=tk.X, pady=5)

        ttk.Label(brightness_container, text="Brightness:").pack(anchor=tk.W)

        brightness_slider_frame = ttk.Frame(brightness_container)
        brightness_slider_frame.pack(fill=tk.X)

        self.sliders['brightness'] = ttk.Scale(
            brightness_slider_frame,
            from_=-100,
            to=100,
            orient=tk.HORIZONTAL,
            command=self._on_brightness_change
        )
        self.sliders['brightness'].set(0)
        self.sliders['brightness'].pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.brightness_value_label = ttk.Label(brightness_slider_frame, text="0")
        self.brightness_value_label.pack(side=tk.RIGHT, padx=(5, 0))

        self.buttons['brightness'] = ttk.Button(
            brightness_container,
            text="Apply Brightness",
            command=self._apply_brightness
        )
        self.buttons['brightness'].pack(fill=tk.X, pady=(5, 0))

        # Contrast adjustment
        contrast_container = ttk.Frame(adjust_frame)
        contrast_container.pack(fill=tk.X, pady=5)

        ttk.Label(contrast_container, text="Contrast:").pack(anchor=tk.W)

        contrast_slider_frame = ttk.Frame(contrast_container)
        contrast_slider_frame.pack(fill=tk.X)

        self.sliders['contrast'] = ttk.Scale(
            contrast_slider_frame,
            from_=0.5,
            to=3.0,
            orient=tk.HORIZONTAL,
            command=self._on_contrast_change
        )
        self.sliders['contrast'].set(1.0)
        self.sliders['contrast'].pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.contrast_value_label = ttk.Label(contrast_slider_frame, text="1.0")
        self.contrast_value_label.pack(side=tk.RIGHT, padx=(5, 0))

        self.buttons['contrast'] = ttk.Button(
            contrast_container,
            text="Apply Contrast",
            command=self._apply_contrast
        )
        self.buttons['contrast'].pack(fill=tk.X, pady=(5, 0))

    def _create_transform_section(self) -> None:
        """Create the transform buttons section"""
        # Transform section frame
        transform_frame = ttk.LabelFrame(self, text="Transform", padding=5)
        transform_frame.pack(fill=tk.X, pady=(0, 10))

        # Rotation buttons frame
        rotate_frame = ttk.Frame(transform_frame)
        rotate_frame.pack(fill=tk.X, pady=2)

        ttk.Label(rotate_frame, text="Rotate:").pack(anchor=tk.W)

        rotate_buttons = ttk.Frame(rotate_frame)
        rotate_buttons.pack(fill=tk.X)

        self.buttons['rotate_90'] = ttk.Button(
            rotate_buttons,
            text="90°",
            width=7,
            command=lambda: self.parent_app.apply_filter("rotate_90")
        )
        self.buttons['rotate_90'].pack(side=tk.LEFT, padx=1, fill=tk.X, expand=True)

        self.buttons['rotate_180'] = ttk.Button(
            rotate_buttons,
            text="180°",
            width=7,
            command=lambda: self.parent_app.apply_filter("rotate_180")
        )
        self.buttons['rotate_180'].pack(side=tk.LEFT, padx=1, fill=tk.X, expand=True)

        self.buttons['rotate_270'] = ttk.Button(
            rotate_buttons,
            text="270°",
            width=7,
            command=lambda: self.parent_app.apply_filter("rotate_270")
        )
        self.buttons['rotate_270'].pack(side=tk.LEFT, padx=1, fill=tk.X, expand=True)

        # Flip buttons frame
        flip_frame = ttk.Frame(transform_frame)
        flip_frame.pack(fill=tk.X, pady=(10, 2))

        ttk.Label(flip_frame, text="Flip:").pack(anchor=tk.W)

        flip_buttons = ttk.Frame(flip_frame)
        flip_buttons.pack(fill=tk.X)

        self.buttons['flip_h'] = ttk.Button(
            flip_buttons,
            text="Horizontal",
            command=lambda: self.parent_app.apply_filter("flip_horizontal")
        )
        self.buttons['flip_h'].pack(side=tk.LEFT, padx=1, fill=tk.X, expand=True)

        self.buttons['flip_v'] = ttk.Button(
            flip_buttons,
            text="Vertical",
            command=lambda: self.parent_app.apply_filter("flip_vertical")
        )
        self.buttons['flip_v'].pack(side=tk.LEFT, padx=1, fill=tk.X, expand=True)

    def _create_resize_section(self) -> None:
        """Create the resize controls section"""
        # Resize section frame
        resize_frame = ttk.LabelFrame(self, text="Resize", padding=5)
        resize_frame.pack(fill=tk.X, pady=(0, 10))

        # Width input
        width_frame = ttk.Frame(resize_frame)
        width_frame.pack(fill=tk.X, pady=2)

        ttk.Label(width_frame, text="Width:").pack(side=tk.LEFT)
        self.entries['width'] = ttk.Entry(width_frame, width=10)
        self.entries['width'].pack(side=tk.LEFT, padx=(5, 0))
        self.entries['width'].insert(0, "800")
        self.entries['width'].bind('<KeyRelease>', lambda e: self._on_width_change())

        # Height input
        height_frame = ttk.Frame(resize_frame)
        height_frame.pack(fill=tk.X, pady=2)

        ttk.Label(height_frame, text="Height:").pack(side=tk.LEFT)
        self.entries['height'] = ttk.Entry(height_frame, width=10)
        self.entries['height'].pack(side=tk.LEFT, padx=(5, 0))
        self.entries['height'].insert(0, "600")
        self.entries['height'].bind('<KeyRelease>', lambda e: self._on_height_change())

        # Get current size button
        self.buttons['get_size'] = ttk.Button(
            resize_frame,
            text="Get Current Size",
            command=self._get_current_size
        )
        self.buttons['get_size'].pack(fill=tk.X, pady=(5, 5))

        # Maintain aspect ratio checkbox
        self.maintain_aspect_var = tk.BooleanVar(value=True)
        self.maintain_aspect_check = ttk.Checkbutton(
            resize_frame,
            text="Maintain Aspect Ratio",
            variable=self.maintain_aspect_var
        )
        self.maintain_aspect_check.pack(fill=tk.X, pady=5)

        # Apply resize button
        self.buttons['resize'] = ttk.Button(
            resize_frame,
            text="Apply Resize",
            command=self._apply_resize
        )
        self.buttons['resize'].pack(fill=tk.X)

    # === Slider Callbacks ===

    def _on_blur_change(self, value: str) -> None:
        """Update blur intensity label"""
        int_value = int(float(value))
        # Ensure odd number for blur kernel
        if int_value % 2 == 0:
            int_value += 1
            self.sliders['blur'].set(int_value)
        if self.blur_value_label:
            self.blur_value_label.config(text=str(int_value))

    def _on_brightness_change(self, value: str) -> None:
        """Update brightness label"""
        int_value = int(float(value))
        if self.brightness_value_label:
            self.brightness_value_label.config(text=str(int_value))

    def _on_contrast_change(self, value: str) -> None:
        """Update contrast label"""
        float_value = float(value)
        if self.contrast_value_label:
            self.contrast_value_label.config(text=f"{float_value:.1f}")

    # === Apply Filter Methods ===

    def _apply_blur(self) -> None:
        """Apply blur with current slider value"""
        intensity = int(self.sliders['blur'].get())
        if intensity % 2 == 0:
            intensity += 1
        self.parent_app.apply_filter("blur", intensity=intensity)

    def _apply_brightness(self) -> None:
        """Apply brightness adjustment"""
        value = int(self.sliders['brightness'].get())
        self.parent_app.apply_filter("brightness", value=value)

    def _apply_contrast(self) -> None:
        """Apply contrast adjustment"""
        value = float(self.sliders['contrast'].get())
        self.parent_app.apply_filter("contrast", value=value)

    def _apply_resize(self) -> None:
        """Apply resize with specified dimensions"""
        try:
            width = int(self.entries['width'].get())
            height = int(self.entries['height'].get())

            if width <= 0 or height <= 0:
                messagebox.showerror("Invalid Input", "Width and height must be positive numbers.")
                return

            maintain_aspect = self.maintain_aspect_var.get()
            self.parent_app.apply_filter("resize", width=width, height=height,
                                        maintain_aspect=maintain_aspect)

        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for width and height.")

    def _get_current_size(self) -> None:
        """Get and display the current image dimensions"""
        if self.parent_app.image_processor.has_image:
            metadata = self.parent_app.image_processor.metadata
            if metadata:
                self.entries['width'].delete(0, tk.END)
                self.entries['width'].insert(0, str(metadata.width))
                self.entries['height'].delete(0, tk.END)
                self.entries['height'].insert(0, str(metadata.height))
                # Update aspect ratio
                self.current_aspect_ratio = metadata.width / metadata.height
        else:
            messagebox.showinfo("No Image", "Please load an image first.")

    def _on_width_change(self) -> None:
        """Handle width input change - auto-calculate height if aspect ratio is locked"""
        if self._updating_size or not self.maintain_aspect_var.get():
            return

        try:
            width = int(self.entries['width'].get())
            if width > 0 and self.current_aspect_ratio > 0:
                self._updating_size = True
                new_height = int(width / self.current_aspect_ratio)
                self.entries['height'].delete(0, tk.END)
                self.entries['height'].insert(0, str(new_height))
                self._updating_size = False
        except (ValueError, tk.TclError):
            pass

    def _on_height_change(self) -> None:
        """Handle height input change - auto-calculate width if aspect ratio is locked"""
        if self._updating_size or not self.maintain_aspect_var.get():
            return

        try:
            height = int(self.entries['height'].get())
            if height > 0 and self.current_aspect_ratio > 0:
                self._updating_size = True
                new_width = int(height * self.current_aspect_ratio)
                self.entries['width'].delete(0, tk.END)
                self.entries['width'].insert(0, str(new_width))
                self._updating_size = False
        except (ValueError, tk.TclError):
            pass

    # === Control State Management ===

    def enable_controls(self) -> None:
        """Enable all controls when image is loaded"""
        self.controls_enabled = True

        # Enable all buttons
        for button in self.buttons.values():
            button.config(state=tk.NORMAL)

        # Enable all sliders
        for slider in self.sliders.values():
            slider.config(state=tk.NORMAL)

        # Enable all entries
        for entry in self.entries.values():
            entry.config(state=tk.NORMAL)

        # Enable checkbox
        if hasattr(self, 'maintain_aspect_check'):
            self.maintain_aspect_check.config(state=tk.NORMAL)

    def disable_controls(self) -> None:
        """Disable all controls when no image is loaded"""
        self.controls_enabled = False

        # Disable all buttons
        for button in self.buttons.values():
            button.config(state=tk.DISABLED)

        # Disable all sliders
        for slider in self.sliders.values():
            slider.config(state=tk.DISABLED)

        # Disable all entries
        for entry in self.entries.values():
            entry.config(state=tk.DISABLED)

        # Disable checkbox
        if hasattr(self, 'maintain_aspect_check'):
            self.maintain_aspect_check.config(state=tk.DISABLED)

    def reset_controls(self) -> None:
        """Reset all controls to default values"""
        self.sliders['blur'].set(5)
        self.sliders['brightness'].set(0)
        self.sliders['contrast'].set(1.0)
        self.entries['width'].delete(0, tk.END)
        self.entries['width'].insert(0, "800")
        self.entries['height'].delete(0, tk.END)
        self.entries['height'].insert(0, "600")
        self.maintain_aspect_var.set(True)