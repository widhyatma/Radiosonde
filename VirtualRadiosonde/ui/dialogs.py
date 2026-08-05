"""
Dialogs Module for Virtual Radiosonde Plotter.
Defines AboutDialog, ExportDialog, and high-contrast notification message boxes.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QComboBox, QSpinBox, QFormLayout, QMessageBox, QWidget
)


def apply_dialog_style(dialog: QWidget):
    """Applies clean, high-contrast QSS styling to dialogs and message boxes."""
    qss = """
    QDialog, QMessageBox {
        background-color: #ffffff;
        color: #0f172a;
        font-family: 'Segoe UI', 'Roboto', sans-serif;
    }
    QLabel {
        color: #0f172a;
        font-weight: 500;
        font-size: 12px;
    }
    QComboBox, QSpinBox {
        border: 1px solid #94a3b8;
        border-radius: 4px;
        padding: 6px;
        background-color: #ffffff;
        color: #0f172a;
        font-weight: 600;
    }
    QComboBox:focus, QSpinBox:focus {
        border: 2px solid #2563eb;
    }
    QPushButton {
        border: 1px solid #cbd5e1;
        border-radius: 4px;
        padding: 6px 14px;
        background-color: #f1f5f9;
        color: #0f172a;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #e2e8f0;
        border-color: #64748b;
    }
    """
    dialog.setStyleSheet(qss)


def show_error_dialog(parent: QWidget, title: str, message: str) -> None:
    """Displays a high-contrast Qt error message box."""
    msg_box = QMessageBox(parent)
    apply_dialog_style(msg_box)
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.exec()


def show_info_dialog(parent: QWidget, title: str, message: str) -> None:
    """Displays a high-contrast Qt information message box."""
    msg_box = QMessageBox(parent)
    apply_dialog_style(msg_box)
    msg_box.setIcon(QMessageBox.Information)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.exec()


class AboutDialog(QDialog):
    """
    About Dialog displaying Jerukagung Meteorologi organization information.
    """
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setWindowTitle("About - Jerukagung Meteorologi")
        self.setFixedSize(440, 310)
        apply_dialog_style(self)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        lbl_app_name = QLabel("🌦️ Virtual Radiosonde Plotter")
        lbl_app_name.setStyleSheet("font-size: 17px; font-weight: bold; color: #1e3a8a;")
        lbl_app_name.setAlignment(Qt.AlignCenter)

        lbl_org = QLabel("Jerukagung Meteorologi")
        lbl_org.setAlignment(Qt.AlignCenter)
        lbl_org.setStyleSheet("color: #047857; font-size: 13px; font-weight: bold;")

        lbl_version = QLabel("Version 1.0.0 (PySide6 / MetPy)")
        lbl_version.setAlignment(Qt.AlignCenter)
        lbl_version.setStyleSheet("color: #475569; font-size: 11px; font-weight: 500;")

        lbl_desc = QLabel(
            "Aplikasi analisis termodinamika atmosfer dan visualisasi diagram Skew-T Log-P "
            "standar riset meteorologi.\n\n"
            "• Organisasi: Jerukagung Meteorologi\n"
            "• Core Engine: MetPy & Pint\n"
            "• Visualisasi: Matplotlib Skew-T Log-P\n"
            "• Sumber Data: ERA5 / Weather Model\n"
            "• GUI Framework: PySide6 (Qt6)"
        )
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("margin-top: 8px; color: #0f172a; font-size: 11px; line-height: 1.4;")

        btn_close = QPushButton("Tutup")
        btn_close.setMinimumWidth(100)
        btn_close.setMinimumHeight(34)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #1d4ed8;
                color: #ffffff;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1e40af;
            }
        """)
        btn_close.clicked.connect(self.accept)

        layout.addWidget(lbl_app_name)
        layout.addWidget(lbl_org)
        layout.addWidget(lbl_version)
        layout.addWidget(lbl_desc)
        layout.addStretch()
        layout.addWidget(btn_close, alignment=Qt.AlignCenter)


class ExportDialog(QDialog):
    """
    Dialog for configuring image export settings (PNG, PDF, SVG, DPI).
    """
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setWindowTitle("Export Skew-T Figure")
        self.setFixedSize(380, 220)

        self.export_format = "PNG"
        self.export_dpi = 300

        apply_dialog_style(self)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        lbl_title = QLabel("💾 Export Settings")
        lbl_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #1e3a8a;")
        layout.addWidget(lbl_title)

        form = QFormLayout()
        form.setSpacing(10)

        self.combo_format = QComboBox()
        self.combo_format.addItems(["PNG Image (*.png)", "PDF Document (*.pdf)", "SVG Vector (*.svg)"])

        self.spin_dpi = QSpinBox()
        self.spin_dpi.setRange(72, 600)
        self.spin_dpi.setValue(300)
        self.spin_dpi.setSingleStep(50)

        lbl_fmt = QLabel("Format Gambar:")
        lbl_fmt.setStyleSheet("color: #0f172a; font-weight: bold;")
        lbl_dpi = QLabel("Resolusi (DPI):")
        lbl_dpi.setStyleSheet("color: #0f172a; font-weight: bold;")

        form.addRow(lbl_fmt, self.combo_format)
        form.addRow(lbl_dpi, self.spin_dpi)

        layout.addLayout(form)

        btn_box = QHBoxLayout()
        btn_cancel = QPushButton("Batal")
        btn_cancel.setStyleSheet("background-color: #f1f5f9; color: #0f172a; font-weight: bold; border: 1px solid #94a3b8;")

        btn_save = QPushButton("Simpan...")
        btn_save.setDefault(True)
        btn_save.setStyleSheet("background-color: #1d4ed8; color: #ffffff; font-weight: bold;")

        btn_cancel.clicked.connect(self.reject)
        btn_save.clicked.connect(self.accept)

        btn_box.addWidget(btn_cancel)
        btn_box.addWidget(btn_save)

        layout.addStretch()
        layout.addLayout(btn_box)

    def get_settings(self) -> tuple[str, int]:
        """Returns selected file format extension and DPI."""
        fmt_text = self.combo_format.currentText()
        if "pdf" in fmt_text:
            ext = "pdf"
        elif "svg" in fmt_text:
            ext = "svg"
        else:
            ext = "png"
        return ext, self.spin_dpi.value()
