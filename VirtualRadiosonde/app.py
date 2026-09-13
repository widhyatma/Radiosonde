"""
Virtual Radiosonde Plotter - Application Entry Point (Tkinter).
"""

import sys
import os
import ctypes
import tkinter as tk
from tkinter import ttk

# Ensure VirtualRadiosonde package root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ui.main_window import MainWindow
from ui.icon_utils import apply_window_icon


def configure_high_dpi():
    """Enables crisp per-monitor DPI awareness on Windows."""
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def configure_app_id():
    """Sets Windows AppUserModelID for proper taskbar grouping and icon."""
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "JerukagungMeteorologi.VirtualRadiosondePlotter.1.0"
        )
    except Exception:
        pass


def configure_retro_style(root: tk.Tk):
    """Configures classic Windows XP retro styling for ttk widgets."""
    style = ttk.Style(root)
    available_themes = style.theme_names()
    if 'winnative' in available_themes:
        style.theme_use('winnative')
    elif 'classic' in available_themes:
        style.theme_use('classic')

    # Global font and color settings
    style.configure(".", font=("Tahoma", 9), background="#ece9d8", foreground="#000000")
    style.configure("Treeview", font=("Tahoma", 8), rowheight=20, background="#ffffff", fieldbackground="#ffffff")
    style.configure("Treeview.Heading", font=("Tahoma", 8, "bold"), background="#ece9d8", foreground="#000000")
    style.map("Treeview.Heading", relief=[('active', 'raised'), ('!active', 'raised')])


def main():
    configure_high_dpi()
    configure_app_id()

    root = tk.Tk()
    configure_retro_style(root)

    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
