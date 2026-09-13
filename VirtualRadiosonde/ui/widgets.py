"""
Custom Tkinter Widgets for Virtual Radiosonde Plotter.
Defines Control Panel, Parameter Display Panel, Matplotlib Canvas Widget,
and a Zero-Dependency Classic Retro Windows XP Calendar Popup.
"""

import calendar
import datetime
from typing import Dict, Any, Optional, List, Tuple, Callable
import tkinter as tk
from tkinter import ttk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from core.sounding import SoundingIndices


class CalendarPopupWidget(tk.Toplevel):
    """
    Zero-dependency classic retro Windows XP Calendar Popup for date picking.
    Uses Python's standard library 'calendar' and renders 3D beveled square day cells.
    """
    WEEKDAY_NAMES = ["Min", "Sen", "Sel", "Rab", "Kam", "Jum", "Sab"]

    def __init__(self, parent: tk.Widget, initial_date_str: str, on_date_selected: Callable[[str], None]):
        super().__init__(parent)
        self.title("Select Date")
        self.resizable(False, False)
        self.configure(bg="#ece9d8")

        self.on_date_selected = on_date_selected

        # Parse initial date (yyyy-MM-dd)
        try:
            parts = [int(p) for p in initial_date_str.split("-")]
            self.current_year = parts[0]
            self.current_month = parts[1]
            self.selected_day = parts[2]
        except Exception:
            today = datetime.date.today()
            self.current_year = today.year
            self.current_month = today.month
            self.selected_day = today.day

        # Make popup transient
        self.transient(parent)
        self.grab_set()

        self.init_ui()
        self.position_near_widget(parent)

    def position_near_widget(self, parent: tk.Widget):
        self.update_idletasks()
        try:
            x = parent.winfo_rootx()
            y = parent.winfo_rooty() + parent.winfo_height() + 2
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass

    def init_ui(self):
        container = tk.Frame(self, bg="#ece9d8", bd=2, relief=tk.RAISED, padx=4, pady=4)
        container.pack(fill=tk.BOTH, expand=True)

        # 1. Navigation Header (< Month Year >)
        nav_frame = tk.Frame(container, bg="#ece9d8", bd=1, relief=tk.GROOVE)
        nav_frame.pack(fill=tk.X, pady=(0, 4))

        btn_prev = tk.Button(
            nav_frame,
            text="<",
            font=("Tahoma", 9, "bold"),
            bg="#ece9d8",
            fg="#000000",
            relief=tk.RAISED,
            bd=2,
            width=2,
            command=self.prev_month
        )
        btn_prev.pack(side=tk.LEFT, padx=2, pady=2)

        self.lbl_month_year = tk.Label(
            nav_frame,
            text=f"{calendar.month_name[self.current_month]} {self.current_year}",
            font=("Tahoma", 9, "bold"),
            bg="#ece9d8",
            fg="#000000"
        )
        self.lbl_month_year.pack(side=tk.LEFT, expand=True)

        btn_next = tk.Button(
            nav_frame,
            text=">",
            font=("Tahoma", 9, "bold"),
            bg="#ece9d8",
            fg="#000000",
            relief=tk.RAISED,
            bd=2,
            width=2,
            command=self.next_month
        )
        btn_next.pack(side=tk.RIGHT, padx=2, pady=2)

        # 2. Weekdays Header
        days_frame = tk.Frame(container, bg="#ece9d8")
        days_frame.pack(fill=tk.X)

        for col, wday in enumerate(self.WEEKDAY_NAMES):
            fg_col = "#cc0000" if col == 0 else ("#0000ff" if col == 6 else "#000000")
            lbl = tk.Label(
                days_frame,
                text=wday,
                font=("Tahoma", 8, "bold"),
                bg="#ece9d8",
                fg=fg_col,
                width=4,
                pady=2,
                relief=tk.GROOVE,
                bd=1
            )
            lbl.grid(row=0, column=col, padx=1, pady=1)

        # 3. Days Grid
        self.grid_frame = tk.Frame(container, bg="#ffffff", bd=1, relief=tk.SUNKEN)
        self.grid_frame.pack(fill=tk.BOTH, expand=True, pady=(2, 0))

        self.render_calendar_days()

    def render_calendar_days(self):
        # Clear existing buttons
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        self.lbl_month_year.config(text=f"{calendar.month_name[self.current_month]} {self.current_year}")

        cal = calendar.Calendar(firstweekday=6)
        month_days = cal.monthdayscalendar(self.current_year, self.current_month)

        for r, week in enumerate(month_days):
            for c, day in enumerate(week):
                if day == 0:
                    lbl_empty = tk.Label(self.grid_frame, text="", bg="#ffffff", width=4, height=1)
                    lbl_empty.grid(row=r, column=c, padx=1, pady=1)
                else:
                    is_selected = (day == self.selected_day)
                    bg_col = "#316ac5" if is_selected else "#ffffff"
                    fg_col = "#ffffff" if is_selected else ("#cc0000" if c == 0 else ("#0000ff" if c == 6 else "#000000"))

                    btn = tk.Button(
                        self.grid_frame,
                        text=str(day),
                        font=("Tahoma", 8, "bold" if is_selected else "normal"),
                        bg=bg_col,
                        fg=fg_col,
                        activebackground="#316ac5",
                        activeforeground="#ffffff",
                        relief=tk.FLAT if is_selected else tk.GROOVE,
                        bd=1,
                        width=3,
                        cursor="hand2",
                        command=lambda d=day: self.on_day_clicked(d)
                    )
                    btn.grid(row=r, column=c, padx=1, pady=1)

    def prev_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.render_calendar_days()

    def next_month(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.render_calendar_days()

    def on_day_clicked(self, day: int):
        date_str = f"{self.current_year:04d}-{self.current_month:02d}-{day:02d}"
        self.on_date_selected(date_str)
        self.destroy()


class ControlPanelWidget(tk.Frame):
    """
    Left panel widget providing inputs for coordinates, date/time, city search, presets, and action buttons.
    Styled with classic Windows XP neutral palette (#ece9d8, Tahoma).
    """
    PRESET_CITIES = [
        ("-- Select Preset Location --", None, None),
        ("Kebumen, Central Java", -7.6686, 109.6536),
        ("Jakarta (Soekarno-Hatta / CGK)", -6.1256, 106.6559),
        ("Surabaya (Juanda / SUB)", -7.3798, 112.7875),
        ("Bandung (Husein / BDO)", -6.9006, 107.5761),
        ("Yogyakarta (YIA)", -7.9073, 110.0544),
        ("Denpasar, Bali (DPS)", -8.7482, 115.1672),
        ("Medan (Kualanamu / KNO)", 3.6422, 98.8853),
        ("Makassar (Sultan Hasanuddin / UPG)", -5.0617, 119.5540),
        ("Singapore (Changi / WSSS)", 1.3644, 103.9915),
        ("Darwin, Australia (YPDN)", -12.4147, 130.8767),
    ]

    def __init__(
        self,
        parent: tk.Widget,
        on_fetch: Callable[[Dict[str, Any]], None],
        on_open_csv: Callable[[], None],
        on_save_figure: Callable[[], None],
        on_export_csv: Callable[[], None],
        on_search_city: Callable[[str], None]
    ):
        super().__init__(parent, bg="#ece9d8", padx=4, pady=4)
        self.on_fetch = on_fetch
        self.on_open_csv = on_open_csv
        self.on_save_figure = on_save_figure
        self.on_export_csv = on_export_csv
        self.on_search_city = on_search_city

        self.init_ui()

    def init_ui(self):
        # 1. Section Title
        lbl_title = tk.Label(
            self,
            text="Configuration",
            font=("Tahoma", 10, "bold"),
            bg="#ece9d8",
            fg="#000080"
        )
        lbl_title.pack(anchor="w", pady=(0, 4))

        # 2. City Search Box Group
        group_search = tk.LabelFrame(
            self,
            text="City Search & Presets",
            font=("Tahoma", 8, "bold"),
            bg="#ece9d8",
            fg="#000000",
            padx=4,
            pady=4
        )
        group_search.pack(fill=tk.X, pady=(0, 6))

        search_bar = tk.Frame(group_search, bg="#ece9d8")
        search_bar.pack(fill=tk.X, pady=(0, 3))

        self.txt_city_search = ttk.Entry(search_bar, font=("Tahoma", 8), width=13)
        self.txt_city_search.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        self.txt_city_search.insert(0, "Kebumen")
        self.txt_city_search.bind("<Return>", lambda e: self.do_search())

        self.btn_search_city = tk.Button(
            search_bar,
            text="Search",
            font=("Tahoma", 8),
            bg="#ece9d8",
            fg="#000000",
            relief=tk.RAISED,
            bd=2,
            padx=4,
            command=self.do_search
        )
        self.btn_search_city.pack(side=tk.RIGHT)

        tk.Label(group_search, text="Preset Location:", font=("Tahoma", 8), bg="#ece9d8", fg="#000000").pack(anchor="w")

        preset_names = [p[0] for p in self.PRESET_CITIES]
        self.combo_presets = ttk.Combobox(
            group_search,
            values=preset_names,
            state="readonly",
            font=("Tahoma", 8),
            width=23
        )
        self.combo_presets.current(1)  # Default Kebumen
        self.combo_presets.pack(fill=tk.X, pady=(2, 0))
        self.combo_presets.bind("<<ComboboxSelected>>", self.on_preset_selected)

        # 3. Location & Time Group
        group_input = tk.LabelFrame(
            self,
            text="Target Sounding Settings",
            font=("Tahoma", 8, "bold"),
            bg="#ece9d8",
            fg="#000000",
            padx=4,
            pady=4
        )
        group_input.pack(fill=tk.X, pady=(0, 6))

        form = tk.Frame(group_input, bg="#ece9d8")
        form.pack(fill=tk.X)

        # Latitude
        tk.Label(form, text="Latitude (°):", font=("Tahoma", 8), bg="#ece9d8", fg="#000000").grid(row=0, column=0, sticky="w", pady=2)
        self.spin_lat = ttk.Spinbox(form, from_=-90.0, to=90.0, increment=0.1, font=("Tahoma", 8), width=11)
        self.spin_lat.set(-7.6686)
        self.spin_lat.grid(row=0, column=1, sticky="e", pady=2)

        # Longitude
        tk.Label(form, text="Longitude (°):", font=("Tahoma", 8), bg="#ece9d8", fg="#000000").grid(row=1, column=0, sticky="w", pady=2)
        self.spin_lon = ttk.Spinbox(form, from_=-180.0, to=180.0, increment=0.1, font=("Tahoma", 8), width=11)
        self.spin_lon.set(109.6536)
        self.spin_lon.grid(row=1, column=1, sticky="e", pady=2)

        # Location Name
        tk.Label(form, text="Location Name:", font=("Tahoma", 8), bg="#ece9d8", fg="#000000").grid(row=2, column=0, sticky="w", pady=2)
        self.txt_loc_name = ttk.Entry(form, font=("Tahoma", 8), width=12)
        self.txt_loc_name.insert(0, "Kebumen")
        self.txt_loc_name.grid(row=2, column=1, sticky="e", pady=2)

        # Date Picker with Popup button
        tk.Label(form, text="Date (UTC):", font=("Tahoma", 8), bg="#ece9d8", fg="#000000").grid(row=3, column=0, sticky="w", pady=2)
        date_bar = tk.Frame(form, bg="#ece9d8")
        date_bar.grid(row=3, column=1, sticky="e", pady=2)

        today_str = datetime.date.today().strftime("%Y-%m-%d")
        self.txt_date = ttk.Entry(date_bar, font=("Tahoma", 8), width=9)
        self.txt_date.insert(0, today_str)
        self.txt_date.pack(side=tk.LEFT, padx=(0, 2))

        self.btn_calendar = tk.Button(
            date_bar,
            text="📅",
            font=("Tahoma", 7),
            bg="#ece9d8",
            fg="#000000",
            relief=tk.RAISED,
            bd=2,
            padx=2,
            pady=0,
            command=self.open_calendar
        )
        self.btn_calendar.pack(side=tk.RIGHT)

        # Time UTC
        tk.Label(form, text="Time (UTC):", font=("Tahoma", 8), bg="#ece9d8", fg="#000000").grid(row=4, column=0, sticky="w", pady=2)
        self.combo_utc_hour = ttk.Combobox(
            form,
            values=["00:00 UTC", "06:00 UTC", "12:00 UTC", "18:00 UTC"],
            state="readonly",
            font=("Tahoma", 8),
            width=11
        )
        self.combo_utc_hour.current(2)  # Default 12:00 UTC
        self.combo_utc_hour.grid(row=4, column=1, sticky="e", pady=2)

        # Data Source
        tk.Label(form, text="Data Source:", font=("Tahoma", 8), bg="#ece9d8", fg="#000000").grid(row=5, column=0, sticky="w", pady=2)
        self.combo_source = ttk.Combobox(
            form,
            values=["ERA5", "GFS", "Radiosonde Observation"],
            state="readonly",
            font=("Tahoma", 8),
            width=11
        )
        self.combo_source.current(0)
        self.combo_source.grid(row=5, column=1, sticky="e", pady=2)

        # 4. Action Buttons Group
        group_actions = tk.LabelFrame(
            self,
            text="Actions",
            font=("Tahoma", 8, "bold"),
            bg="#ece9d8",
            fg="#000000",
            padx=4,
            pady=4
        )
        group_actions.pack(fill=tk.X, pady=(0, 3))

        self.btn_download = tk.Button(
            group_actions,
            text="Fetch & Plot Sounding",
            font=("Tahoma", 8, "bold"),
            bg="#ece9d8",
            fg="#000000",
            activebackground="#f5f4ea",
            relief=tk.RAISED,
            bd=2,
            pady=4,
            command=self.on_fetch_clicked
        )
        self.btn_download.pack(fill=tk.X, pady=(0, 4))

        self.btn_open_csv = tk.Button(
            group_actions,
            text="Open Local CSV",
            font=("Tahoma", 8),
            bg="#ece9d8",
            fg="#000000",
            relief=tk.RAISED,
            bd=2,
            pady=2,
            command=self.on_open_csv
        )
        self.btn_open_csv.pack(fill=tk.X, pady=(0, 3))

        self.btn_save_fig = tk.Button(
            group_actions,
            text="Save Figure (PNG / PDF)",
            font=("Tahoma", 8),
            bg="#ece9d8",
            fg="#000000",
            relief=tk.RAISED,
            bd=2,
            pady=2,
            command=self.on_save_figure
        )
        self.btn_save_fig.pack(fill=tk.X, pady=(0, 3))

        self.btn_export_csv = tk.Button(
            group_actions,
            text="Export CSV Data",
            font=("Tahoma", 8),
            bg="#ece9d8",
            fg="#000000",
            relief=tk.RAISED,
            bd=2,
            pady=2,
            command=self.on_export_csv
        )
        self.btn_export_csv.pack(fill=tk.X)

    def do_search(self):
        query = self.txt_city_search.get().strip()
        if query:
            self.on_search_city(query)

    def open_calendar(self):
        current_date = self.txt_date.get().strip()
        CalendarPopupWidget(
            parent=self.btn_calendar,
            initial_date_str=current_date,
            on_date_selected=lambda d: self.txt_date.delete(0, tk.END) or self.txt_date.insert(0, d)
        )

    def on_preset_selected(self, event=None):
        idx = self.combo_presets.current()
        if idx > 0:
            name, lat, lon = self.PRESET_CITIES[idx]
            self.set_coordinates(lat, lon, name.split(",")[0].strip())

    def set_coordinates(self, lat: float, lon: float, name: str):
        self.spin_lat.set(f"{lat:.4f}")
        self.spin_lon.set(f"{lon:.4f}")
        self.txt_loc_name.delete(0, tk.END)
        self.txt_loc_name.insert(0, name)

    def on_fetch_clicked(self):
        try:
            lat = float(self.spin_lat.get())
            lon = float(self.spin_lon.get())
        except ValueError:
            return

        loc_name = self.txt_loc_name.get().strip() or "Custom Location"
        date_str = self.txt_date.get().strip()
        utc_text = self.combo_utc_hour.get()
        target_utc_hour = int(utc_text.split(":")[0])
        source = self.combo_source.get()

        config = {
            "latitude": lat,
            "longitude": lon,
            "location_name": loc_name,
            "date_str": date_str,
            "target_utc_hour": target_utc_hour,
            "source": source
        }
        self.on_fetch(config)


class PlotCanvasWidget(tk.Frame):
    """
    Matplotlib Tkinter Canvas widget embedding Skew-T diagrams with navigation toolbar.
    """
    def __init__(self, parent: tk.Widget):
        super().__init__(parent, bg="#ffffff", bd=1, relief=tk.SUNKEN)
        self.canvas: Optional[FigureCanvasTkAgg] = None
        self.toolbar: Optional[NavigationToolbar2Tk] = None

        self.lbl_placeholder = tk.Label(
            self,
            text="Click 'Fetch & Plot Sounding' or 'Open Local CSV' to generate a Skew-T diagram.",
            font=("Tahoma", 11, "bold"),
            bg="#ffffff",
            fg="#555555"
        )
        self.lbl_placeholder.pack(expand=True)

    def set_figure(self, fig: plt.Figure):
        if self.lbl_placeholder:
            self.lbl_placeholder.destroy()
            self.lbl_placeholder = None

        if self.toolbar:
            self.toolbar.destroy()
            self.toolbar = None

        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None

        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        self.toolbar.pack(side=tk.BOTTOM, fill=tk.X)


class ParameterDisplayWidget(tk.Frame):
    """
    Right panel widget displaying meteorological sounding indices, key levels, and severe risk badges.
    """
    def __init__(self, parent: tk.Widget, on_copy_summary: Callable[[], None]):
        super().__init__(parent, bg="#ece9d8", padx=4, pady=4)
        self.on_copy_summary = on_copy_summary

        self.init_ui()

    def init_ui(self):
        lbl_title = tk.Label(
            self,
            text="Sounding Parameters",
            font=("Tahoma", 10, "bold"),
            bg="#ece9d8",
            fg="#000080"
        )
        lbl_title.pack(anchor="w", pady=(0, 4))

        # Canvas with Scrollbar for vertical scrolling
        container = tk.Frame(self, bg="#ece9d8")
        container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(container, bg="#ece9d8", highlightthickness=0, width=225)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.scroll_content = tk.Frame(canvas, bg="#ece9d8")

        self.scroll_content.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.scroll_content, anchor="nw", width=225)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 1. Severe Weather Risk Assessment Box
        group_threat = tk.LabelFrame(
            self.scroll_content,
            text="Severe Weather Threat Risk",
            font=("Tahoma", 8, "bold"),
            bg="#ece9d8",
            fg="#000000",
            padx=4,
            pady=4
        )
        group_threat.pack(fill=tk.X, pady=(0, 6))

        self.lbl_ts_threat = tk.Label(
            group_threat,
            text="⚡ Thunderstorm: N/A",
            font=("Tahoma", 8, "bold"),
            bg="#10b981",
            fg="#ffffff",
            relief=tk.SOLID,
            bd=1,
            pady=2
        )
        self.lbl_ts_threat.pack(fill=tk.X, pady=2)

        self.lbl_rain_threat = tk.Label(
            group_threat,
            text="🌧️ Heavy Rain: N/A",
            font=("Tahoma", 8, "bold"),
            bg="#10b981",
            fg="#ffffff",
            relief=tk.SOLID,
            bd=1,
            pady=2
        )
        self.lbl_rain_threat.pack(fill=tk.X, pady=2)

        self.lbl_wind_threat = tk.Label(
            group_threat,
            text="🌪️ Wind Shear: N/A",
            font=("Tahoma", 8, "bold"),
            bg="#10b981",
            fg="#ffffff",
            relief=tk.SOLID,
            bd=1,
            pady=2
        )
        self.lbl_wind_threat.pack(fill=tk.X, pady=2)

        # 2. Surface & Key Levels Table
        self.tree_levels = self._create_param_tree(
            self.scroll_content,
            "Surface & Lifted Levels",
            ["Param", "Level", "Value"],
            [76, 52, 74],
            6
        )

        # 3. Convective Energy (CAPE / CIN) Table
        self.tree_cape = self._create_param_tree(
            self.scroll_content,
            "Convective Energy",
            ["Parcel", "CAPE", "CIN"],
            [80, 58, 58],
            3
        )

        # 4. Stability & Severe Indices Table
        self.tree_indices = self._create_param_tree(
            self.scroll_content,
            "Stability & Severe Indices",
            ["Index", "Value", "Unit"],
            [94, 56, 44],
            8
        )

        # Copy Summary Button
        self.btn_copy_summary = tk.Button(
            self.scroll_content,
            text="📋 Copy Summary Text",
            font=("Tahoma", 8, "bold"),
            bg="#ece9d8",
            fg="#000000",
            relief=tk.RAISED,
            bd=2,
            pady=3,
            command=self.on_copy_summary
        )
        self.btn_copy_summary.pack(fill=tk.X, pady=(4, 4))

        self.clear_display()

    def _create_param_tree(
        self,
        parent: tk.Widget,
        title: str,
        columns: List[str],
        widths: List[int],
        height: int
    ) -> ttk.Treeview:
        group = tk.LabelFrame(
            parent,
            text=title,
            font=("Tahoma", 8, "bold"),
            bg="#ece9d8",
            fg="#000000",
            padx=2,
            pady=2
        )
        group.pack(fill=tk.X, pady=(0, 6))

        tree = ttk.Treeview(group, columns=columns, show="headings", height=height)
        for col, width in zip(columns, widths):
            tree.heading(col, text=col)
            tree.column(col, width=width, anchor="center")

        tree.pack(fill=tk.X)
        return tree

    def _fmt(self, val: Optional[float], fmt: str = ".1f") -> str:
        if val is None:
            return "N/A"
        try:
            return f"{val:{fmt}}"
        except Exception:
            return str(val)

    def _populate_tree(self, tree: ttk.Treeview, data: List[Tuple[str, ...]]):
        for item in tree.get_children():
            tree.delete(item)
        for row in data:
            tree.insert("", tk.END, values=row)

    def clear_display(self):
        self.update_indices(SoundingIndices())

    def update_indices(self, indices: SoundingIndices):
        threats = indices.get_threat_assessment()

        self.lbl_ts_threat.config(
            text=f"⚡ Thunderstorm: {threats['thunderstorm']['level']}",
            bg=threats['thunderstorm']['color']
        )
        self.lbl_rain_threat.config(
            text=f"🌧️ Heavy Rain: {threats['heavy_rain']['level']}",
            bg=threats['heavy_rain']['color']
        )
        self.lbl_wind_threat.config(
            text=f"🌪️ Wind Shear: {threats['wind_shear']['level']}",
            bg=threats['wind_shear']['color']
        )

        cbh_val = f"{self._fmt(indices.lcl_height_m, '.0f')} m"
        levels_data = [
            ("Sfc Temp", "-", f"{self._fmt(indices.surface_temp_c)} °C"),
            ("Sfc Dewpt", "-", f"{self._fmt(indices.surface_dewpoint_c)} °C"),
            ("LCL", f"{self._fmt(indices.lcl_pressure_hpa, '.0f')} hPa", f"{self._fmt(indices.lcl_temp_c)} °C"),
            ("Cloud Base", f"{self._fmt(indices.lcl_pressure_hpa, '.0f')} hPa", cbh_val),
            ("LFC", f"{self._fmt(indices.lfc_pressure_hpa, '.0f')} hPa", f"{self._fmt(indices.lfc_temp_c)} °C"),
            ("EL", f"{self._fmt(indices.el_pressure_hpa, '.0f')} hPa", f"{self._fmt(indices.el_temp_c)} °C"),
        ]
        self._populate_tree(self.tree_levels, levels_data)

        cape_data = [
            ("Surface (SB)", self._fmt(indices.sb_cape, ".0f"), self._fmt(indices.sb_cin, ".0f")),
            ("Mixed (ML)", self._fmt(indices.ml_cape, ".0f"), self._fmt(indices.ml_cin, ".0f")),
            ("Unstable (MU)", self._fmt(indices.mu_cape, ".0f"), self._fmt(indices.mu_cin, ".0f")),
        ]
        self._populate_tree(self.tree_cape, cape_data)

        pwat_val = f"{self._fmt(indices.pwat_mm, '.1f')} mm"
        indices_data = [
            ("PWAT", pwat_val, "mm"),
            ("K-Index", self._fmt(indices.k_index), "°C"),
            ("Total Totals", self._fmt(indices.total_totals), "°C"),
            ("Lifted Index", self._fmt(indices.lifted_index), "°C"),
            ("Showalter", self._fmt(indices.showalter_index), "°C"),
            ("SWEAT Index", self._fmt(indices.sweat_index, ".0f"), "-"),
            ("SRH (0-1 km)", self._fmt(indices.srh_0_1km, ".0f"), "m²/s²"),
            ("SRH (0-3 km)", self._fmt(indices.srh_0_3km, ".0f"), "m²/s²"),
        ]
        self._populate_tree(self.tree_indices, indices_data)
