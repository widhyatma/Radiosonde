"""
Sounding Calculations Module
Executes MetPy thermodynamic and dynamic calculations on sounding profiles.
"""

from typing import Tuple, Dict, Any
import numpy as np
import metpy.calc as mpcalc
from metpy.units import units

from .sounding import SoundingData, SoundingIndices
from .interpolation import SoundingInterpolator


class SoundingCalculator:
    """
    Computes thermodynamic profiles and stability parameters from raw sounding observations.
    """
    @staticmethod
    def process_sounding(sounding: SoundingData) -> SoundingData:
        """
        Processes the input SoundingData object by running MetPy calculations and setting
        the computed profiles and SoundingIndices on the sounding object.
        """
        p_arr, T_arr, rh_arr, ws_arr, wd_arr = SoundingInterpolator.clean_and_attach_units(
            sounding.pressures,
            sounding.temperatures,
            sounding.relative_humidity,
            sounding.wind_speeds,
            sounding.wind_directions
        )

        # 1. Wind Components (U & V in knots)
        u_arr, v_arr = mpcalc.wind_components(ws_arr.to(units.knots), wd_arr)
        sounding.u_wind = u_arr.magnitude
        sounding.v_wind = v_arr.magnitude

        # 2. Dewpoint (Td) & Wetbulb (Tw)
        Td_arr = mpcalc.dewpoint_from_relative_humidity(T_arr, rh_arr)
        sounding.dewpoints = Td_arr.magnitude

        try:
            Tw_arr = mpcalc.wet_bulb_temperature(p_arr, T_arr, Td_arr)
            sounding.wetbulb = Tw_arr.magnitude
        except Exception:
            sounding.wetbulb = np.full_like(p_arr.magnitude, np.nan)

        # 3. Parcel Profile
        try:
            ml_p, ml_t, ml_td = mpcalc.mixed_parcel(p_arr, T_arr, Td_arr, depth=100 * units.hPa)
            parcel_prof = mpcalc.parcel_profile(p_arr, ml_t, ml_td)
        except Exception:
            parcel_prof = mpcalc.parcel_profile(p_arr, T_arr[0], Td_arr[0])

        sounding.parcel_profile = parcel_prof.magnitude

        # 4. Thermodynamic Indices
        indices = SoundingIndices()

        # Surface conditions
        indices.surface_temp_c = float(T_arr[0].magnitude)
        indices.surface_dewpoint_c = float(Td_arr[0].magnitude)

        # LCL
        try:
            lcl_p, lcl_t = mpcalc.lcl(p_arr[0], T_arr[0], Td_arr[0])
            indices.lcl_pressure_hpa = float(lcl_p.to(units.hPa).magnitude)
            indices.lcl_temp_c = float(lcl_t.to(units.degC).magnitude)
        except Exception:
            indices.lcl_pressure_hpa = np.nan
            indices.lcl_temp_c = np.nan

        # LFC & EL
        try:
            lfc_p, lfc_t = mpcalc.lfc(p_arr, T_arr, Td_arr)
            indices.lfc_pressure_hpa = float(lfc_p.to(units.hPa).magnitude) if not np.isnan(lfc_p) else np.nan
            indices.lfc_temp_c = float(lfc_t.to(units.degC).magnitude) if not np.isnan(lfc_t) else np.nan
        except Exception:
            indices.lfc_pressure_hpa = np.nan
            indices.lfc_temp_c = np.nan

        try:
            el_p, el_t = mpcalc.el(p_arr, T_arr, Td_arr)
            indices.el_pressure_hpa = float(el_p.to(units.hPa).magnitude) if not np.isnan(el_p) else np.nan
            indices.el_temp_c = float(el_t.to(units.degC).magnitude) if not np.isnan(el_t) else np.nan
        except Exception:
            indices.el_pressure_hpa = np.nan
            indices.el_temp_c = np.nan

        # CAPE & CIN
        try:
            sb_cape, sb_cin = mpcalc.surface_based_cape_cin(p_arr, T_arr, Td_arr)
            indices.sb_cape = float(sb_cape.magnitude)
            indices.sb_cin = float(sb_cin.magnitude)
        except Exception:
            indices.sb_cape = 0.0
            indices.sb_cin = 0.0

        try:
            ml_cape, ml_cin = mpcalc.mixed_layer_cape_cin(p_arr, T_arr, Td_arr)
            indices.ml_cape = float(ml_cape.magnitude)
            indices.ml_cin = float(ml_cin.magnitude)
        except Exception:
            indices.ml_cape = 0.0
            indices.ml_cin = 0.0

        try:
            mu_cape, mu_cin = mpcalc.most_unstable_cape_cin(p_arr, T_arr, Td_arr)
            indices.mu_cape = float(mu_cape.magnitude)
            indices.mu_cin = float(mu_cin.magnitude)
        except Exception:
            indices.mu_cape = 0.0
            indices.mu_cin = 0.0

        # Precipitable Water (PWAT)
        try:
            pwat = mpcalc.precipitable_water(p_arr, Td_arr)
            indices.pwat_mm = float(pwat.to(units.mm).magnitude)
            indices.pwat_in = float(pwat.to(units.inch).magnitude)
        except Exception:
            indices.pwat_mm = np.nan
            indices.pwat_in = np.nan

        # K Index
        try:
            ki = mpcalc.k_index(p_arr, T_arr, Td_arr)
            indices.k_index = float(ki.magnitude)
        except Exception:
            indices.k_index = np.nan

        # Total Totals Index
        try:
            tt = mpcalc.total_totals_index(p_arr, T_arr, Td_arr)
            indices.total_totals = float(tt.magnitude)
        except Exception:
            indices.total_totals = np.nan

        # Lifted Index
        try:
            li = mpcalc.lifted_index(p_arr, T_arr, parcel_prof)
            indices.lifted_index = float(li.magnitude[0]) if hasattr(li.magnitude, '__len__') else float(li.magnitude)
        except Exception:
            indices.lifted_index = np.nan

        # Showalter Index
        try:
            si = mpcalc.showalter_index(p_arr, T_arr, Td_arr)
            indices.showalter_index = float(si.magnitude[0]) if hasattr(si.magnitude, '__len__') else float(si.magnitude)
        except Exception:
            indices.showalter_index = np.nan

        # SWEAT Index
        try:
            sweat = mpcalc.sweat_index(p_arr, T_arr, Td_arr, ws_arr.to(units.knots), wd_arr)
            indices.sweat_index = float(sweat.magnitude)
        except Exception:
            indices.sweat_index = np.nan

        # Storm Relative Helicity (SRH) Placeholder / Calculation
        try:
            heights = mpcalc.pressure_to_height_std(p_arr)
            srh_1km, _, _ = mpcalc.storm_relative_helicity(heights, u_arr, v_arr, depth=1000 * units.m)
            indices.srh_0_1km = float(srh_1km.magnitude)
        except Exception:
            indices.srh_0_1km = np.nan

        try:
            heights = mpcalc.pressure_to_height_std(p_arr)
            srh_3km, _, _ = mpcalc.storm_relative_helicity(heights, u_arr, v_arr, depth=3000 * units.m)
            indices.srh_0_3km = float(srh_3km.magnitude)
        except Exception:
            indices.srh_0_3km = np.nan

        sounding.indices = indices
        return sounding
