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
from PySide6.QtGui import QFont, QPalette, QColor

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


def create_classic_xp_palette() -> QPalette:
    """Returns an authentic Windows XP Classic neutral color palette to override modern OS dark modes."""
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#ece9d8"))
    palette.setColor(QPalette.WindowText, QColor("#000000"))
    palette.setColor(QPalette.Base, QColor("#ffffff"))
    palette.setColor(QPalette.AlternateBase, QColor("#f0eee0"))
    palette.setColor(QPalette.ToolTipBase, QColor("#ffffe1"))
    palette.setColor(QPalette.ToolTipText, QColor("#000000"))
    palette.setColor(QPalette.Text, QColor("#000000"))
    palette.setColor(QPalette.Button, QColor("#ece9d8"))
    palette.setColor(QPalette.ButtonText, QColor("#000000"))
    palette.setColor(QPalette.BrightText, QColor("#ffffff"))
    palette.setColor(QPalette.Link, QColor("#0000ff"))
    palette.setColor(QPalette.Highlight, QColor("#316ac5"))
    palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    palette.setColor(QPalette.Disabled, QPalette.Text, QColor("#808080"))
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor("#808080"))
    palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor("#808080"))
    palette.setColor(QPalette.Light, QColor("#ffffff"))
    palette.setColor(QPalette.Midlight, QColor("#f4f3ec"))
    palette.setColor(QPalette.Dark, QColor("#aca899"))
    palette.setColor(QPalette.Mid, QColor("#c0bcb0"))
    palette.setColor(QPalette.Shadow, QColor("#716f64"))
    return palette


def apply_app_stylesheet(app: QApplication):
    """Applies a classic Windows XP / Windows Classic square & boxy styling theme."""
    qss = """
    QMainWindow, QDialog, QMessageBox {
        background-color: #ece9d8;
        color: #000000;
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
    QLineEdit, QDoubleSpinBox, QDateEdit, QComboBox, QSpinBox {
        border: 1px solid #7f9db9;
        border-radius: 0px;
        padding: 3px 5px;
        background-color: #ffffff;
        color: #000000;
    }
    QLineEdit:focus, QDoubleSpinBox:focus, QDateEdit:focus, QComboBox:focus, QSpinBox:focus {
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

    /* Status Bar */
    QStatusBar {
        background-color: #ece9d8;
        border-top: 1px solid #919b9c;
        color: #000000;
    }
    QStatusBar QLabel {
        color: #000000;
    }

    /* Progress Bar */
    QProgressBar {
        border: 2px inset #d4d0c8;
        border-radius: 0px;
        background-color: #ffffff;
        text-align: center;
        color: #000000;
        font-weight: bold;
    }
    QProgressBar::chunk {
        background-color: #316ac5;
    }

    /* Scrollbars */
    QScrollBar:vertical {
        border: 1px solid #919b9c;
        background-color: #ece9d8;
        width: 16px;
        margin: 16px 0 16px 0;
    }
    QScrollBar::handle:vertical {
        background-color: #ece9d8;
        border: 2px outset #d4d0c8;
        border-radius: 0px;
        min-height: 20px;
    }
    QScrollBar::handle:vertical:pressed {
        border: 2px inset #d4d0c8;
        background-color: #e2dfce;
    }
    QScrollBar::add-line:vertical {
        border: 2px outset #d4d0c8;
        border-radius: 0px;
        background-color: #ece9d8;
        height: 16px;
        subcontrol-position: bottom;
        subcontrol-origin: margin;
    }
    QScrollBar::sub-line:vertical {
        border: 2px outset #d4d0c8;
        border-radius: 0px;
        background-color: #ece9d8;
        height: 16px;
        subcontrol-position: top;
        subcontrol-origin: margin;
    }
    QScrollBar:horizontal {
        border: 1px solid #919b9c;
        background-color: #ece9d8;
        height: 16px;
        margin: 0 16px 0 16px;
    }
    QScrollBar::handle:horizontal {
        background-color: #ece9d8;
        border: 2px outset #d4d0c8;
        border-radius: 0px;
        min-width: 20px;
    }
    QScrollBar::handle:horizontal:pressed {
        border: 2px inset #d4d0c8;
        background-color: #e2dfce;
    }
    QScrollBar::add-line:horizontal {
        border: 2px outset #d4d0c8;
        border-radius: 0px;
        background-color: #ece9d8;
        width: 16px;
        subcontrol-position: right;
        subcontrol-origin: margin;
    }
    QScrollBar::sub-line:horizontal {
        border: 2px outset #d4d0c8;
        border-radius: 0px;
        background-color: #ece9d8;
        width: 16px;
        subcontrol-position: left;
        subcontrol-origin: margin;
    }

    /* Splitter */
    QSplitter::handle {
        background-color: #d4d0c8;
    }
    QSplitter::handle:horizontal {
        width: 4px;
    }
    QSplitter::handle:vertical {
        height: 4px;
    }

    /* Tooltip */
    QToolTip {
        background-color: #ffffe1;
        color: #000000;
        border: 1px solid #000000;
        border-radius: 0px;
        padding: 2px 4px;
    }

    /* Classic Windows Calendar Widget */
    QCalendarWidget {
        background-color: #ece9d8;
        border: 2px outset #d4d0c8;
    }
    QCalendarWidget QWidget#qt_calendar_navigationbar {
        background-color: #ece9d8;
        border-bottom: 1px solid #919b9c;
        min-height: 26px;
    }
    QCalendarWidget QToolButton {
        background-color: #ece9d8;
        color: #000000;
        border: 2px outset #d4d0c8;
        border-radius: 0px;
        margin: 1px;
        padding: 2px 6px;
        font-family: 'Tahoma';
        font-size: 11px;
        font-weight: normal;
    }
    QCalendarWidget QToolButton:hover {
        background-color: #f5f4ea;
    }
    QCalendarWidget QToolButton:pressed {
        border: 2px inset #d4d0c8;
        background-color: #e2dfce;
    }
    QCalendarWidget QSpinBox#qt_calendar_yearedit {
        background-color: #ffffff;
        color: #000000;
        border: 1px solid #7f9db9;
        border-radius: 0px;
        font-family: 'Tahoma';
        font-size: 11px;
    }
    QCalendarWidget QTableView#qt_calendar_calendarview {
        background-color: #ffffff;
        color: #000000;
        border: 1px solid #7f9db9;
        border-radius: 0px;
        selection-background-color: #316ac5;
        selection-color: #ffffff;
        gridline-color: #d4d0c8;
        font-family: 'Tahoma';
        font-size: 11px;
    }
    QCalendarWidget QMenu {
        background-color: #ffffff;
        color: #000000;
        border: 1px solid #919b9c;
        border-radius: 0px;
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

    # Override modern OS dark theme by forcing authentic Windows XP neutral palette
    app.setPalette(create_classic_xp_palette())

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
