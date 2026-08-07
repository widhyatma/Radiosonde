"""
Custom PySide6 Widgets for Virtual Radiosonde Plotter.
Defines Control Panel, Parameter Display Panel, and Matplotlib Canvas Widget.
"""

from typing import Dict, Any, Optional, List
import numpy as np
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QLineEdit, QDoubleSpinBox, QDateEdit, QComboBox,
    QPushButton, QFrame, QScrollArea, QTableWidget, QTableWidgetItem,
    QHeaderView, QSizePolicy
)

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

from core.sounding import SoundingIndices


class ControlPanelWidget(QWidget):
    """
    Left panel widget providing inputs for coordinates, date/time, city search, presets, and action buttons.
    """
    fetch_requested = Signal(dict)
    save_figure_requested = Signal()
    export_csv_requested = Signal()
    open_csv_requested = Signal()
    search_city_requested = Signal(str)

    PRESET_CITIES = [
        ("Custom Coordinates", None, None),
        ("Kebumen", -7.6686, 109.6536),
        ("Jakarta", -6.2088, 106.8456),
        ("Bandung", -6.9175, 107.6191),
        ("Surabaya", -7.2575, 112.7521),
        ("Yogyakarta", -7.7956, 110.3695),
        ("Medan", 3.5952, 98.6722),
        ("Makassar", -5.1477, 119.4327),
        ("Denpasar", -8.6705, 115.2126),
        ("Jayapura", -2.5489, 140.7196),
    ]

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)

        # Title
        lbl_title = QLabel("Configuration")
        lbl_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #1e3a8a;")
        layout.addWidget(lbl_title)

        # 1. City Search Box
        group_search = QGroupBox("City Search & Presets")
        search_layout = QVBoxLayout(group_search)
        search_layout.setSpacing(8)

        search_input_layout = QHBoxLayout()
        self.txt_city_search = QLineEdit()
        self.txt_city_search.setPlaceholderText("Search city (e.g. Bandung, Jakarta)")
        self.btn_search_city = QPushButton("Search")
        self.btn_search_city.setStyleSheet("background-color: #0284c7; color: white; font-weight: bold;")
        
        search_input_layout.addWidget(self.txt_city_search)
        search_input_layout.addWidget(self.btn_search_city)

        # Presets dropdown
        self.combo_presets = QComboBox()
        for name, lat, lon in self.PRESET_CITIES:
            label = f"{name} ({lat:.2f}°, {lon:.2f}°)" if lat is not None else name
            self.combo_presets.addItem(label)
        self.combo_presets.setCurrentIndex(1)  # Default Kebumen

        search_layout.addLayout(search_input_layout)
        search_layout.addWidget(QLabel("Preset Location:"))
        search_layout.addWidget(self.combo_presets)

        layout.addWidget(group_search)

        # 2. Location & Time Group
        group_input = QGroupBox("Target Sounding Settings")
        form = QFormLayout(group_input)
        form.setSpacing(10)

        self.spin_lat = QDoubleSpinBox()
        self.spin_lat.setRange(-90.0, 90.0)
        self.spin_lat.setDecimals(4)
        self.spin_lat.setValue(-7.6686)

        self.spin_lon = QDoubleSpinBox()
        self.spin_lon.setRange(-180.0, 180.0)
        self.spin_lon.setDecimals(4)
        self.spin_lon.setValue(109.6536)

        self.txt_loc_name = QLineEdit("Kebumen")
        self.txt_loc_name.setPlaceholderText("e.g. Kebumen, Jakarta")

        self.date_picker = QDateEdit()
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setDate(QDate.currentDate())
        self.date_picker.setDisplayFormat("yyyy-MM-dd")

        self.combo_utc_hour = QComboBox()
        self.combo_utc_hour.addItems(["00:00 UTC", "06:00 UTC", "12:00 UTC", "18:00 UTC"])
        self.combo_utc_hour.setCurrentIndex(2)  # Default 12:00 UTC

        self.combo_source = QComboBox()
        self.combo_source.addItems(["ERA5", "GFS", "Radiosonde Observation"])

        form.addRow("Latitude (°):", self.spin_lat)
        form.addRow("Longitude (°):", self.spin_lon)
        form.addRow("Location Name:", self.txt_loc_name)
        form.addRow("Date (UTC):", self.date_picker)
        form.addRow("Time (UTC):", self.combo_utc_hour)
        form.addRow("Data Source:", self.combo_source)

        layout.addWidget(group_input)

        # 3. Action Buttons
        group_actions = QGroupBox("Actions")
        btn_layout = QVBoxLayout(group_actions)
        btn_layout.setSpacing(8)

        self.btn_download = QPushButton("Fetch & Plot Sounding")
        self.btn_download.setMinimumHeight(40)
        self.btn_download.setStyleSheet("""
            QPushButton {
                background-color: #1d4ed8;
                color: #ffffff;
                font-weight: bold;
                font-size: 13px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #1e40af;
            }
            QPushButton:disabled {
                background-color: #94a3b8;
                color: #ffffff;
            }
        """)

        self.btn_open_csv = QPushButton("Open Local CSV")
        self.btn_open_csv.setMinimumHeight(35)
        self.btn_open_csv.setStyleSheet("font-weight: bold; color: #0f172a; background-color: #e0f2fe; border: 1px solid #0284c7;")

        self.btn_save_fig = QPushButton("Save Figure (PNG / PDF)")
        self.btn_save_fig.setMinimumHeight(35)
        self.btn_save_fig.setStyleSheet("font-weight: bold; color: #0f172a; background-color: #f1f5f9; border: 1px solid #94a3b8;")

        self.btn_export_csv = QPushButton("Export CSV Data")
        self.btn_export_csv.setMinimumHeight(35)
        self.btn_export_csv.setStyleSheet("font-weight: bold; color: #0f172a; background-color: #f1f5f9; border: 1px solid #94a3b8;")

        btn_layout.addWidget(self.btn_download)
        btn_layout.addWidget(self.btn_open_csv)
        btn_layout.addWidget(self.btn_save_fig)
        btn_layout.addWidget(self.btn_export_csv)

        layout.addWidget(group_actions)
        layout.addStretch()

        # Connect signals
        self.btn_download.clicked.connect(self._on_download_clicked)
        self.btn_save_fig.clicked.connect(self.save_figure_requested.emit)
        self.btn_export_csv.clicked.connect(self.export_csv_requested.emit)
        self.btn_open_csv.clicked.connect(self.open_csv_requested.emit)
        
        self.btn_search_city.clicked.connect(self._on_search_clicked)
        self.txt_city_search.returnPressed.connect(self._on_search_clicked)
        self.combo_presets.currentIndexChanged.connect(self._on_preset_changed)

    def _on_search_clicked(self):
        query = self.txt_city_search.text().strip()
        if query:
            self.search_city_requested.emit(query)

    def _on_preset_changed(self, idx: int):
        if idx >= 0 and idx < len(self.PRESET_CITIES):
            name, lat, lon = self.PRESET_CITIES[idx]
            if lat is not None and lon is not None:
                self.spin_lat.setValue(lat)
                self.spin_lon.setValue(lon)
                self.txt_loc_name.setText(name)

    def set_coordinates(self, lat: float, lon: float, name: str):
        """Sets form fields when city search is completed."""
        self.spin_lat.setValue(lat)
        self.spin_lon.setValue(lon)
        self.txt_loc_name.setText(name)

    def _on_download_clicked(self):
        utc_text = self.combo_utc_hour.currentText()
        utc_hour = int(utc_text.split(":")[0])

        config = {
            "latitude": self.spin_lat.value(),
            "longitude": self.spin_lon.value(),
            "location_name": self.txt_loc_name.text().strip() or "Target Location",
            "date_str": self.date_picker.date().toString("yyyy-MM-dd"),
            "target_utc_hour": utc_hour,
            "source": self.combo_source.currentText(),
        }
        self.fetch_requested.emit(config)


class ParameterDisplayWidget(QWidget):
    """
    Right panel widget displaying calculated thermodynamic parameters, threat assessments, and copy action.
    """
    copy_summary_requested = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)

        lbl_title = QLabel("Sounding Parameters")
        lbl_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #047857;")
        main_layout.addWidget(lbl_title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background-color: #ffffff; border: none; }")

        container = QWidget()
        container.setStyleSheet("QWidget { background-color: #ffffff; color: #0f172a; }")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # 1. Severe Weather Risk Assessment Box
        group_threat = QGroupBox("Severe Weather Threat Risk")
        gt_layout = QVBoxLayout(group_threat)
        gt_layout.setSpacing(6)

        self.lbl_ts_threat = QLabel("Thunderstorm: N/A")
        self.lbl_rain_threat = QLabel("Heavy Rain: N/A")
        self.lbl_wind_threat = QLabel("Wind Shear: N/A")

        for lbl in [self.lbl_ts_threat, self.lbl_rain_threat, self.lbl_wind_threat]:
            lbl.setStyleSheet("font-weight: bold; font-size: 11px; padding: 5px; border-radius: 4px; color: #0f172a; background-color: #f1f5f9;")
            gt_layout.addWidget(lbl)

        layout.addWidget(group_threat)

        # 2. Surface & Key Levels Table
        self.table_levels = self._create_param_table(["Parameter", "Pressure", "Value"])
        group_levels = QGroupBox("Surface & Lifted Levels")
        gl_layout = QVBoxLayout(group_levels)
        gl_layout.setContentsMargins(4, 8, 4, 4)
        gl_layout.addWidget(self.table_levels)
        layout.addWidget(group_levels)

        # 3. Convective Energy (CAPE / CIN) Table
        self.table_cape = self._create_param_table(["Parcel Type", "CAPE (J/kg)", "CIN (J/kg)"])
        group_cape = QGroupBox("Convective Energy")
        gc_layout = QVBoxLayout(group_cape)
        gc_layout.setContentsMargins(4, 8, 4, 4)
        gc_layout.addWidget(self.table_cape)
        layout.addWidget(group_cape)

        # 4. Moisture & Stability Indices Table
        self.table_indices = self._create_param_table(["Stability Index", "Value", "Unit"])
        group_indices = QGroupBox("Stability & Severe Indices")
        gi_layout = QVBoxLayout(group_indices)
        gi_layout.setContentsMargins(4, 8, 4, 4)
        gi_layout.addWidget(self.table_indices)
        layout.addWidget(group_indices)

        # Style QGroupBoxes cleanly
        for grp in [group_threat, group_levels, group_cape, group_indices]:
            grp.setStyleSheet("""
                QGroupBox {
                    font-weight: bold;
                    border: 1px solid #cbd5e1;
                    border-radius: 6px;
                    margin-top: 6px;
                    padding-top: 10px;
                    background-color: #ffffff;
                    color: #0f172a;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 0 4px;
                    color: #1e293b;
                }
            """)

        # Copy Summary Button
        self.btn_copy_summary = QPushButton("Copy Summary Text")
        self.btn_copy_summary.setMinimumHeight(35)
        self.btn_copy_summary.setStyleSheet("font-weight: bold; color: #ffffff; background-color: #059669; border-radius: 4px;")
        self.btn_copy_summary.clicked.connect(self.copy_summary_requested.emit)
        layout.addWidget(self.btn_copy_summary)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        # Set initial empty state
        self.clear_display()

    def _create_param_table(self, headers: List[str]) -> QTableWidget:
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionMode(QTableWidget.NoSelection)
        table.setShowGrid(True)
        table.setStyleSheet("""
            QTableWidget {
                font-size: 11px;
                gridline-color: #cbd5e1;
                background-color: #ffffff;
                color: #0f172a;
                border: 1px solid #cbd5e1;
            }
            QTableWidget::item {
                background-color: #ffffff;
                color: #0f172a;
                padding: 4px;
            }
            QHeaderView::section {
                background-color: #e2e8f0;
                color: #0f172a;
                font-weight: bold;
                padding: 4px;
                border: 1px solid #cbd5e1;
            }
        """)
        return table

    def clear_display(self):
        """Resets all parameter tables to N/A."""
        self.update_indices(SoundingIndices())

    def update_indices(self, indices: SoundingIndices):
        """Populates parameter tables and threat risks with computed SoundingIndices."""
        # 1. Threats
        threats = indices.get_threat_assessment()

        self.lbl_ts_threat.setText(f"⚡ Thunderstorm: {threats['thunderstorm']['level']}")
        self.lbl_ts_threat.setStyleSheet(f"font-weight: bold; font-size: 11px; padding: 5px; color: #ffffff; background-color: {threats['thunderstorm']['color']}; border-radius: 4px;")

        self.lbl_rain_threat.setText(f"🌧️ Heavy Rain: {threats['heavy_rain']['level']}")
        self.lbl_rain_threat.setStyleSheet(f"font-weight: bold; font-size: 11px; padding: 5px; color: #ffffff; background-color: {threats['heavy_rain']['color']}; border-radius: 4px;")

        self.lbl_wind_threat.setText(f"🌪️ Wind Shear: {threats['wind_shear']['level']}")
        self.lbl_wind_threat.setStyleSheet(f"font-weight: bold; font-size: 11px; padding: 5px; color: #ffffff; background-color: {threats['wind_shear']['color']}; border-radius: 4px;")

        # 2. Levels Table
        cbh_val = f"{self._fmt(indices.lcl_height_m, '.0f')} m ({self._fmt(indices.lcl_height_ft, '.0f')} ft)"
        levels_data = [
            ("Surface Temp", "-", f"{self._fmt(indices.surface_temp_c)} °C"),
            ("Surface Dewpoint", "-", f"{self._fmt(indices.surface_dewpoint_c)} °C"),
            ("LCL (Lifted Cond.)", f"{self._fmt(indices.lcl_pressure_hpa, '.0f')} hPa", f"{self._fmt(indices.lcl_temp_c)} °C"),
            ("Cloud Base Height", f"{self._fmt(indices.lcl_pressure_hpa, '.0f')} hPa", cbh_val),
            ("LFC (Free Conv.)", f"{self._fmt(indices.lfc_pressure_hpa, '.0f')} hPa", f"{self._fmt(indices.lfc_temp_c)} °C"),
            ("EL (Equilibrium)", f"{self._fmt(indices.el_pressure_hpa, '.0f')} hPa", f"{self._fmt(indices.el_temp_c)} °C"),
        ]
        self._populate_table(self.table_levels, levels_data)

        # 3. CAPE / CIN Table
        cape_data = [
            ("Surface-Based (SB)", self._fmt(indices.sb_cape, ".0f"), self._fmt(indices.sb_cin, ".0f")),
            ("Mixed-Layer (ML)", self._fmt(indices.ml_cape, ".0f"), self._fmt(indices.ml_cin, ".0f")),
            ("Most-Unstable (MU)", self._fmt(indices.mu_cape, ".0f"), self._fmt(indices.mu_cin, ".0f")),
        ]
        self._populate_table(self.table_cape, cape_data)

        # 4. Stability Indices Table
        indices_data = [
            ("Precipitable Water (PWAT)", f"{self._fmt(indices.pwat_mm, '.1f')} mm", f"({self._fmt(indices.pwat_in, '.2f')} in)"),
            ("K Index (KI)", self._fmt(indices.k_index, ".1f"), "°C"),
            ("Total Totals (TT)", self._fmt(indices.total_totals, ".1f"), "°C"),
            ("Lifted Index (LI)", self._fmt(indices.lifted_index, ".1f"), "°C"),
            ("Showalter Index (SI)", self._fmt(indices.showalter_index, ".1f"), "°C"),
            ("SWEAT Index", self._fmt(indices.sweat_index, ".0f"), "-"),
            ("0-1km SRH", self._fmt(indices.srh_0_1km, ".0f"), "m²/s²"),
            ("0-3km SRH", self._fmt(indices.srh_0_3km, ".0f"), "m²/s²"),
        ]
        self._populate_table(self.table_indices, indices_data)

    def _fmt(self, val: Optional[float], fmt_spec: str = ".1f") -> str:
        if val is None or np.isnan(val):
            return "N/A"
        return f"{val:{fmt_spec}}"

    def _populate_table(self, table: QTableWidget, data: List[tuple]):
        table.setRowCount(len(data))
        for row, row_data in enumerate(data):
            for col, item_text in enumerate(row_data):
                item = QTableWidgetItem(str(item_text))
                item.setTextAlignment(Qt.AlignCenter)
                table.setItem(row, col, item)
        row_height = 24
        header_height = 28
        total_height = header_height + (row_height * len(data)) + 6
        table.setFixedHeight(total_height)
        row_height = 24
        header_height = 28
        total_height = header_height + (row_height * len(data)) + 6
        table.setFixedHeight(total_height)


class PlotCanvasWidget(QWidget):
    """
    Matplotlib Qt Canvas widget embedding Skew-T diagrams with navigation toolbar.
    """
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.canvas: Optional[FigureCanvas] = None
        self.toolbar: Optional[NavigationToolbar] = None
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.lbl_placeholder = QLabel("Click 'Fetch & Plot Sounding' or 'Open Local CSV' to generate a Skew-T diagram.")
        self.lbl_placeholder.setAlignment(Qt.AlignCenter)
        self.lbl_placeholder.setStyleSheet("font-size: 14px; font-weight: bold; color: #475569;")
        self.layout.addWidget(self.lbl_placeholder)

    def set_figure(self, fig: plt.Figure):
        """Replaces current canvas with the new figure."""
        if self.lbl_placeholder:
            self.layout.removeWidget(self.lbl_placeholder)
            self.lbl_placeholder.deleteLater()
            self.lbl_placeholder = None

        if self.canvas:
            self.layout.removeWidget(self.toolbar)
            self.layout.removeWidget(self.canvas)
            self.toolbar.deleteLater()
            self.canvas.deleteLater()

        self.canvas = FigureCanvas(fig)
        self.toolbar = NavigationToolbar(self.canvas, self)

        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)
        self.canvas.draw()
