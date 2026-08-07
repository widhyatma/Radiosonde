"""
Sounding Data Model
Defines classes for storing atmospheric profile data and calculated thermodynamic parameters.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any
import numpy as np
import pandas as pd


@dataclass
class SoundingIndices:
    """Class representing thermodynamic and stability indices calculated from a sounding."""
    surface_temp_c: Optional[float] = None
    surface_dewpoint_c: Optional[float] = None
    
    lcl_pressure_hpa: Optional[float] = None
    lcl_temp_c: Optional[float] = None
    lcl_height_m: Optional[float] = None
    lcl_height_ft: Optional[float] = None
    
    lfc_pressure_hpa: Optional[float] = None
    lfc_temp_c: Optional[float] = None
    
    el_pressure_hpa: Optional[float] = None
    el_temp_c: Optional[float] = None
    
    sb_cape: Optional[float] = None
    sb_cin: Optional[float] = None
    ml_cape: Optional[float] = None
    ml_cin: Optional[float] = None
    mu_cape: Optional[float] = None
    mu_cin: Optional[float] = None
    
    pwat_mm: Optional[float] = None
    pwat_in: Optional[float] = None
    
    k_index: Optional[float] = None
    total_totals: Optional[float] = None
    lifted_index: Optional[float] = None
    showalter_index: Optional[float] = None
    sweat_index: Optional[float] = None
    
    srh_0_1km: Optional[float] = None
    srh_0_3km: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert indices to a clean dictionary formatted for UI display."""
        return {k: (v if v is not None and not np.isnan(v) else np.nan) for k, v in asdict(self).items()}

    def get_threat_assessment(self) -> Dict[str, Dict[str, str]]:
        """
        Evaluates severe weather threat levels based on thermodynamic indices.
        Returns risk categories: Low, Moderate, High, Extreme.
        """
        cape = self.sb_cape if (self.sb_cape is not None and not np.isnan(self.sb_cape)) else 0.0
        ki = self.k_index if (self.k_index is not None and not np.isnan(self.k_index)) else 0.0

        if cape > 2500 or ki > 38:
            ts_risk = "Sangat Tinggi (Extreme)"
            ts_color = "#dc2626"
        elif cape > 1000 or ki > 30:
            ts_risk = "Tinggi (High)"
            ts_color = "#ea580c"
        elif cape > 300 or ki > 22:
            ts_risk = "Sedang (Moderate)"
            ts_color = "#d97706"
        else:
            ts_risk = "Rendah (Low)"
            ts_color = "#16a34a"

        pwat = self.pwat_mm if (self.pwat_mm is not None and not np.isnan(self.pwat_mm)) else 0.0
        if pwat >= 55.0:
            rain_risk = "Sangat Tinggi (Extreme)"
            rain_color = "#dc2626"
        elif pwat >= 40.0:
            rain_risk = "Tinggi (High)"
            rain_color = "#ea580c"
        elif pwat >= 20.0:
            rain_risk = "Sedang (Moderate)"
            rain_color = "#d97706"
        else:
            rain_risk = "Rendah (Low)"
            rain_color = "#16a34a"

        srh = self.srh_0_3km if (self.srh_0_3km is not None and not np.isnan(self.srh_0_3km)) else 0.0
        if srh > 250:
            wind_risk = "Sangat Tinggi (Extreme)"
            wind_color = "#dc2626"
        elif srh > 150:
            wind_risk = "Tinggi (High)"
            wind_color = "#ea580c"
        elif srh > 75:
            wind_risk = "Sedang (Moderate)"
            wind_color = "#d97706"
        else:
            wind_risk = "Rendah (Low)"
            wind_color = "#16a34a"

        return {
            "thunderstorm": {"level": ts_risk, "color": ts_color},
            "heavy_rain": {"level": rain_risk, "color": rain_color},
            "wind_shear": {"level": wind_risk, "color": wind_color},
        }


class SoundingData:
    """
    Class containing raw and processed atmospheric sounding profiles and metadata.
    """
    def __init__(
        self,
        pressures: np.ndarray,
        temperatures: np.ndarray,
        dewpoints: np.ndarray,
        relative_humidity: np.ndarray,
        wind_speeds: np.ndarray,
        wind_directions: np.ndarray,
        latitude: float,
        longitude: float,
        date_str: str,
        time_utc_hour: int,
        location_name: str = "Target Location",
        source: str = "ERA5 (Open-Meteo)",
    ):
        self.pressures = np.array(pressures, dtype=float)           # hPa
        self.temperatures = np.array(temperatures, dtype=float)       # degC
        self.dewpoints = np.array(dewpoints, dtype=float)           # degC
        self.relative_humidity = np.array(relative_humidity, dtype=float) # %
        self.wind_speeds = np.array(wind_speeds, dtype=float)       # km/h or knots
        self.wind_directions = np.array(wind_directions, dtype=float) # degrees
        
        # Computed level profiles
        self.u_wind: Optional[np.ndarray] = None  # knots
        self.v_wind: Optional[np.ndarray] = None  # knots
        self.wetbulb: Optional[np.ndarray] = None # degC
        self.parcel_profile: Optional[np.ndarray] = None # degC
        
        # Metadata
        self.latitude = latitude
        self.longitude = longitude
        self.date_str = date_str
        self.time_utc_hour = time_utc_hour
        self.location_name = location_name
        self.source = source
        self.observation_time_str = f"{date_str} {time_utc_hour:02d}:00 UTC"
        
        # Calculated indices
        self.indices: SoundingIndices = SoundingIndices()

    def to_dataframe(self) -> pd.DataFrame:
        """Returns sounding profile as a structured pandas DataFrame."""
        df_dict = {
            "Pressure_hPa": self.pressures,
            "Temperature_C": self.temperatures,
            "Dewpoint_C": self.dewpoints,
            "RelativeHumidity_%": self.relative_humidity,
            "WindSpeed_kmh": self.wind_speeds,
            "WindDir_deg": self.wind_directions,
        }
        if self.u_wind is not None:
            df_dict["U_wind_kt"] = self.u_wind
        if self.v_wind is not None:
            df_dict["V_wind_kt"] = self.v_wind
        if self.wetbulb is not None:
            df_dict["Wetbulb_C"] = self.wetbulb
        if self.parcel_profile is not None:
            df_dict["Parcel_C"] = self.parcel_profile

        return pd.DataFrame(df_dict)

    def to_csv(self, filepath: str) -> None:
        """Saves sounding profile data and metadata to a CSV file."""
        df = self.to_dataframe()
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# Virtual Radiosonde Plotter Data Export\n")
            f.write(f"# Source: {self.source}\n")
            f.write(f"# Location: {self.location_name} (Lat: {self.latitude}, Lon: {self.longitude})\n")
            f.write(f"# Valid Time: {self.observation_time_str}\n")
            f.write("# Calculated Summary Parameters:\n")
            indices_dict = self.indices.to_dict()
            for key, val in indices_dict.items():
                val_str = f"{val:.2f}" if isinstance(val, (int, float)) and not np.isnan(val) else "N/A"
                f.write(f"#   {key}: {val_str}\n")
            f.write("# Profile Data:\n")
        df.to_csv(filepath, mode="a", index=False)

    def to_raob_csv(self, filepath: str) -> None:
        """Exports sounding data in RAOB software compliant CSV format."""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# RAOB Software Compatible Sounding Data\n")
            f.write(f"# Station: {self.location_name}\n")
            f.write(f"# Latitude: {self.latitude:.4f}\n")
            f.write(f"# Longitude: {self.longitude:.4f}\n")
            f.write(f"# Date: {self.date_str}\n")
            f.write(f"# Time: {self.time_utc_hour:02d}:00 UTC\n")
            f.write(f"# Source: {self.source}\n")
            f.write("PRES,HGHT,TEMP,DWPT,DIR,SPD,RH\n")
            
            # Approximate height estimation from standard pressure levels if height not explicitly present
            heights = 44330.0 * (1.0 - (self.pressures / 1013.25) ** 0.1903)
            ws_kt = self.wind_speeds / 1.852 if self.wind_speeds is not None else np.zeros_like(self.pressures)
            
            for p, h, t, td, wd, ws, rh in zip(
                self.pressures, heights, self.temperatures, self.dewpoints,
                self.wind_directions, ws_kt, self.relative_humidity
            ):
                f.write(f"{p:.1f},{h:.0f},{t:.1f},{td:.1f},{wd:.0f},{ws:.1f},{rh:.1f}\n")

    def to_raob_txt(self, filepath: str) -> None:
        """Exports sounding data in RAOB / NOAA fixed-width ASCII text format."""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"TITLE = Jerukagung Meteorologi RAOB Sounding Data\n")
            f.write(f"STATION = {self.location_name}\n")
            f.write(f"LAT = {self.latitude:.4f}\n")
            f.write(f"LON = {self.longitude:.4f}\n")
            f.write(f"DATE = {self.date_str}\n")
            f.write(f"TIME = {self.time_utc_hour:02d}:00 UTC\n")
            f.write(f"SOURCE = {self.source}\n\n")
            f.write(f"  PRES    HGHT    TEMP    DWPT    WDIR    WSPD      RH\n")
            f.write(f"   hPa       m       C       C     deg      kt       %\n")
            heights = 44330.0 * (1.0 - (self.pressures / 1013.25) ** 0.1903)
            ws_kt = self.wind_speeds / 1.852 if self.wind_speeds is not None else np.zeros_like(self.pressures)

            for p, h, t, td, wd, ws, rh in zip(
                self.pressures, heights, self.temperatures, self.dewpoints,
                self.wind_directions, ws_kt, self.relative_humidity
            ):
                f.write(f"{p:6.1f}  {h:6.0f}  {t:6.1f}  {td:6.1f}  {wd:6.0f}  {ws:6.1f}  {rh:6.1f}\n")

    def to_raob_env(self, filepath: str) -> None:
        """
        Exports sounding data in native RAOB .ENV / .RAW file format.
        Structure recognized natively by RAOB software import wizard.
        """
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"RAOB\n")
            f.write(f"{self.location_name.upper()} ID {self.latitude:.2f} {self.longitude:.2f} 29m {self.date_str} {self.time_utc_hour:02d}:00UTC\n")
            f.write(f"PRES(hPa) HGHT(m) TEMP(C) DWPT(C) WDIR(deg) WSPD(kt) RH(%)\n")
            
            heights = 44330.0 * (1.0 - (self.pressures / 1013.25) ** 0.1903)
            ws_kt = self.wind_speeds / 1.852 if self.wind_speeds is not None else np.zeros_like(self.pressures)

            for p, h, t, td, wd, ws, rh in zip(
                self.pressures, heights, self.temperatures, self.dewpoints,
                self.wind_directions, ws_kt, self.relative_humidity
            ):
                f.write(f"{p:7.1f} {h:6.0f} {t:6.1f} {td:6.1f} {wd:5.0f} {ws:5.1f} {rh:5.1f}\n")

    def to_raob_rsf(self, filepath: str) -> None:
        """
        Exports sounding data in native RAOB Sounding Format (.RSF).
        Format specifically recognized by RAOB software (.rsf).
        """
        with open(filepath, "w", encoding="utf-8") as f:
            date_clean = self.date_str.replace("-", "")
            time_clean = f"{self.time_utc_hour:02d}00"
            f.write("RSF\n")
            f.write(f"99999,{self.latitude:.4f},{self.longitude:.4f},29,{date_clean},{time_clean},{self.location_name.upper()}\n")
            f.write("PRES,HGHT,TEMP,DWPT,WDIR,WSPD,RH\n")

            heights = 44330.0 * (1.0 - (self.pressures / 1013.25) ** 0.1903)
            ws_kt = self.wind_speeds / 1.852 if self.wind_speeds is not None else np.zeros_like(self.pressures)

            for p, h, t, td, wd, ws, rh in zip(
                self.pressures, heights, self.temperatures, self.dewpoints,
                self.wind_directions, ws_kt, self.relative_humidity
            ):
                f.write(f"{p:.1f},{h:.0f},{t:.1f},{td:.1f},{wd:.0f},{ws:.1f},{rh:.1f}\n")

    def to_summary_text(self) -> str:
        """Generates a clean text report for clipboard copying."""
        idx = self.indices
        threats = idx.get_threat_assessment()

        sb_cape_str = f"{idx.sb_cape:.0f}" if idx.sb_cape is not None and not np.isnan(idx.sb_cape) else "N/A"
        ml_cape_str = f"{idx.ml_cape:.0f}" if idx.ml_cape is not None and not np.isnan(idx.ml_cape) else "N/A"
        mu_cape_str = f"{idx.mu_cape:.0f}" if idx.mu_cape is not None and not np.isnan(idx.mu_cape) else "N/A"
        pwat_str = f"{idx.pwat_mm:.1f} mm ({idx.pwat_in:.2f} in)" if idx.pwat_mm is not None and not np.isnan(idx.pwat_mm) else "N/A"
        ki_str = f"{idx.k_index:.1f} °C" if idx.k_index is not None and not np.isnan(idx.k_index) else "N/A"
        tt_str = f"{idx.total_totals:.1f} °C" if idx.total_totals is not None and not np.isnan(idx.total_totals) else "N/A"
        lcl_str = f"{idx.lcl_pressure_hpa:.0f} hPa ({idx.lcl_temp_c:.1f} °C)" if idx.lcl_pressure_hpa is not None and not np.isnan(idx.lcl_pressure_hpa) else "N/A"
        cbh_str = f"{idx.lcl_height_m:.0f} m ({idx.lcl_height_ft:.0f} ft)" if idx.lcl_height_m is not None and not np.isnan(idx.lcl_height_m) else "N/A"

        text = (
            f"=== LAPORAN SOUNDING ATMOSFER ===\n"
            f"Organisasi: Jerukagung Meteorologi\n"
            f"Lokasi: {self.location_name} ({abs(self.latitude):.2f}°, {abs(self.longitude):.2f}°)\n"
            f"Waktu Observasi: {self.observation_time_str}\n"
            f"Sumber Data: {self.source}\n\n"
            f"[ INDEKS TERMODINAMIKA ]\n"
            f"• SBCAPE            : {sb_cape_str} J/kg\n"
            f"• MLCAPE            : {ml_cape_str} J/kg\n"
            f"• MUCAPE            : {mu_cape_str} J/kg\n"
            f"• PWAT              : {pwat_str}\n"
            f"• K-INDEX           : {ki_str}\n"
            f"• TOTALS            : {tt_str}\n"
            f"• LCL Pressure/Temp : {lcl_str}\n"
            f"• TINGGI BASIS AWAN : {cbh_str}\n\n"
            f"[ PENILAIAN RISIKO CUACA EKSTREM ]\n"
            f"• Potensi Petir/Badai : {threats['thunderstorm']['level']}\n"
            f"• Potensi Hujan Lebat : {threats['heavy_rain']['level']}\n"
            f"• Potensi Wind Shear  : {threats['wind_shear']['level']}\n"
        )
        return text

    @staticmethod
    def from_csv(filepath: str) -> "SoundingData":
        """Parses a local CSV file exported by the app or standard profile CSV."""
        df = pd.read_csv(filepath, comment="#")

        location_name = "Local CSV Data"
        source = "Local CSV File"
        date_str = "2026-01-01"
        time_utc_hour = 12
        latitude = -7.7367
        longitude = 109.6461

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.startswith("#"):
                        break
                    line_str = line.strip("# \n")
                    if "Location:" in line_str:
                        parts = line_str.split("Location:")[1].strip()
                        location_name = parts.split("(")[0].strip()
                    elif "Source:" in line_str:
                        source = line_str.split("Source:")[1].strip()
                    elif "Valid Time:" in line_str:
                        vt = line_str.split("Valid Time:")[1].strip()
                        date_str = vt.split()[0]
                        time_utc_hour = int(vt.split()[1].split(":")[0])
        except Exception:
            pass

        pressures = df["Pressure_hPa"].values if "Pressure_hPa" in df.columns else df.iloc[:, 0].values
        temperatures = df["Temperature_C"].values if "Temperature_C" in df.columns else df.iloc[:, 1].values
        dewpoints = df["Dewpoint_C"].values if "Dewpoint_C" in df.columns else temperatures
        rh = df["RelativeHumidity_%"].values if "RelativeHumidity_%" in df.columns else np.full_like(temperatures, 80.0)
        ws = df["WindSpeed_kmh"].values if "WindSpeed_kmh" in df.columns else np.zeros_like(temperatures)
        wd = df["WindDir_deg"].values if "WindDir_deg" in df.columns else np.zeros_like(temperatures)

        return SoundingData(
            pressures=pressures,
            temperatures=temperatures,
            dewpoints=dewpoints,
            relative_humidity=rh,
            wind_speeds=ws,
            wind_directions=wd,
            latitude=latitude,
            longitude=longitude,
            date_str=date_str,
            time_utc_hour=time_utc_hour,
            location_name=location_name,
            source=source
        )
