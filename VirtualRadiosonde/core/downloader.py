"""
Sounding Downloader Module
Fetches atmospheric sounding data from weather model APIs (Open-Meteo ERA5 / Forecast).
"""

from typing import List, Tuple, Dict, Any, Optional
import datetime
import requests
import numpy as np
import pandas as pd


class SoundingDownloader:
    """
    Downloads vertical sounding data for specified coordinates and date/time.
    """
    DEFAULT_PRESSURES: List[int] = [
        1000, 975, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 250, 200, 150, 100
    ]

    FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(self, pressures: Optional[List[int]] = None):
        self.pressures = pressures or self.DEFAULT_PRESSURES

    def _build_hourly_vars(self) -> List[str]:
        """Construct variable request names for Open-Meteo API."""
        vars_list = []
        for p in self.pressures:
            vars_list.extend([
                f"temperature_{p}hPa",
                f"relative_humidity_{p}hPa",
                f"wind_speed_{p}hPa",
                f"wind_direction_{p}hPa"
            ])
        return vars_list

    def fetch_sounding(
        self,
        latitude: float,
        longitude: float,
        date_str: str,
        target_utc_hour: int = 12,
        location_name: str = "Target Location",
        source: str = "ERA5 (Open-Meteo)"
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, str]:
        """
        Fetches vertical pressure profile data for specified lat, lon, date, and hour.

        Returns:
            (pressures, temp_list, rh_list, ws_list, wd_list, valid_time_str)
        """
        # Validate coordinates
        if not (-90 <= latitude <= 90):
            raise ValueError(f"Invalid latitude: {latitude}. Must be between -90 and 90.")
        if not (-180 <= longitude <= 180):
            raise ValueError(f"Invalid longitude: {longitude}. Must be between -180 and 180.")

        hourly_vars = self._build_hourly_vars()
        target_dt = pd.to_datetime(f"{date_str} {target_utc_hour:02d}:00")

        # Open-Meteo parameter rules:
        # Pass start_date and end_date WITHOUT past_days / forecast_days (they are mutually exclusive)
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": ",".join(hourly_vars),
            "timezone": "UTC",
            "start_date": date_str,
            "end_date": date_str,
        }

        try:
            response = requests.get(self.FORECAST_URL, params=params, timeout=15)
            
            # Handle HTTP errors gracefully
            if response.status_code != 200:
                try:
                    res_json = response.json()
                    error_reason = res_json.get("reason", response.text)
                except Exception:
                    error_reason = response.text
                
                if response.status_code == 400:
                    raise ValueError(
                        f"Open-Meteo API Error (HTTP 400 Bad Request):\n{error_reason}\n\n"
                        f"Catatan: Open-Meteo Forecast API mendukung tanggal dari 3 bulan yang lalu hingga 16 hari ke depan."
                    )
                elif response.status_code == 503:
                    raise RuntimeError(
                        "Open-Meteo API Error (HTTP 503 Service Unavailable):\n"
                        "Server Open-Meteo sedang sibuk. Silakan coba beberapa detik lagi."
                    )
                else:
                    raise RuntimeError(f"Open-Meteo API Error (HTTP {response.status_code}): {error_reason}")

            res_json = response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Koneksi Internet / API Terganggu:\n{e}") from e

        if "hourly" not in res_json:
            error_msg = res_json.get("reason", "Unknown API error")
            raise RuntimeError(f"Open-Meteo API Error: {error_msg}")

        hourly = res_json["hourly"]
        times = pd.to_datetime(hourly["time"])
        
        target_hour_idx = int(np.abs(times - target_dt).argmin())
        valid_time_str = f"{hourly['time'][target_hour_idx].replace('T', ' ')} UTC"

        temp_arr = np.array([hourly.get(f"temperature_{p}hPa", [np.nan])[target_hour_idx] for p in self.pressures], dtype=float)
        rh_arr = np.array([hourly.get(f"relative_humidity_{p}hPa", [np.nan])[target_hour_idx] for p in self.pressures], dtype=float)
        ws_arr = np.array([hourly.get(f"wind_speed_{p}hPa", [np.nan])[target_hour_idx] for p in self.pressures], dtype=float)
        wd_arr = np.array([hourly.get(f"wind_direction_{p}hPa", [np.nan])[target_hour_idx] for p in self.pressures], dtype=float)

        return (
            np.array(self.pressures, dtype=float),
            temp_arr,
            rh_arr,
            ws_arr,
            wd_arr,
            valid_time_str
        )
