"""
Main Window for Virtual Radiosonde Plotter.
Assembles UI widgets, handles application state, and manages asynchronous data processing.
"""

from typing import Optional, Dict, Any
import os
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QSplitter,
    QFileDialog, QProgressBar, QLabel, QMenuBar, QMenu
)
from PySide6.QtGui import QAction, QIcon

from .widgets import ControlPanelWidget, ParameterDisplayWidget, PlotCanvasWidget
from .dialogs import AboutDialog, ExportDialog, show_error_dialog, show_info_dialog
from .icon_utils import load_app_icon
from core.sounding import SoundingData
from core.downloader import SoundingDownloader
from core.calculations import SoundingCalculator
from core.plotting import SkewTPlotter


class DataFetchWorker(QThread):
    """
    Background worker thread to handle API downloading and MetPy thermodynamic calculations
    without freezing the main Qt UI thread.
    """
    finished = Signal(object)  # Emits SoundingData
    error = Signal(str)        # Emits error string message

    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = config

    def run(self):
        try:
            downloader = SoundingDownloader()
            pressures, temp_list, rh_list, ws_list, wd_list, valid_time_str = downloader.fetch_sounding(
                latitude=self.config["latitude"],
                longitude=self.config["longitude"],
                date_str=self.config["date_str"],
                target_utc_hour=self.config["target_utc_hour"],
                location_name=self.config["location_name"],
                source=self.config["source"]
            )

            # Create SoundingData instance
            sounding = SoundingData(
                pressures=pressures,
                temperatures=temp_list,
                dewpoints=temp_list,  # Will be recalculated from RH in SoundingCalculator
                relative_humidity=rh_list,
                wind_speeds=ws_list,
                wind_directions=wd_list,
                latitude=self.config["latitude"],
                longitude=self.config["longitude"],
                date_str=self.config["date_str"],
                time_utc_hour=self.config["target_utc_hour"],
                location_name=self.config["location_name"],
                source=self.config["source"]
            )

            # Run MetPy calculations
            sounding = SoundingCalculator.process_sounding(sounding)
            self.finished.emit(sounding)

        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """
    Main Application Window container.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Virtual Radiosonde Plotter")
        self.resize(1280, 800)

        app_icon = load_app_icon()
        if not app_icon.isNull():
            self.setWindowIcon(app_icon)

        self.current_sounding: Optional[SoundingData] = None
        self.dark_mode = False
        self.worker: Optional[DataFetchWorker] = None

        self.init_ui()
        self.create_menus()

    def init_ui(self):
        # Central widget layout with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(4, 4, 4, 4)

        splitter = QSplitter(Qt.Horizontal)

        # 1. Left Control Panel
        self.control_panel = ControlPanelWidget()
        self.control_panel.setMinimumWidth(260)
        self.control_panel.setMaximumWidth(340)

        # 2. Center Plot Canvas
        self.canvas_widget = PlotCanvasWidget()

        # 3. Right Parameter Panel
        self.param_panel = ParameterDisplayWidget()
        self.param_panel.setMinimumWidth(280)
        self.param_panel.setMaximumWidth(360)

        splitter.addWidget(self.control_panel)
        splitter.addWidget(self.canvas_widget)
        splitter.addWidget(self.param_panel)

        # Set initial splitter stretch factors (Left: 1, Center: 3, Right: 1)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        splitter.setStretchFactor(2, 1)

        main_layout.addWidget(splitter)

        # Status Bar
        self.status_bar = self.statusBar()
        self.lbl_status = QLabel("Ready")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.setFixedWidth(150)
        self.progress_bar.setVisible(False)

        self.status_bar.addWidget(self.lbl_status)
        self.status_bar.addPermanentWidget(self.progress_bar)

        # Connect Control Panel signals
        self.control_panel.fetch_requested.connect(self.start_fetch_sounding)
        self.control_panel.save_figure_requested.connect(self.save_figure)
        self.control_panel.export_csv_requested.connect(self.export_csv)

    def create_menus(self):
        menu_bar = self.menuBar()

        # File Menu
        menu_file = menu_bar.addMenu("&File")

        act_save_fig = QAction("&Save Figure...", self)
        act_save_fig.setShortcut("Ctrl+S")
        act_save_fig.triggered.connect(self.save_figure)

        act_export_csv = QAction("&Export CSV Data...", self)
        act_export_csv.setShortcut("Ctrl+E")
        act_export_csv.triggered.connect(self.export_csv)

        act_exit = QAction("E&xit", self)
        act_exit.setShortcut("Ctrl+Q")
        act_exit.triggered.connect(self.close)

        menu_file.addAction(act_save_fig)
        menu_file.addAction(act_export_csv)
        menu_file.addSeparator()
        menu_file.addAction(act_exit)

        # View Menu
        menu_view = menu_bar.addMenu("&View")
        act_toggle_theme = QAction("Toggle &Dark Theme", self)
        act_toggle_theme.triggered.connect(self.toggle_dark_theme)
        menu_view.addAction(act_toggle_theme)

        # Help Menu
        menu_help = menu_bar.addMenu("&Help")
        act_about = QAction("&About Virtual Radiosonde Plotter", self)
        act_about.triggered.connect(self.show_about_dialog)
        menu_help.addAction(act_about)

    def start_fetch_sounding(self, config: Dict[str, Any]):
        """Launches asynchronous DataFetchWorker thread."""
        self.control_panel.btn_download.setEnabled(False)
        self.lbl_status.setText(f"Downloading sounding data for {config['location_name']}...")
        self.progress_bar.setVisible(True)

        self.worker = DataFetchWorker(config)
        self.worker.finished.connect(self.on_fetch_success)
        self.worker.error.connect(self.on_fetch_error)
        self.worker.start()

    def on_fetch_success(self, sounding: SoundingData):
        """Callback when worker successfully finishes downloading and processing."""
        self.current_sounding = sounding
        self.progress_bar.setVisible(False)
        self.control_panel.btn_download.setEnabled(True)
        self.lbl_status.setText(f"Sounding analysis complete for {sounding.location_name} ({sounding.observation_time_str}).")

        # 1. Update Skew-T Plot
        fig = SkewTPlotter.create_skewt_figure(sounding, dark_mode=self.dark_mode)
        self.canvas_widget.set_figure(fig)

        # 2. Update Right Parameter Panel
        self.param_panel.update_indices(sounding.indices)

    def on_fetch_error(self, error_msg: str):
        """Callback when worker encounters an error."""
        self.progress_bar.setVisible(False)
        self.control_panel.btn_download.setEnabled(True)
        self.lbl_status.setText("Error generating sounding.")

        show_error_dialog(self, "Data Download / Calculation Error", error_msg)

    def save_figure(self):
        """Exports currently rendered Skew-T figure to PNG or PDF."""
        if self.current_sounding is None:
            show_info_dialog(self, "No Sounding Data", "Please fetch and plot a sounding before saving the figure.")
            return

        dlg = ExportDialog(self)
        if dlg.exec():
            ext, dpi = dlg.get_settings()
            default_filename = f"skewt_{self.current_sounding.location_name.lower().replace(' ', '_')}_{self.current_sounding.date_str}.{ext}"

            file_filter = "PNG Image (*.png)" if ext == "png" else ("PDF Document (*.pdf)" if ext == "pdf" else "SVG Vector (*.svg)")
            filepath, _ = QFileDialog.getSaveFileName(self, "Save Skew-T Figure", default_filename, file_filter)

            if filepath:
                try:
                    fig = SkewTPlotter.create_skewt_figure(self.current_sounding, dpi=dpi, dark_mode=self.dark_mode)
                    SkewTPlotter.save_figure(fig, filepath, dpi=dpi)
                    self.lbl_status.setText(f"Figure saved to {os.path.basename(filepath)}")
                    show_info_dialog(self, "Export Successful", f"Skew-T diagram successfully saved to:\n{filepath}")
                except Exception as e:
                    show_error_dialog(self, "Save Error", f"Failed to save figure: {e}")

    def export_csv(self):
        """Exports profile data and indices to CSV file."""
        if self.current_sounding is None:
            show_info_dialog(self, "No Sounding Data", "Please fetch and plot a sounding before exporting CSV data.")
            return

        default_filename = f"sounding_{self.current_sounding.location_name.lower().replace(' ', '_')}_{self.current_sounding.date_str}.csv"
        filepath, _ = QFileDialog.getSaveFileName(self, "Export Sounding CSV", default_filename, "CSV Files (*.csv)")

        if filepath:
            try:
                self.current_sounding.to_csv(filepath)
                self.lbl_status.setText(f"CSV data exported to {os.path.basename(filepath)}")
                show_info_dialog(self, "Export Successful", f"Sounding data successfully exported to:\n{filepath}")
            except Exception as e:
                show_error_dialog(self, "Export Error", f"Failed to export CSV: {e}")

    def toggle_dark_theme(self):
        """Toggles dark theme for figure rendering."""
        self.dark_mode = not self.dark_mode
        if self.current_sounding:
            fig = SkewTPlotter.create_skewt_figure(self.current_sounding, dark_mode=self.dark_mode)
            self.canvas_widget.set_figure(fig)
        self.lbl_status.setText(f"Dark mode {'enabled' if self.dark_mode else 'disabled'}.")

    def show_about_dialog(self):
        """Displays About Dialog."""
        dlg = AboutDialog(self)
        dlg.exec()
