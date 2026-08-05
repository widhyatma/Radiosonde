"""
UI package for Virtual Radiosonde Plotter.
Contains PySide6 Qt main window, custom widgets, and dialogs.
"""

from .widgets import ControlPanelWidget, ParameterDisplayWidget, PlotCanvasWidget
from .dialogs import AboutDialog, ExportDialog
from .main_window import MainWindow

__all__ = [
    "ControlPanelWidget",
    "ParameterDisplayWidget",
    "PlotCanvasWidget",
    "AboutDialog",
    "ExportDialog",
    "MainWindow",
]
