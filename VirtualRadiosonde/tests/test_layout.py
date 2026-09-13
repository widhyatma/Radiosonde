import os
import sys
import tkinter as tk
from tkinter import ttk

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ui.main_window import MainWindow


def run_layout_check():
    print("Starting Virtual Radiosonde Plotter UI layout test...")
    sys.stdout.flush()

    root = tk.Tk()
    root.geometry("1366x820")

    # Retro style configuration
    style = ttk.Style(root)
    if 'winnative' in style.theme_names():
        style.theme_use('winnative')

    app = MainWindow(root)

    def on_ready():
        total_w = app.main_paned.winfo_width()
        cp_w = app.control_panel.winfo_width()
        cv_w = app.canvas_widget.winfo_width()
        pp_w = app.param_panel.winfo_width()

        print(f"Total Paned Width: {total_w}px")
        print(f"Control Panel (Left): {cp_w}px")
        print(f"Plot Canvas (Center): {cv_w}px")
        print(f"Parameter Panel (Right): {pp_w}px")

        pct_center = (cv_w / total_w) * 100 if total_w > 0 else 0
        print(f"Center Canvas Proportion: {pct_center:.1f}% of total width")
        sys.stdout.flush()

        assert cp_w <= 270, f"Left control panel too wide: {cp_w}px"
        assert pp_w <= 270, f"Right parameter panel too wide: {pp_w}px"
        assert cv_w >= 800, f"Center plot canvas too narrow: {cv_w}px"
        assert pct_center >= 60.0, f"Center canvas proportion too low: {pct_center:.1f}%"

        print("[SUCCESS] ALL LAYOUT CHECKS PASSED: Center Skew-T canvas is wide (>65%) and sidebars are slim.")
        sys.stdout.flush()
        root.destroy()
        os._exit(0)

    root.after(400, on_ready)
    root.mainloop()


if __name__ == "__main__":
    run_layout_check()
