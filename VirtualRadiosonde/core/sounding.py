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
