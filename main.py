#!/usr/bin/env python3
"""
HIT137 Assignment 3 - Image Processing Desktop Application
Main entry point for the application

This application demonstrates Object-Oriented Programming principles,
GUI development using Tkinter, and image processing using OpenCV.

Author: Group Assignment Team
Date: January 2026
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Add src directory to path for proper imports (works on Windows, Mac, Linux)
SRC_DIR = os.path.join(SCRIPT_DIR, 'src')
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# Import main application
from gui.main_window import ImageEditorApp


def main():
    """Main entry point for the application"""
    try:
        # Create the root window
        root = tk.Tk()

        # Initialize the application
        app = ImageEditorApp(root)

        # Start the GUI event loop
        root.mainloop()

    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()