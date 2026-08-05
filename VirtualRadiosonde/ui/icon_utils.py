"""
Icon Utility Module for Virtual Radiosonde Plotter.
Loads logo.webp using Pillow and converts it to PySide6 QIcon for window & taskbar favicon.
"""

import os
import io
from typing import Optional
from PIL import Image

from PySide6.QtGui import QImage, QPixmap, QIcon


def load_app_icon(logo_path: Optional[str] = None) -> QIcon:
    """
    Loads logo.webp (or fallback icon formats) and returns a PySide6 QIcon.
    """
    if logo_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(base_dir, "assets", "logo", "logo.webp")

    if not os.path.exists(logo_path):
        return QIcon()

    try:
        # Load webp using Pillow
        pil_img = Image.open(logo_path)
        buffer = io.BytesIO()
        pil_img.save(buffer, format="PNG")
        
        qimg = QImage.fromData(buffer.getvalue())
        pixmap = QPixmap.fromImage(qimg)
        return QIcon(pixmap)
    except Exception as e:
        print(f"[WARNING] Could not load app icon from {logo_path}: {e}")
        return QIcon()
