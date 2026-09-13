import os
import sys
import tkinter as tk

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ui.widgets import CalendarPopupWidget


def test_calendar_widget():
    print("Testing CalendarPopupWidget click effect & functionality...")
    sys.stdout.flush()
    root = tk.Tk()
    root.withdraw()

    selected_dates = []

    def on_date_selected(date_str):
        selected_dates.append(date_str)
        print(f"Date selected callback invoked with: {date_str}")
        sys.stdout.flush()

    # Initialize popup with specific date: 2026-09-13
    popup = CalendarPopupWidget(root, "2026-09-13", on_date_selected)

    assert popup.current_year == 2026
    assert popup.current_month == 9
    assert popup.selected_day == 13

    # Check button widgets in the grid
    buttons = [w for w in popup.grid_frame.winfo_children() if isinstance(w, tk.Button)]
    assert len(buttons) == 30  # September has 30 days
    print(f"Found {len(buttons)} calendar day buttons for September 2026.")
    sys.stdout.flush()

    # Find the button for day 13
    btn_13 = next(b for b in buttons if b.cget("text") == "13")
    # Day 13 is initially selected, should be SUNKEN
    assert btn_13.cget("relief") == "sunken" or btn_13.cget("relief") == tk.SUNKEN
    assert btn_13.cget("bg") == "#316ac5"

    # Find button for day 20 (unselected, should be RAISED)
    btn_20 = next(b for b in buttons if b.cget("text") == "20")
    assert btn_20.cget("relief") == "raised" or btn_20.cget("relief") == tk.RAISED
    assert btn_20.cget("cursor") == "hand2"

    # Simulate clicking day 20
    print("Simulating click on day 20...")
    sys.stdout.flush()
    popup.on_day_clicked(20)

    assert popup.selected_day == 20
    assert len(selected_dates) == 1
    assert selected_dates[0] == "2026-09-20"

    # Wait for the 120ms destroy timer
    def after_destroy_check():
        print("[SUCCESS] CalendarPopupWidget closed gracefully after click delay.")
        sys.stdout.flush()
        root.destroy()
        os._exit(0)

    root.after(200, after_destroy_check)
    root.mainloop()


if __name__ == "__main__":
    test_calendar_widget()
