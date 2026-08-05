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
    """Applies a modern, high-contrast, clean styling theme to the Qt Application."""
    qss = """
    QMainWindow {
        background-color: #f8fafc;
    }
    QWidget {
        font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif;
        color: #0f172a;
    }
    QLabel {
        color: #0f172a;
        font-weight: 500;
    }
    QGroupBox {
        font-weight: bold;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        margin-top: 10px;
        padding-top: 12px;
        background-color: #ffffff;
        color: #0f172a;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 6px;
        color: #1e293b;
    }
    QLineEdit, QDoubleSpinBox, QDateEdit, QComboBox {
        border: 1px solid #cbd5e1;
        border-radius: 4px;
        padding: 6px;
        background-color: #ffffff;
        color: #0f172a;
        font-weight: 600;
    }
    QLineEdit:focus, QDoubleSpinBox:focus, QDateEdit:focus, QComboBox:focus {
        border: 2px solid #2563eb;
    }

    /* ComboBox & Dropdown Selectors */
    QComboBox QAbstractItemView {
        background-color: #ffffff;
        color: #0f172a;
        selection-background-color: #2563eb;
        selection-color: #ffffff;
        border: 1px solid #cbd5e1;
        outline: none;
        padding: 4px;
    }
    QComboBox QAbstractItemView::item {
        color: #0f172a;
        min-height: 26px;
        padding: 4px 8px;
    }
    QComboBox QAbstractItemView::item:selected, QComboBox QAbstractItemView::item:hover {
        background-color: #2563eb;
        color: #ffffff;
        font-weight: bold;
    }

    /* Menu Bar (File, View, Help) */
    QMenuBar {
        background-color: #1e293b;
        color: #f8fafc;
        font-weight: bold;
        font-size: 12px;
        padding: 2px 4px;
        border-bottom: 1px solid #0f172a;
    }
    QMenuBar::item {
        background-color: transparent;
        color: #f8fafc;
        padding: 6px 12px;
        border-radius: 4px;
    }
    QMenuBar::item:selected, QMenuBar::item:pressed {
        background-color: #2563eb;
        color: #ffffff;
    }

    /* Dropdown Menus (File -> Save, View -> Dark Theme, Help -> About) */
    QMenu {
        background-color: #ffffff;
        color: #0f172a;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        padding: 4px;
    }
    QMenu::item {
        background-color: transparent;
        color: #0f172a;
        font-weight: 500;
        padding: 6px 24px 6px 12px;
        border-radius: 4px;
    }
    QMenu::item:selected {
        background-color: #2563eb;
        color: #ffffff;
        font-weight: bold;
    }
    QMenu::separator {
        height: 1px;
        background-color: #e2e8f0;
        margin: 4px 8px;
    }

    /* Buttons */
    QPushButton {
        border: 1px solid #cbd5e1;
        border-radius: 4px;
        padding: 6px 12px;
        background-color: #ffffff;
        color: #0f172a;
        font-weight: 600;
    }
    QPushButton:hover {
        background-color: #f1f5f9;
        border-color: #64748b;
    }
    QTableWidget {
        background-color: #ffffff;
        color: #0f172a;
        gridline-color: #cbd5e1;
        font-size: 11px;
    }
    QTableWidget::item {
        color: #0f172a;
        padding: 4px;
    }
    QHeaderView::section {
        background-color: #e2e8f0;
        color: #0f172a;
        font-weight: bold;
        padding: 5px;
        border: 1px solid #cbd5e1;
    }
    QMessageBox, QDialog {
        background-color: #ffffff;
        color: #0f172a;
    }
    QMessageBox QLabel, QDialog QLabel {
        color: #0f172a;
        font-weight: 500;
    }
    QStatusBar {
        background-color: #e2e8f0;
        color: #0f172a;
        font-weight: 500;
    }
    QStatusBar QLabel {
        color: #0f172a;
        font-weight: 600;
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

    # Set Window & Taskbar Favicon Icon
    app_icon = load_app_icon()
    if not app_icon.isNull():
        app.setWindowIcon(app_icon)

    # Set Application Font
    font = QFont("Segoe UI", 9)
    app.setFont(font)

    apply_app_stylesheet(app)

    main_win = MainWindow()
    main_win.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
