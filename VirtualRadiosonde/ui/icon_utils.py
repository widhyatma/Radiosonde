"""
Icon Utility Module for Virtual Radiosonde Plotter (Tkinter).
Loads logo.webp using Pillow and sets it as window & taskbar icon.
"""

import os
from typing import Optional
from PIL import Image, ImageTk
import tkinter as tk

# Global cache so garbage collector doesn't discard the PhotoImage
_CACHED_ICON = None


def get_app_icon_photo(logo_path: Optional[str] = None) -> Optional[ImageTk.PhotoImage]:
    """
    Loads logo.webp using Pillow and returns a Tkinter PhotoImage.
    """
    global _CACHED_ICON
    if _CACHED_ICON is not None:
        return _CACHED_ICON

    if logo_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(base_dir, "assets", "logo", "logo.webp")

    if not os.path.exists(logo_path):
        return None

    try:
        pil_img = Image.open(logo_path)
        # Resize to standard icon size if desired or keep high res
        _CACHED_ICON = ImageTk.PhotoImage(pil_img)
        return _CACHED_ICON
    except Exception as e:
        print(f"[WARNING] Could not load app icon from {logo_path}: {e}")
        return None


def apply_window_icon(window: tk.Wm, logo_path: Optional[str] = None) -> None:
    """
    Applies the logo icon to a Tk or Toplevel window.
    """
    icon = get_app_icon_photo(logo_path)
    if icon is not None:
        try:
            window.iconphoto(True, icon)
        except Exception:
            pass
