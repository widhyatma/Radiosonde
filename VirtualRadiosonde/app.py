"""
Virtual Radiosonde Plotter - Application Entry Point
"""

import sys
import os

# Ensure VirtualRadiosonde package root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

from ui.main_window import MainWindow
from ui.icon_utils import load_app_icon

# Set Windows Taskbar AppUserModelID so the logo icon shows on Taskbar
import ctypes
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
        "JerukagungMeteorologi.VirtualRadiosondePlotter.1.0"
    )
except Exception:
    pass


def apply_app_stylesheet(app: QApplication):
    """Applies a classic Windows XP / Windows Classic square & boxy styling theme."""
    qss = """
    QMainWindow {
        background-color: #ece9d8;
    }
    QWidget {
        font-family: 'Tahoma', 'Segoe UI', sans-serif;
        font-size: 11px;
        color: #000000;
    }
    QLabel {
        color: #000000;
    }
    QGroupBox {
        font-weight: bold;
        border: 1px solid #919b9c;
        border-radius: 0px;
        margin-top: 8px;
        padding-top: 10px;
        background-color: transparent;
        color: #000000;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 4px;
        color: #000000;
    }
    QLineEdit, QDoubleSpinBox, QDateEdit, QComboBox {
        border: 1px solid #7f9db9;
        border-radius: 0px;
        padding: 3px 5px;
        background-color: #ffffff;
        color: #000000;
    }
    QLineEdit:focus, QDoubleSpinBox:focus, QDateEdit:focus, QComboBox:focus {
        border: 1px solid #003c74;
    }

    /* ComboBox */
    QComboBox QAbstractItemView {
        background-color: #ffffff;
        color: #000000;
        selection-background-color: #316ac5;
        selection-color: #ffffff;
        border: 1px solid #7f9db9;
        border-radius: 0px;
        outline: none;
    }
    QComboBox QAbstractItemView::item:selected, QComboBox QAbstractItemView::item:hover {
        background-color: #316ac5;
        color: #ffffff;
    }

    /* Menu Bar */
    QMenuBar {
        background-color: #ece9d8;
        color: #000000;
        font-size: 11px;
        border-bottom: 1px solid #919b9c;
    }
    QMenuBar::item {
        background-color: transparent;
        color: #000000;
        padding: 3px 8px;
        border-radius: 0px;
    }
    QMenuBar::item:selected, QMenuBar::item:pressed {
        background-color: #316ac5;
        color: #ffffff;
    }

    /* Menus */
    QMenu {
        background-color: #ffffff;
        color: #000000;
        border: 1px solid #919b9c;
        border-radius: 0px;
        padding: 2px;
    }
    QMenu::item {
        padding: 4px 20px 4px 10px;
        border-radius: 0px;
    }
    QMenu::item:selected {
        background-color: #316ac5;
        color: #ffffff;
    }
    QMenu::separator {
        height: 1px;
        background-color: #d4d0c8;
        margin: 2px 4px;
    }

    /* Classic Boxy Buttons */
    QPushButton {
        border: 2px outset #d4d0c8;
        border-radius: 0px;
        padding: 4px 12px;
        background-color: #ece9d8;
        color: #000000;
        font-weight: normal;
    }
    QPushButton:hover {
        background-color: #f5f4ea;
    }
    QPushButton:pressed {
        border: 2px inset #d4d0c8;
        background-color: #e2dfce;
    }
    QPushButton:disabled {
        color: #888888;
        border-color: #d4d0c8;
    }

    /* Table Widget */
    QTableWidget {
        background-color: #ffffff;
        color: #000000;
        gridline-color: #d4d0c8;
        border: 1px solid #7f9db9;
        border-radius: 0px;
        font-size: 11px;
    }
    QTableWidget::item {
        color: #000000;
        padding: 3px;
        border-radius: 0px;
    }
    QHeaderView::section {
        background-color: #ece9d8;
        color: #000000;
        font-weight: bold;
        padding: 4px;
        border: 1px solid #919b9c;
        border-radius: 0px;
    }

    QStatusBar {
        background-color: #ece9d8;
        border-top: 1px solid #919b9c;
        color: #000000;
    }
    QStatusBar QLabel {
        color: #000000;
    }
    """
    app.setStyleSheet(qss)


def main():
    # Enable High DPI Scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("Virtual Radiosonde Plotter")
    app.setOrganizationName("Jerukagung Meteorologi")

    # Set Classic Windows Engine ('Windows' / 'Fusion')
    app.setStyle("Windows")

    # Set Window & Taskbar Favicon Icon
    app_icon = load_app_icon()
    if not app_icon.isNull():
        app.setWindowIcon(app_icon)

    # Set Classic Windows XP Font (Tahoma)
    font = QFont("Tahoma", 9)
    app.setFont(font)

    apply_app_stylesheet(app)

    main_win = MainWindow()
    main_win.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
