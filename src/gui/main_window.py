"""
Main Window GUI Module
Implements the main application window using Tkinter

This module contains the ImageEditorApp class which creates and manages
the main GUI window with all required UI elements.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Menu
from PIL import Image, ImageTk
import numpy as np
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.image_processor import ImageProcessor, RotationAngle, FlipDirection
from core.history_manager import HistoryManager
from gui.control_panel import ControlPanel


class ImageEditorApp:
    """
    Main application class for the Image Editor

    This class manages the main window and coordinates between
    the image processor, history manager, and UI components.

    Attributes:
        root: The main tkinter window
        image_processor: Core image processing engine
        history_manager: Manages undo/redo functionality
        control_panel: Side panel with editing controls
    """

    def __init__(self, root: tk.Tk):
        """
        Initialize the Image Editor Application

        Args:
            root: The main tkinter window
        """
        self.root = root
        self.image_processor = ImageProcessor()
        self.history_manager = HistoryManager()
        self.control_panel = None

        # Configure main window
        self._setup_window()

        # Create UI components
        self._create_menu_bar()
        self._create_main_layout()
        self._create_status_bar()

        # Initialize state
        self.current_file_path = None
        self.is_modified = False

        # Bind keyboard shortcuts
        self._setup_shortcuts()

    def _setup_window(self) -> None:
        """Configure the main window properties"""
        self.root.title("Image Editor - HIT137 Assignment 3")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)

        # Configure window icon (if available)
        try:
            # self.root.iconbitmap('assets/icon.ico')
            pass
        except:
            pass

        # Configure grid weights for responsive layout
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _create_menu_bar(self) -> None:
        """Create the application menu bar with File and Edit menus"""
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        # File Menu
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)

        file_menu.add_command(label="Open...", command=self._open_image,
                            accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=self._save_image,
                            accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self._save_image_as,
                            accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing,
                            accelerator="Alt+F4")

        # Edit Menu
        edit_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        edit_menu.add_command(label="Undo", command=self._undo_action,
                            accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self._redo_action,
                            accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Reset Image", command=self._reset_image)

        # View Menu
        view_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)

        view_menu.add_command(label="Zoom In", command=self._zoom_in,
                            accelerator="Ctrl++")
        view_menu.add_command(label="Zoom Out", command=self._zoom_out,
                            accelerator="Ctrl+-")
        view_menu.add_command(label="Fit to Window", command=self._fit_to_window,
                            accelerator="Ctrl+0")

        # Help Menu
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)

        help_menu.add_command(label="About", command=self._show_about)
        help_menu.add_command(label="Keyboard Shortcuts", command=self._show_shortcuts)

    def _create_main_layout(self) -> None:
        """Create the main layout with image display and control panel"""
        # Create main container frame
        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Configure grid weights
        main_frame.grid_columnconfigure(0, weight=3)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # Create image display area
        self._create_image_display(main_frame)

        # Create control panel
        self._create_control_panel(main_frame)

    def _create_image_display(self, parent: ttk.Frame) -> None:
        """Create the image display area with canvas"""
        # Frame for image display
        display_frame = ttk.LabelFrame(parent, text="Image Display", padding=10)
        display_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        # Create canvas with scrollbars
        canvas_frame = ttk.Frame(display_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas for image display
        self.canvas = tk.Canvas(canvas_frame, bg='gray20')
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL,
                                   command=self.canvas.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        h_scrollbar = ttk.Scrollbar(display_frame, orient=tk.HORIZONTAL,
                                   command=self.canvas.xview)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Configure canvas scrolling
        self.canvas.configure(
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )

        # Image placeholder
        self.canvas_image = None
        self.photo_image = None

        # Display welcome message
        self.canvas.create_text(
            400, 300,
            text="Open an image to start editing\n(File → Open or Ctrl+O)",
            fill="white",
            font=("Arial", 14),
            tag="welcome"
        )

    def _create_control_panel(self, parent: ttk.Frame) -> None:
        """Create the control panel with filter buttons and sliders"""
        from gui.control_panel import ControlPanel

        # Create a frame to hold the canvas and scrollbar
        control_container = ttk.Frame(parent)
        control_container.grid(row=0, column=1, sticky="nsew")
        control_container.grid_rowconfigure(0, weight=1)
        control_container.grid_columnconfigure(0, weight=1)

        # Create canvas for scrolling
        control_canvas = tk.Canvas(control_container, highlightthickness=0)
        control_canvas.grid(row=0, column=0, sticky="nsew")

        # Add scrollbar
        scrollbar = ttk.Scrollbar(control_container, orient="vertical", command=control_canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        control_canvas.configure(yscrollcommand=scrollbar.set)

        # Create control panel inside canvas
        self.control_panel = ControlPanel(control_canvas, self)
        canvas_window = control_canvas.create_window((0, 0), window=self.control_panel, anchor="nw")

        # Configure scrolling
        def _configure_scroll_region(event=None):
            control_canvas.configure(scrollregion=control_canvas.bbox("all"))
            # Also update the window width to match canvas width
            canvas_width = control_canvas.winfo_width()
            control_canvas.itemconfig(canvas_window, width=canvas_width)

        self.control_panel.bind("<Configure>", _configure_scroll_region)
        control_canvas.bind("<Configure>", _configure_scroll_region)

        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            control_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        control_canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def _create_status_bar(self) -> None:
        """Create the status bar at the bottom of the window"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.grid(row=2, column=0, sticky="ew", padx=5, pady=(0, 5))

        # Status label
        self.status_label = ttk.Label(
            self.status_bar,
            text="Ready",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Image info label
        self.info_label = ttk.Label(
            self.status_bar,
            text="No image loaded",
            relief=tk.SUNKEN,
            anchor=tk.E
        )
        self.info_label.pack(side=tk.RIGHT, fill=tk.X, padx=(5, 0))

    def _setup_shortcuts(self) -> None:
        """Setup keyboard shortcuts"""
        self.root.bind('<Control-o>', lambda e: self._open_image())
        self.root.bind('<Control-s>', lambda e: self._save_image())
        self.root.bind('<Control-Shift-S>', lambda e: self._save_image_as())
        self.root.bind('<Control-z>', lambda e: self._undo_action())
        self.root.bind('<Control-y>', lambda e: self._redo_action())
        self.root.bind('<Control-plus>', lambda e: self._zoom_in())
        self.root.bind('<Control-minus>', lambda e: self._zoom_out())
        self.root.bind('<Control-0>', lambda e: self._fit_to_window())

    # === File Operations ===

    def _open_image(self) -> None:
        """Open an image file"""
        file_path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("PNG files", "*.png"),
                ("BMP files", "*.bmp"),
                ("All files", "*.*")
            ]
        )

        if file_path:
            if self.image_processor.load_image(file_path):
                self.current_file_path = file_path
                self.is_modified = False

                # Initialize history with the loaded image
                self.history_manager.initialize_state(
                    self.image_processor.get_image_copy()
                )

                # Update display
                self._update_image_display()
                self._update_status(f"Loaded: {os.path.basename(file_path)}")

                # Enable controls and auto-fill resize dimensions
                if self.control_panel:
                    self.control_panel.enable_controls()
                    self.control_panel._get_current_size()  # Auto-fill image dimensions
            else:
                messagebox.showerror("Error", "Failed to load image file.")

    def _save_image(self) -> None:
        """Save the current image"""
        if not self.image_processor.has_image:
            messagebox.showwarning("Warning", "No image to save.")
            return

        if self.current_file_path:
            if self.image_processor.save_image(self.current_file_path):
                self.is_modified = False
                self._update_status(f"Saved: {os.path.basename(self.current_file_path)}")
            else:
                messagebox.showerror("Error", "Failed to save image.")
        else:
            self._save_image_as()

    def _save_image_as(self) -> None:
        """Save the current image with a new name"""
        if not self.image_processor.has_image:
            messagebox.showwarning("Warning", "No image to save.")
            return

        file_path = filedialog.asksaveasfilename(
            title="Save Image As",
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("BMP files", "*.bmp"),
                ("All files", "*.*")
            ]
        )

        if file_path:
            if self.image_processor.save_image(file_path):
                self.current_file_path = file_path
                self.is_modified = False
                self._update_status(f"Saved as: {os.path.basename(file_path)}")
            else:
                messagebox.showerror("Error", "Failed to save image.")

    # === Edit Operations ===

    def _undo_action(self) -> None:
        """Undo the last action"""
        if self.history_manager.can_undo:
            image = self.history_manager.undo()
            if image is not None:
                self.image_processor.set_image(image)
                self._update_image_display()
                self._update_status("Undo performed")

    def _redo_action(self) -> None:
        """Redo the last undone action"""
        if self.history_manager.can_redo:
            image = self.history_manager.redo()
            if image is not None:
                self.image_processor.set_image(image)
                self._update_image_display()
                self._update_status("Redo performed")

    def _reset_image(self) -> None:
        """Reset image to original state"""
        if self.image_processor.has_image:
            response = messagebox.askyesno(
                "Reset Image",
                "Are you sure you want to reset the image to its original state?"
            )
            if response:
                # Save current state before reset
                self._save_state_to_history()

                if self.image_processor.reset_image():
                    self._update_image_display()
                    self._update_status("Image reset to original")

    # === View Operations ===

    def _zoom_in(self) -> None:
        """Zoom in the image display"""
        # Implementation for zoom in
        self._update_status("Zoom in")

    def _zoom_out(self) -> None:
        """Zoom out the image display"""
        # Implementation for zoom out
        self._update_status("Zoom out")

    def _fit_to_window(self) -> None:
        """Fit image to window size"""
        # Implementation for fit to window
        self._update_status("Fit to window")

    # === Image Processing Operations ===

    def apply_filter(self, filter_name: str, **kwargs) -> None:
        """
        Apply a filter to the image

        Args:
            filter_name: Name of the filter to apply
            **kwargs: Additional parameters for the filter
        """
        if not self.image_processor.has_image:
            messagebox.showwarning("Warning", "No image loaded.")
            return

        # Save current state to history before applying filter
        self._save_state_to_history()

        success = False

        # Apply the requested filter
        if filter_name == "grayscale":
            success = self.image_processor.apply_grayscale()
        elif filter_name == "blur":
            intensity = kwargs.get('intensity', 5)
            success = self.image_processor.apply_blur(intensity)
        elif filter_name == "edge_detection":
            success = self.image_processor.apply_edge_detection()
        elif filter_name == "brightness":
            value = kwargs.get('value', 0)
            success = self.image_processor.adjust_brightness(value)
        elif filter_name == "contrast":
            value = kwargs.get('value', 1.0)
            success = self.image_processor.adjust_contrast(value)
        elif filter_name == "rotate_90":
            success = self.image_processor.rotate_image(RotationAngle.ROTATE_90)
        elif filter_name == "rotate_180":
            success = self.image_processor.rotate_image(RotationAngle.ROTATE_180)
        elif filter_name == "rotate_270":
            success = self.image_processor.rotate_image(RotationAngle.ROTATE_270)
        elif filter_name == "flip_horizontal":
            success = self.image_processor.flip_image(FlipDirection.HORIZONTAL)
        elif filter_name == "flip_vertical":
            success = self.image_processor.flip_image(FlipDirection.VERTICAL)
        elif filter_name == "resize":
            width = kwargs.get('width', 800)
            height = kwargs.get('height', 600)
            maintain_aspect = kwargs.get('maintain_aspect', True)
            success = self.image_processor.resize_image(width, height, maintain_aspect)

        if success:
            self.is_modified = True
            self._update_image_display()
            self._update_status(f"Applied: {filter_name}")

            # Auto-update resize dimensions for filters that change image size
            if filter_name in ["rotate_90", "rotate_180", "rotate_270", "resize"]:
                if self.control_panel:
                    self.control_panel._get_current_size()
        else:
            # Restore previous state if filter failed
            self.history_manager.undo()
            messagebox.showerror("Error", f"Failed to apply {filter_name} filter.")

    # === Helper Methods ===

    def _save_state_to_history(self) -> None:
        """Save current image state to history"""
        if self.image_processor.has_image:
            self.history_manager.add_state(self.image_processor.get_image_copy())

    def _update_image_display(self) -> None:
        """Update the canvas with the current image"""
        if not self.image_processor.has_image:
            return

        # Get the image from processor
        cv_image = self.image_processor.get_image_for_display()
        if cv_image is None:
            return

        # Convert to PIL Image
        pil_image = Image.fromarray(cv_image)

        # Get canvas size for scaling
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width > 1 and canvas_height > 1:
            # Calculate scale to fit image in canvas
            img_width, img_height = pil_image.size
            scale_x = canvas_width / img_width
            scale_y = canvas_height / img_height
            scale = min(scale_x, scale_y, 1.0)  # Don't upscale

            if scale < 1.0:
                new_width = int(img_width * scale)
                new_height = int(img_height * scale)
                pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Convert to PhotoImage
        self.photo_image = ImageTk.PhotoImage(pil_image)

        # Clear canvas
        self.canvas.delete("all")

        # Display image centered
        self.canvas_image = self.canvas.create_image(
            canvas_width // 2 if canvas_width > 1 else 400,
            canvas_height // 2 if canvas_height > 1 else 300,
            image=self.photo_image,
            anchor=tk.CENTER
        )

        # Update scrollregion
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        # Update status bar with image info
        if self.image_processor.metadata:
            self.info_label.config(text=str(self.image_processor.metadata))

    def _update_status(self, message: str) -> None:
        """Update the status bar message"""
        self.status_label.config(text=message)

    def _show_about(self) -> None:
        """Show about dialog"""
        messagebox.showinfo(
            "About",
            "Image Editor\n"
            "HIT137 Assignment 3\n\n"
            "A desktop application demonstrating OOP principles,\n"
            "GUI development with Tkinter, and image processing with OpenCV.\n\n"
            "Features:\n"
            "• 8 Image Processing Filters\n"
            "• Undo/Redo Functionality\n"
            "• File Operations\n"
            "• Adjustable Filter Intensities"
        )

    def _show_shortcuts(self) -> None:
        """Show keyboard shortcuts dialog"""
        shortcuts = """
        Keyboard Shortcuts:

        Ctrl+O          Open Image
        Ctrl+S          Save Image
        Ctrl+Shift+S    Save As
        Ctrl+Z          Undo
        Ctrl+Y          Redo
        Ctrl++          Zoom In
        Ctrl+-          Zoom Out
        Ctrl+0          Fit to Window
        Alt+F4          Exit
        """
        messagebox.showinfo("Keyboard Shortcuts", shortcuts)

    def _on_closing(self) -> None:
        """Handle window closing event"""
        if self.is_modified:
            response = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save them?"
            )
            if response is None:  # Cancel
                return
            elif response:  # Yes - save
                self._save_image()

        self.root.quit()