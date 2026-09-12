# Virtual Radiosonde Plotter 🌦️

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.12345678.svg)](https://doi.org/10.5281/zenodo.12345678)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![GUI Framework](https://img.shields.io/badge/GUI-PySide6%20(Qt6)-green.svg)](https://doc.qt.io/qtforpython-6/)
[![Calculations](https://img.shields.io/badge/Science-MetPy-orange.svg)](https://unidata.github.io/MetPy/)

A professional, modular desktop application for downloading atmospheric weather model data (Open-Meteo ERA5 / Forecast), performing MetPy thermodynamic calculations, generating publication-quality Skew-T Log-P diagrams, calculating Cloud Base Height ($z_{LCL}$), assessing tropical severe weather threats, and exporting profiles into CSV and native RAOB software formats (`.rsf`, `.env`).

---

## 🇲🇨 Ringkasan (Bahasa Indonesia)

**Virtual Radiosonde Plotter** adalah perangkat lunak desktop profesional yang dirancang khusus untuk peneliti, praktisi meteorologi, dan prakirawan cuaca. Aplikasi ini memungkinkan pengunduhan data profil atmosfer vertikal (*upper-air*) secara otomatis dari API Open-Meteo (ERA5 Reanalysis / Weather Forecast), melakukan analisis termodinamika atmosfer presisi tinggi menggunakan kerangka sains **MetPy**, serta memvisualisasikan diagram **Skew-T Log-P** standar laboratorium publikasi meteorologi.

---

## 🌟 Key Features / Fitur Utama

- **Asynchronous Data Ingestion / Pengunduhan Data Asinkron**:
  - Pustaka geocoding interaktif untuk pencarian kota/lokasi di seluruh dunia.
  - Pengunduhan data 19 tingkat tekanan (*pressure levels*) dari permukaan hingga $10\text{ hPa}$ tanpa membekukan antarmuka GUI (`QThread` workers).
  - Opsi preset lokasi cuaca tropis (Kebumen, Jakarta, Surabaya, Medan, Makassar, Jayapura).
  - Impor data CSV lokal (*📂 Open Local CSV*).

- **Thermodynamic Analysis & Cloud Base Height / Perhitungan Termodinamika & Tinggi Basis Awan**:
  - Surface Pressure, Surface Temperature, and Surface Dew Point ($P_0, T_0, T_{d0}$).
  - Lifted Condensation Level (LCL Pressure, Temperature, & Cloud Base Height $z_{LCL}$ in meters/feet).
  - Level of Free Convection (LFC Pressure & Temperature).
  - Equilibrium Level (EL Pressure & Temperature).
  - Surface-Based, Mixed-Layer, and Most-Unstable CAPE & CIN (SBCAPE, MLCAPE, MUCAPE, SBCIN, MLCIN, MUCIN in $\text{J/kg}$).
  - Precipitable Water (PWAT in $\text{mm}$ and inches).
  - Atmospheric Stability Indices: K Index (KI), Total Totals (TT), Lifted Index (LI), Showalter Index (SI), SWEAT Index, Storm Relative Helicity (SRH $0\text{--}1\text{km}$, $0\text{--}3\text{km}$).

- **Tropical Severe Weather Assessment / Penilaian Risiko Cuaca Ekstrem Tropis**:
  - Penilaian risiko otomatis berbasis ambang batas cuaca tropis (Petir/Badai Konvektif, Hujan Lebat Mendadak/PWAT, dan Wind Shear).
  - Fitur salin ringkasan laporan (*📋 Copy Summary Text*) untuk kemudahan laporan operasional.

- **Publication-Quality Skew-T Log-P Visualization**:
  - Kurva Temperatur ($T$), Dew Point ($T_d$), Wet Bulb ($T_w$), dan Jalur Parsel Terangkat (*Parcel Path*).
  - Arsiran energi konvektif positif/negatif (CAPE merah/pink, CIN biru).
  - Grid background garis adiabatik kering (*dry adiabats*), adiabatik basah (*moist adiabats*), dan rasio pencampuran (*mixing ratio*).
  - Barbs kecepatan dan arah angin dalam satuan knots.
  - Mode tampilan Gelap & Terang (*Dark/Light Mode toggle*).

- **Export Options & Compatibility / Ekspor Data & Kompatibilitas**:
  - Visual diagram Skew-T resolusi tinggi ke format PNG, PDF, atau SVG (hingga 600 DPI).
  - Ekspor CSV standar aplikasi.
  - **Ekspor Format Asli RAOB**:
    - **RAOB Sounding Format (`.rsf`)**: Format native software RAOB.
    - **RAOB Native Sounding Format (`.env`)**: Format mentah universal software RAOB.
    - **RAOB / NOAA ASCII Sounding Text (`.txt`)**: Format teks kolom tetap standar WMO / NOAA FSL.

---

## 🧮 Mathematical & Meteorological Formulations

### 1. Cloud Base Height ($z_{LCL}$) / Ketinggian Basis Awan
Ketinggian basis awan konvektif terangkat dihitung menggunakan gabungan persamaan termodinamika Espy dan formulasi geopotensial barometrik hipso metrik dari tekanan LCL ($P_{LCL}$) dan tekanan permukaan ($P_0$):

$$z_{LCL} = 44330.0 \times \left(1.0 - \left(\frac{P_{LCL}}{P_0}\right)^{0.1903}\right) \quad \text{[meter AGL/MSL]}$$

$$z_{LCL, ft} = z_{LCL} \times 3.28084 \quad \text{[feet AGL/MSL]}$$

### 2. Tropical PWAT Classification / Ambang Batas PWAT Tropis

| Kategori PWAT | Rentang Nilai | Karakteristik & Implikasi Cuaca |
| :--- | :--- | :--- |
| **Kering (Low)** | $< 20\text{ mm}$ | Udara sangat kering, tutupan awan minim. |
| **Moderat (Moderate)** | $20 - 40\text{ mm}$ | Kelembapan rata-rata, mendukung pembentukan awan Cumulus. |
| **Tinggi / Lembap (High)** | $40 - 55\text{ mm}$ | Kondisi harian normal wilayah tropis maritim, potensi hujan musiman. |
| **Sangat Tinggi (Extreme)** | $\ge 55\text{ mm}$ | Suplai uap air masif; berpotensi hujan lebat mendadak & konveksi kuat. |

---

## 📁 Project Structure

```text
VirtualRadiosonde/
│
├── app.py                     # Main application entry point
├── requirements.txt           # Dependency specification
├── VirtualRadiosondePlotter.spec # PyInstaller compilation specification
├── compile.bat                # Windows batch compiler
├── run.bat                    # Application execution batch script
│
├── core/                      # Core scientific computation & data package
│   ├── __init__.py
│   ├── sounding.py            # SoundingData, SoundingIndices & RAOB exporters (.rsf, .env, .csv)
│   ├── calculations.py        # MetPy thermodynamic calculations & Cloud Base Height
│   ├── interpolation.py       # Profile data cleaning & Pint unit handling
│   ├── plotting.py            # Skew-T Log-P visualization module
│   └── downloader.py          # Asynchronous Open-Meteo Geocoding & Profile downloader
│
├── ui/                        # PySide6 User Interface package
│   ├── __init__.py
│   ├── main_window.py         # Main application window & event handlers
│   ├── widgets.py             # Control panel, Parameter display table, Matplotlib canvas
│   ├── dialogs.py             # About dialog, Export settings dialog
│   └── icon_utils.py          # Pillow WebP application icon loader
│
├── assets/                    # Application logos and graphics
├── CITATION.cff               # Citation File Format (CFF v1.2.0)
└── .zenodo.json               # Zenodo metadata integration configuration
```

---

## 🚀 Quick Start & Installation

### 1. Installation from Source

Memerlukan Python **3.11+** atau **3.12+**. Install dependensi utama:

```bash
pip install -r requirements.txt
```

### 2. Running the Desktop Application

Jalankan aplikasi langsung melalui script launcher atau Python:

```bash
# Menggunakan batch launcher (Windows)
run.bat

# Atau menggunakan Python langsung:
python VirtualRadiosonde/app.py
```

### 3. Compiling Standalone Windows Executable (.exe)

Untuk membuat bundel executable mandiri yang dapat dijalankan tanpa Python:

```bash
# Menggunakan batch compiler
compile.bat

# Atau menggunakan PyInstaller langsung:
pyinstaller --noconfirm VirtualRadiosondePlotter.spec
```

Output executable terletak di: `dist\VirtualRadiosondePlotter\VirtualRadiosondePlotter.exe`.

---

## 📊 RAOB Software Integration

Aplikasi ini mendukung ekspor data tingkat tinggi yang dapat dibuka secara native di software **RAOB (Rawinsonde Observation Program)**:

- **RAOB Sounding Format (`.rsf`)**: Format bawaan RAOB Sounding Framework.
- **RAOB Native Format (`.env`)**: Format rawinsonde universal RAOB.
- **RAOB ASCII Text (`.txt`)**: Format teks standar NOAA FSL / WMO.

Ekspor dapat dilakukan via tombol **Export CSV Data** (`Ctrl+E`) di dalam aplikasi.

---

## 📜 Citation / Cara Mengutip (Zenodo DOI)

Jika Anda menggunakan software **Virtual Radiosonde Plotter** dalam riset, publikasi ilmiah, atau operasional meteorologi, silakan kutip menggunakan format berikut:

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.12345678.svg)](https://doi.org/10.5281/zenodo.12345678)

### APA / IEEE Format
> Widhyatma. (2026). *Virtual Radiosonde Plotter: Atmospheric Sounding Analysis & Skew-T Visualization Tool* (Version v1.0.0). Jerukagung Meteorologi. Zenodo. https://doi.org/10.5281/zenodo.12345678

### BibTeX Format
```bibtex
@software{widhyatma_2026_virtual_radiosonde,
  author       = {Widhyatma},
  title        = {Virtual Radiosonde Plotter: Atmospheric Sounding Analysis \& Skew-T Visualization Tool},
  month        = sep,
  year         = 2026,
  publisher    = {Zenodo},
  version      = {v1.0.0},
  doi          = {10.5281/zenodo.12345678},
  url          = {https://github.com/widhyatma/Radiosonde}
}
```

---

## ⚖️ License & Attribution

Hak Cipta (c) 2026 **Widhyatma (Jerukagung Meteorologi)**.  
Lisensi perangkat lunak ini berada di bawah [MIT License](LICENSE).
