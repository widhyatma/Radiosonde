"""
Dialogs Module for Virtual Radiosonde Plotter (Tkinter).
Defines AboutDialog, ExportDialog, and high-contrast message boxes with classic retro styling.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Tuple
from .icon_utils import apply_window_icon


def show_error_dialog(parent: Optional[tk.Widget], title: str, message: str) -> None:
    """Displays a standard error message box."""
    messagebox.showerror(title, message, parent=parent)


def show_info_dialog(parent: Optional[tk.Widget], title: str, message: str) -> None:
    """Displays a standard information message box."""
    messagebox.showinfo(title, message, parent=parent)


class AboutDialog(tk.Toplevel):
    """
    About Dialog displaying Jerukagung Meteorologi organization information.
    Styled with classic Windows XP neutral palette (#ece9d8, Tahoma).
    """
    def __init__(self, parent: tk.Widget):
        super().__init__(parent)
        self.title("About - Jerukagung Meteorologi")
        self.geometry("450x340")
        self.resizable(False, False)
        self.configure(bg="#ece9d8")
        apply_window_icon(self)

        # Make modal
        self.transient(parent)
        self.grab_set()

        self.init_ui()
        self.center_window(parent)

    def center_window(self, parent: tk.Widget):
        self.update_idletasks()
        try:
            px = parent.winfo_rootx()
            py = parent.winfo_rooty()
            pw = parent.winfo_width()
            ph = parent.winfo_height()
            w = self.winfo_width()
            h = self.winfo_height()
            x = px + max(0, (pw - w) // 2)
            y = py + max(0, (ph - h) // 2)
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass

    def init_ui(self):
        container = tk.Frame(self, bg="#ece9d8", padx=16, pady=16)
        container.pack(fill=tk.BOTH, expand=True)

        lbl_app = tk.Label(
            container,
            text="Virtual Radiosonde Plotter",
            font=("Tahoma", 13, "bold"),
            bg="#ece9d8",
            fg="#000080"
        )
        lbl_app.pack(pady=(0, 4))

        lbl_org = tk.Label(
            container,
            text="Jerukagung Meteorologi",
            font=("Tahoma", 10, "bold"),
            bg="#ece9d8",
            fg="#000000"
        )
        lbl_org.pack(pady=(0, 2))

        lbl_ver = tk.Label(
            container,
            text="Version 1.0.0 (Tkinter / MetPy)",
            font=("Tahoma", 9),
            bg="#ece9d8",
            fg="#555555"
        )
        lbl_ver.pack(pady=(0, 10))

        desc_text = (
            "Aplikasi analisis termodinamika atmosfer dan visualisasi diagram Skew-T Log-P "
            "standar riset meteorologi.\n\n"
            "Organisasi: Jerukagung Meteorologi\n"
            "Core Engine: MetPy & Pint\n"
            "Visualisasi: Matplotlib Skew-T Log-P (TkAgg)\n"
            "Sumber Data: ERA5 / Weather Model\n"
            "GUI Framework: Python Tkinter"
        )
        lbl_desc = tk.Label(
            container,
            text=desc_text,
            font=("Tahoma", 9),
            bg="#ece9d8",
            fg="#000000",
            justify=tk.LEFT,
            wraplength=410
        )
        lbl_desc.pack(fill=tk.X, expand=True, pady=(0, 14))

        btn_close = tk.Button(
            container,
            text="Tutup",
            font=("Tahoma", 9),
            bg="#ece9d8",
            fg="#000000",
            activebackground="#f5f4ea",
            relief=tk.RAISED,
            bd=2,
            width=12,
            pady=2,
            command=self.destroy
        )
        btn_close.pack()


class ExportDialog(tk.Toplevel):
    """
    Dialog for configuring image export settings (PNG, PDF, SVG, DPI).
    """
    def __init__(self, parent: tk.Widget):
        super().__init__(parent)
        self.title("Export Skew-T Figure")
        self.geometry("380x200")
        self.resizable(False, False)
        self.configure(bg="#ece9d8")
        apply_window_icon(self)

        self.result: Optional[Tuple[str, int]] = None

        self.transient(parent)
        self.grab_set()

        self.init_ui()
        self.center_window(parent)

    def center_window(self, parent: tk.Widget):
        self.update_idletasks()
        try:
            px = parent.winfo_rootx()
            py = parent.winfo_rooty()
            pw = parent.winfo_width()
            ph = parent.winfo_height()
            w = self.winfo_width()
            h = self.winfo_height()
            x = px + max(0, (pw - w) // 2)
            y = py + max(0, (ph - h) // 2)
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass

    def init_ui(self):
        container = tk.Frame(self, bg="#ece9d8", padx=16, pady=14)
        container.pack(fill=tk.BOTH, expand=True)

        lbl_title = tk.Label(
            container,
            text="💾 Export Settings",
            font=("Tahoma", 11, "bold"),
            bg="#ece9d8",
            fg="#000080"
        )
        lbl_title.pack(anchor="w", pady=(0, 10))

        form_frame = tk.Frame(container, bg="#ece9d8")
        form_frame.pack(fill=tk.X, expand=True)

        tk.Label(form_frame, text="Format Gambar:", font=("Tahoma", 9, "bold"), bg="#ece9d8", fg="#000000").grid(
            row=0, column=0, sticky="w", pady=6
        )
        self.combo_format = ttk.Combobox(
            form_frame,
            values=["PNG Image (*.png)", "PDF Document (*.pdf)", "SVG Vector (*.svg)"],
            state="readonly",
            width=22,
            font=("Tahoma", 9)
        )
        self.combo_format.current(0)
        self.combo_format.grid(row=0, column=1, sticky="e", padx=(10, 0), pady=6)

        tk.Label(form_frame, text="Resolusi (DPI):", font=("Tahoma", 9, "bold"), bg="#ece9d8", fg="#000000").grid(
            row=1, column=0, sticky="w", pady=6
        )
        self.spin_dpi = ttk.Spinbox(
            form_frame,
            from_=72,
            to=600,
            increment=50,
            width=21,
            font=("Tahoma", 9)
        )
        self.spin_dpi.set(300)
        self.spin_dpi.grid(row=1, column=1, sticky="e", padx=(10, 0), pady=6)

        # Buttons
        btn_frame = tk.Frame(container, bg="#ece9d8")
        btn_frame.pack(fill=tk.X, pady=(16, 0))

        btn_cancel = tk.Button(
            btn_frame,
            text="Batal",
            font=("Tahoma", 9),
            bg="#ece9d8",
            fg="#000000",
            relief=tk.RAISED,
            bd=2,
            width=10,
            command=self.destroy
        )
        btn_cancel.pack(side=tk.RIGHT, padx=(6, 0))

        btn_save = tk.Button(
            btn_frame,
            text="Simpan...",
            font=("Tahoma", 9, "bold"),
            bg="#ece9d8",
            fg="#000000",
            relief=tk.RAISED,
            bd=2,
            width=10,
            command=self.on_save
        )
        btn_save.pack(side=tk.RIGHT)

    def on_save(self):
        fmt_text = self.combo_format.get()
        if "pdf" in fmt_text:
            ext = "pdf"
        elif "svg" in fmt_text:
            ext = "svg"
        else:
            ext = "png"

        try:
            dpi = int(self.spin_dpi.get())
        except ValueError:
            dpi = 300

        self.result = (ext, dpi)
        self.destroy()

    def get_settings(self) -> Optional[Tuple[str, int]]:
        self.wait_window()
        return self.result
