"""
Sounding Interpolation and Data Cleaning Module
Handles NaN filtering, MetPy unit attachment, and vertical profile interpolation.
"""

from typing import Tuple
import numpy as np
import metpy.calc as mpcalc
from metpy.units import units


class SoundingInterpolator:
    """
    Cleans, validates, and formats profile arrays with MetPy units.
    """
    @staticmethod
    def clean_and_attach_units(
        pressures: np.ndarray,
        temperatures: np.ndarray,
        relative_humidity: np.ndarray,
        wind_speeds: np.ndarray,
        wind_directions: np.ndarray,
    ) -> Tuple[units.Quantity, units.Quantity, units.Quantity, units.Quantity, units.Quantity]:
        """
        Filters out invalid/NaN levels and attaches MetPy Pint units.

        Returns:
            (p_arr, T_arr, rh_arr, ws_arr, wd_arr) as Pint Quantities.
        """
        # Convert to float arrays
        p_raw = np.array(pressures, dtype=float) * units.hPa
        T_raw = np.array(temperatures, dtype=float) * units.degC
        rh_raw = np.array(relative_humidity, dtype=float) * units.percent
        ws_raw = np.array(wind_speeds, dtype=float) * units("km/h")
        wd_raw = np.array(wind_directions, dtype=float) * units.degrees

        # Mask invalid temperature or RH
        valid_mask = ~np.isnan(T_raw.magnitude) & ~np.isnan(rh_raw.magnitude) & ~np.isnan(p_raw.magnitude)

        if not np.any(valid_mask):
            raise ValueError("No valid data levels found in sounding profile.")

        p_arr = p_raw[valid_mask]
        T_arr = T_raw[valid_mask]
        rh_arr = rh_raw[valid_mask]
        ws_arr = ws_raw[valid_mask]
        wd_arr = wd_raw[valid_mask]

        # Ensure pressures are monotonically decreasing for atmospheric vertical ordering
        if not np.all(np.diff(p_arr.magnitude) < 0):
            # Sort by pressure descending (surface to top)
            sort_idx = np.argsort(p_arr.magnitude)[::-1]
            p_arr = p_arr[sort_idx]
            T_arr = T_arr[sort_idx]
            rh_arr = rh_arr[sort_idx]
            ws_arr = ws_arr[sort_idx]
            wd_arr = wd_arr[sort_idx]

        return p_arr, T_arr, rh_arr, ws_arr, wd_arr
