"""
Main Application Window for Virtual Radiosonde Plotter (Tkinter).
Assembles UI widgets, handles application state, and manages asynchronous data processing.
"""

import os
import threading
from typing import Optional, Dict, Any
import tkinter as tk
from tkinter import ttk, filedialog

from .widgets import ControlPanelWidget, ParameterDisplayWidget, PlotCanvasWidget
from .dialogs import AboutDialog, ExportDialog, show_error_dialog, show_info_dialog
from .icon_utils import apply_window_icon
from core.sounding import SoundingData
from core.downloader import SoundingDownloader
from core.calculations import SoundingCalculator
from core.plotting import SkewTPlotter


class MainWindow:
    """
    Main Application Window container for Virtual Radiosonde Plotter.
    """
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Virtual Radiosonde Plotter")
        self.root.geometry("1280x800")
        self.root.minsize(960, 600)
        self.root.configure(bg="#ece9d8")

        apply_window_icon(self.root)

        self.current_sounding: Optional[SoundingData] = None
        self.dark_mode = False

        self.create_menus()
        self.init_ui()

    def create_menus(self):
        menubar = tk.Menu(self.root, font=("Tahoma", 9))
        self.root.config(menu=menubar)

        # File Menu
        menu_file = tk.Menu(menubar, tearoff=False, font=("Tahoma", 9))
        menu_file.add_command(label="Save Figure...", accelerator="Ctrl+S", command=self.save_figure)
        menu_file.add_command(label="Export CSV Data...", accelerator="Ctrl+E", command=self.export_csv)
        menu_file.add_separator()
        menu_file.add_command(label="Exit", accelerator="Ctrl+Q", command=self.root.quit)
        menubar.add_cascade(label="File", menu=menu_file)

        # View Menu
        menu_view = tk.Menu(menubar, tearoff=False, font=("Tahoma", 9))
        menu_view.add_command(label="Toggle Dark Theme", command=self.toggle_dark_theme)
        menubar.add_cascade(label="View", menu=menu_view)

        # Help Menu
        menu_help = tk.Menu(menubar, tearoff=False, font=("Tahoma", 9))
        menu_help.add_command(label="About Virtual Radiosonde Plotter", command=self.show_about_dialog)
        menubar.add_cascade(label="Help", menu=menu_help)

        # Bind shortcuts
        self.root.bind("<Control-s>", lambda e: self.save_figure())
        self.root.bind("<Control-e>", lambda e: self.export_csv())
        self.root.bind("<Control-q>", lambda e: self.root.quit())

    def init_ui(self):
        # Top Container with PanedWindow Splitter
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # 1. Left Control Panel
        self.control_panel = ControlPanelWidget(
            parent=main_paned,
            on_fetch=self.start_fetch_sounding,
            on_open_csv=self.handle_open_csv,
            on_save_figure=self.save_figure,
            on_export_csv=self.export_csv,
            on_search_city=self.handle_city_search
        )
        main_paned.add(self.control_panel, weight=1)

        # 2. Center Plot Canvas
        self.canvas_widget = PlotCanvasWidget(parent=main_paned)
        main_paned.add(self.canvas_widget, weight=4)

        # 3. Right Parameter Panel
        self.param_panel = ParameterDisplayWidget(
            parent=main_paned,
            on_copy_summary=self.handle_copy_summary
        )
        main_paned.add(self.param_panel, weight=1)

        # Bottom Status Bar
        status_frame = tk.Frame(self.root, bg="#ece9d8", bd=1, relief=tk.SUNKEN)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.lbl_status = tk.Label(
            status_frame,
            text="Ready",
            font=("Tahoma", 9),
            bg="#ece9d8",
            fg="#000000",
            anchor="w"
        )
        self.lbl_status.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6, pady=2)

        self.progress_bar = ttk.Progressbar(status_frame, mode="indeterminate", length=150)
        # Hidden by default

    def set_status(self, text: str):
        self.lbl_status.config(text=text)

    def handle_city_search(self, city_name: str):
        self.set_status(f"Searching coordinates for '{city_name}'...")
        cities = SoundingDownloader.search_city(city_name)
        if not cities:
            show_error_dialog(self.root, "City Not Found", f"No matching coordinates found for '{city_name}'.")
            self.set_status("Ready")
            return

        best = cities[0]
        self.control_panel.set_coordinates(best["latitude"], best["longitude"], best["name"])
        self.set_status(f"Found city: {best['display_name']}")
        show_info_dialog(
            self.root,
            "City Search Result",
            f"Found location for '{best['name']}':\n"
            f"Latitude: {best['latitude']:.4f}°\n"
            f"Longitude: {best['longitude']:.4f}°\n"
            f"Region/Country: {best['admin1']}, {best['country']}"
        )

    def handle_open_csv(self):
        file_path = filedialog.askopenfilename(
            parent=self.root,
            title="Open Local Sounding CSV Data",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        try:
            self.set_status(f"Reading local CSV file: {file_path}...")
            sounding = SoundingData.from_csv(file_path)
            sounding = SoundingCalculator.process_sounding(sounding)
            self.current_sounding = sounding

            fig = SkewTPlotter.create_skewt_figure(sounding, dark_mode=self.dark_mode)
            self.canvas_widget.set_figure(fig)
            self.param_panel.update_indices(sounding.indices)

            self.set_status(f"Loaded local CSV sounding: {sounding.location_name}")
            show_info_dialog(self.root, "Local CSV Loaded", f"Successfully loaded and plotted sounding data from:\n{file_path}")
        except Exception as e:
            show_error_dialog(self.root, "CSV Loading Error", f"Failed to load CSV file:\n{e}")
            self.set_status("Ready")

    def handle_copy_summary(self):
        if not self.current_sounding:
            show_error_dialog(self.root, "No Active Sounding", "Please fetch or open a sounding profile before copying summary text.")
            return

        text = self.current_sounding.to_summary_text()
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        show_info_dialog(self.root, "Summary Copied", "Atmospheric sounding summary text has been copied to your clipboard!")

    def start_fetch_sounding(self, config: Dict[str, Any]):
        self.control_panel.btn_download.config(state=tk.DISABLED)
        self.set_status(f"Downloading sounding data for {config['location_name']}...")
        self.progress_bar.pack(side=tk.RIGHT, padx=6, pady=2)
        self.progress_bar.start(10)

        # Launch background daemon thread
        threading.Thread(target=self._worker_fetch, args=(config,), daemon=True).start()

    def _worker_fetch(self, config: Dict[str, Any]):
        try:
            downloader = SoundingDownloader()
            pressures, temp_list, rh_list, ws_list, wd_list, valid_time_str = downloader.fetch_sounding(
                latitude=config["latitude"],
                longitude=config["longitude"],
                date_str=config["date_str"],
                target_utc_hour=config["target_utc_hour"],
                location_name=config["location_name"],
                source=config["source"]
            )

            sounding = SoundingData(
                pressures=pressures,
                temperatures=temp_list,
                dewpoints=temp_list,
                relative_humidity=rh_list,
                wind_speeds=ws_list,
                wind_directions=wd_list,
                latitude=config["latitude"],
                longitude=config["longitude"],
                date_str=config["date_str"],
                time_utc_hour=config["target_utc_hour"],
                location_name=config["location_name"],
                source=config["source"]
            )

            sounding = SoundingCalculator.process_sounding(sounding)
            self.root.after(0, self.on_fetch_success, sounding)
        except Exception as e:
            self.root.after(0, self.on_fetch_error, str(e))

    def on_fetch_success(self, sounding: SoundingData):
        self.current_sounding = sounding
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.control_panel.btn_download.config(state=tk.NORMAL)
        self.set_status(f"Sounding analysis complete for {sounding.location_name} ({sounding.observation_time_str}).")

        # 1. Update Skew-T Plot
        fig = SkewTPlotter.create_skewt_figure(sounding, dark_mode=self.dark_mode)
        self.canvas_widget.set_figure(fig)

        # 2. Update Right Parameter Panel
        self.param_panel.update_indices(sounding.indices)

    def on_fetch_error(self, error_msg: str):
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.control_panel.btn_download.config(state=tk.NORMAL)
        self.set_status("Error generating sounding.")
        show_error_dialog(self.root, "Data Download / Calculation Error", error_msg)

    def save_figure(self):
        if self.current_sounding is None:
            show_info_dialog(self.root, "No Sounding Data", "Please fetch and plot a sounding before saving the figure.")
            return

        dlg = ExportDialog(self.root)
        settings = dlg.get_settings()
        if settings:
            ext, dpi = settings
            default_filename = f"skewt_{self.current_sounding.location_name.lower().replace(' ', '_')}_{self.current_sounding.date_str}.{ext}"
            file_types = [("PNG Image", "*.png")] if ext == "png" else ([("PDF Document", "*.pdf")] if ext == "pdf" else [("SVG Vector", "*.svg")])

            filepath = filedialog.asksaveasfilename(
                parent=self.root,
                title="Save Skew-T Figure",
                initialfile=default_filename,
                filetypes=file_types
            )
            if filepath:
                try:
                    fig = SkewTPlotter.create_skewt_figure(self.current_sounding, dpi=dpi, dark_mode=self.dark_mode)
                    SkewTPlotter.save_figure(fig, filepath, dpi=dpi)
                    self.set_status(f"Figure saved to {os.path.basename(filepath)}")
                    show_info_dialog(self.root, "Export Successful", f"Skew-T diagram successfully saved to:\n{filepath}")
                except Exception as e:
                    show_error_dialog(self.root, "Save Error", f"Failed to save figure: {e}")

    def export_csv(self):
        if self.current_sounding is None:
            show_info_dialog(self.root, "No Sounding Data", "Please fetch and plot a sounding before exporting data.")
            return

        default_filename = f"sounding_{self.current_sounding.location_name.lower().replace(' ', '_')}_{self.current_sounding.date_str}.rsf"
        file_types = [
            ("RAOB Sounding Format", "*.rsf"),
            ("RAOB Native ENV Format", "*.env"),
            ("RAOB Compatible CSV", "*.csv"),
            ("RAOB / NOAA Sounding Text", "*.txt"),
            ("Standard App CSV", "*.csv"),
            ("All Files", "*.*")
        ]

        filepath = filedialog.asksaveasfilename(
            parent=self.root,
            title="Export Sounding Data (RAOB RSF / ENV / CSV)",
            initialfile=default_filename,
            filetypes=file_types
        )
        if filepath:
            try:
                if filepath.endswith(".rsf"):
                    self.current_sounding.to_raob_rsf(filepath)
                elif filepath.endswith(".env"):
                    self.current_sounding.to_raob_env(filepath)
                elif filepath.endswith(".csv"):
                    self.current_sounding.to_raob_csv(filepath)
                elif filepath.endswith(".txt") or filepath.endswith(".raob"):
                    self.current_sounding.to_raob_txt(filepath)
                else:
                    self.current_sounding.to_csv(filepath)

                self.set_status(f"Data exported to {os.path.basename(filepath)}")
                show_info_dialog(self.root, "Export Successful", f"Sounding data successfully exported to:\n{filepath}")
            except Exception as e:
                show_error_dialog(self.root, "Export Error", f"Failed to export sounding data: {e}")

    def toggle_dark_theme(self):
        self.dark_mode = not self.dark_mode
        if self.current_sounding:
            fig = SkewTPlotter.create_skewt_figure(self.current_sounding, dark_mode=self.dark_mode)
            self.canvas_widget.set_figure(fig)
        self.set_status(f"Dark mode {'enabled' if self.dark_mode else 'disabled'}.")

    def show_about_dialog(self):
        AboutDialog(self.root)
