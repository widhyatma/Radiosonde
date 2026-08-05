# Virtual Radiosonde Plotter 🌦️

A professional, modular desktop application for downloading atmospheric weather model data (Open-Meteo ERA5 / Forecast), performing MetPy thermodynamic calculations, generating publication-quality Skew-T Log-P diagrams, and exporting parameters and figures.

Built with **Python 3.12+**, **PySide6 (Qt6)**, **MetPy**, and **Matplotlib**.

---

## 🌟 Features

- **Asynchronous Data Downloading**: Fetches upper-air pressure level profiles from Open-Meteo API without blocking the GUI using `QThread` workers.
- **Thermodynamic Analysis**:
  - Surface Temperature & Dew Point
  - Lifted Condensation Level (LCL)
  - Level of Free Convection (LFC)
  - Equilibrium Level (EL)
  - Surface-Based, Mixed-Layer, and Most-Unstable CAPE & CIN (SBCAPE, MLCAPE, MUCAPE, SBCIN, MLCIN, MUCIN)
  - Precipitable Water (PWAT in mm and inches)
  - Stability Indices: K Index (KI), Total Totals (TT), Lifted Index (LI), Showalter Index (SI), SWEAT Index, Storm Relative Helicity (SRH).
- **Publication-Quality Skew-T Log-P Plots**:
  - Temperature ($T$), Dew Point ($T_d$), Wet Bulb ($T_w$), and Parcel path lines.
  - Positive/Negative convective energy shading (CAPE in pink/red, CIN in blue).
  - Dry adiabats, moist adiabats, and mixing ratio background grid lines.
  - Wind barbs displayed in knots.
  - Light and Dark Theme support.
- **Export Options**:
  - Export Skew-T diagrams to high-resolution PNG, PDF, or SVG (up to 600 DPI).
  - Export vertical sounding profile and summary parameters to CSV.

---

## 📁 Project Structure

```text
VirtualRadiosonde/
│
├── app.py                     # Main application entry point
│
├── core/                      # Core scientific computation & data package
│   ├── __init__.py
│   ├── sounding.py            # SoundingData and SoundingIndices data models
│   ├── calculations.py        # MetPy thermodynamic calculations
│   ├── interpolation.py       # Data cleaning & unit handling
│   ├── plotting.py            # Skew-T diagram plotting module
│   └── downloader.py          # Asynchronous Open-Meteo API downloader
│
├── ui/                        # PySide6 User Interface package
│   ├── __init__.py
│   ├── main_window.py         # Main application window & thread management
│   ├── widgets.py             # Control panel, Parameter panel, Matplotlib canvas
│   └── dialogs.py             # About dialog, Export dialog, alert boxes
│
├── assets/                    # Application icons & graphics
├── data/                      # Data storage directory
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation
```

---

## 🚀 Quick Start

### 1. Installation

Ensure Python 3.12+ is installed. Install required dependencies:

```bash
pip install -r VirtualRadiosonde/requirements.txt
```

### 2. Running the Desktop Application

#### Option A: Running from Source
Launch the application using Python:

```bash
python VirtualRadiosonde/app.py
```

#### Option B: Running Standalone Executable (.exe)
The compiled standalone executable is built and ready in the distribution folder:

```text
d:\Github\RadioSonde\dist\VirtualRadiosondePlotter\VirtualRadiosondePlotter.exe
```

To recompile into an `.exe` bundle at any time using PyInstaller:

```bash
pyinstaller --noconfirm VirtualRadiosondePlotter.spec
```

---

## 🛠️ Tech Stack & Science

- **GUI**: [PySide6 (Qt6)](https://doc.qt.io/qtforpython-6/)
- **Meteorological Calculations**: [MetPy](https://unidata.github.io/MetPy/)
- **Visualization**: [Matplotlib](https://matplotlib.org/) & MetPy `SkewT`
- **Data Source**: [Open-Meteo Weather API](https://open-meteo.com/)
