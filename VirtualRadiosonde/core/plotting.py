"""
Skew-T Log-P Plotting Module
Generates publication-quality atmospheric Skew-T diagrams using MetPy and Matplotlib
matching the exact rason.ipynb (TropicalTidbits style) standard.
"""

from typing import Optional, Tuple
import matplotlib
matplotlib.use("QtAgg")  # Ensure QtAgg backend compatibility
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

import metpy.calc as mpcalc
from metpy.plots import SkewT
from metpy.units import units

from .sounding import SoundingData


class SkewTPlotter:
    """
    Creates Skew-T Log-P figures from SoundingData objects matching the notebook standard.
    """
    @staticmethod
    def create_skewt_figure(
        sounding: SoundingData,
        fig_size: Tuple[float, float] = (14.0, 9.0),
        dpi: int = 100,
        dark_mode: bool = False
    ) -> matplotlib.figure.Figure:
        """
        Builds a complete Skew-T Log-P Matplotlib Figure matching rason.ipynb standard.
        """
        # Set up color theme
        if dark_mode:
            bg_color = "#1e1e2e"
            text_color = "#cdd6f4"
            side_bg = "#313244"
            side_edge = "#45475a"
            box_text_color = "#cdd6f4"
        else:
            bg_color = "#ffffff"
            text_color = "#111111"
            side_bg = "#f8f9fa"
            side_edge = "#adb5bd"
            box_text_color = "#212529"

        fig = plt.figure(figsize=fig_size, dpi=dpi, facecolor=bg_color)
        gs = gridspec.GridSpec(1, 2, width_ratios=[3.2, 1.1], wspace=0.12)

        # --------------------------------------------------------
        # 1. MAIN SKEW-T LOG-P DIAGRAM
        # --------------------------------------------------------
        skew = SkewT(fig, rotation=45, subplot=gs[0])

        # Retrieve Pint unit-attached profile arrays
        p_arr = sounding.pressures * units.hPa
        T_arr = sounding.temperatures * units.degC
        Td_arr = sounding.dewpoints * units.degC

        # Plot Main Curves (Temperature=Red, Dewpoint=Green, Wetbulb=Blue, ML Parcel=Purple Dashed)
        skew.plot(p_arr, T_arr, 'red', linewidth=2.2, label='Temperature')
        skew.plot(p_arr, Td_arr, 'green', linewidth=2.2, label='Dewpoint')

        if sounding.wetbulb is not None and not np.all(np.isnan(sounding.wetbulb)):
            Tw_arr = sounding.wetbulb * units.degC
            skew.plot(p_arr, Tw_arr, 'blue', linewidth=1.2, alpha=0.85, label='Wetbulb')

        if sounding.parcel_profile is not None and not np.all(np.isnan(sounding.parcel_profile)):
            parcel_prof = sounding.parcel_profile * units.degC
            skew.plot(p_arr, parcel_prof, color='purple', linewidth=2.0, linestyle='--', label='Mixed-Layer Parcel Path (100mb)')

            # Shading CAPE & CIN
            try:
                skew.shade_cape(p_arr, T_arr, parcel_prof, alpha=0.18, color='crimson')
                skew.shade_cin(p_arr, T_arr, parcel_prof, alpha=0.18, color='dodgerblue')
            except Exception:
                pass

        # Plot Wind Barbs on every pressure level
        if sounding.u_wind is not None and sounding.v_wind is not None:
            u_arr = sounding.u_wind * units.knots
            v_arr = sounding.v_wind * units.knots
            skew.plot_barbs(p_arr, u_arr, v_arr, xloc=1.03, length=6, color=text_color)

        # Dry & Moist Adiabats, Mixing Ratio Lines
        skew.plot_dry_adiabats(alpha=0.2, color='brown', linewidth=0.7, label='Dry Adiabats')
        skew.plot_moist_adiabats(alpha=0.2, color='blue', linewidth=0.7, label='Pseudoadiabats')
        skew.plot_mixing_lines(alpha=0.2, color='green', linewidth=0.7, linestyle=':', label='Sat. Mix. Ratio')

        # Axis Limits & Formatting
        skew.ax.set_ylim(1000, 100)
        skew.ax.set_xlim(-40, 50)
        skew.ax.set_xlabel('Temperature (°C)', fontsize=11, fontweight='bold', color=text_color)
        skew.ax.set_ylabel('Pressure (hPa)', fontsize=11, fontweight='bold', color=text_color)
        skew.ax.tick_params(colors=text_color, labelsize=10)

        legend = skew.ax.legend(loc='upper left', fontsize=8.5, framealpha=0.9, facecolor=bg_color)
        plt.setp(legend.get_texts(), color=text_color)

        # Surface Temperature/Dewpoint Badge
        try:
            surf_t_f = T_arr[0].to('degF').magnitude
            badge_text = f"{T_arr[0].magnitude:.0f}°C / {surf_t_f:.0f}°F"
            skew.ax.text(
                T_arr[0].magnitude + 2, 980, badge_text,
                color='red', fontweight='bold', fontsize=9.5,
                bbox=dict(boxstyle='square,pad=0.2', facecolor=bg_color, edgecolor='red', alpha=0.8)
            )
        except Exception:
            pass

        # --------------------------------------------------------
        # 2. RIGHT SIDE PANEL: THERMODYNAMIC PARAMETER TABLE
        # --------------------------------------------------------
        ax_side = fig.add_subplot(gs[1])
        ax_side.axis('off')

        # Header Watermark
        ax_side.text(0.05, 0.98, 'JERUKAGUNG METEOROLOGI', fontsize=11, fontweight='bold', color=text_color, ha='left', va='top')

        idx = sounding.indices
        sb_cape_val = f"{idx.sb_cape:6.0f}" if idx.sb_cape is not None and not np.isnan(idx.sb_cape) else "     0"
        ml_cape_val = f"{idx.ml_cape:6.0f}" if idx.ml_cape is not None and not np.isnan(idx.ml_cape) else "     0"
        mu_cape_val = f"{idx.mu_cape:6.0f}" if idx.mu_cape is not None and not np.isnan(idx.mu_cape) else "     0"

        sb_cin_val = f"{idx.sb_cin:6.0f}" if idx.sb_cin is not None and not np.isnan(idx.sb_cin) else "     0"
        ml_cin_val = f"{idx.ml_cin:6.0f}" if idx.ml_cin is not None and not np.isnan(idx.ml_cin) else "     0"

        ki_val = f"{idx.k_index:6.1f}" if idx.k_index is not None and not np.isnan(idx.k_index) else "   N/A"
        tt_val = f"{idx.total_totals:6.1f}" if idx.total_totals is not None and not np.isnan(idx.total_totals) else "   N/A"

        lcl_p_val = f"{idx.lcl_pressure_hpa:6.0f}" if idx.lcl_pressure_hpa is not None and not np.isnan(idx.lcl_pressure_hpa) else "   N/A"
        lcl_t_val = f"{idx.lcl_temp_c:6.1f}" if idx.lcl_temp_c is not None and not np.isnan(idx.lcl_temp_c) else "   N/A"

        pwat_in_val = f"{idx.pwat_in:6.2f}" if idx.pwat_in is not None and not np.isnan(idx.pwat_in) else "   N/A"
        pwat_mm_val = f"{idx.pwat_mm:.1f}" if idx.pwat_mm is not None and not np.isnan(idx.pwat_mm) else "N/A"

        param_text = (
            f"SBCAPE:    {sb_cape_val} J/kg\n"
            f"MLCAPE:    {ml_cape_val} J/kg\n"
            f"MUCAPE:    {mu_cape_val} J/kg\n"
            "-------------------------\n"
            f"SBCIN:     {sb_cin_val} J/kg\n"
            f"MLCIN:     {ml_cin_val} J/kg\n"
            "-------------------------\n"
            f"K-INDEX:   {ki_val} °C\n"
            f"TOTALS:    {tt_val} °C\n"
            "-------------------------\n"
            f"LCL PRESS: {lcl_p_val} hPa\n"
            f"LCL TEMP:  {lcl_t_val} °C\n"
            "-------------------------\n"
            f"PWAT:      {pwat_in_val} in\n"
            f"           ({pwat_mm_val} mm)\n"
        )

        ax_side.text(
            0.05, 0.92, param_text, fontsize=9.5, family='monospace', fontweight='bold',
            color=box_text_color, va='top',
            bbox=dict(boxstyle='square,pad=0.7', facecolor=side_bg, edgecolor=side_edge, linewidth=1.2)
        )

        # Main Title Header
        lat_dir = "S" if sounding.latitude < 0 else "N"
        lon_dir = "W" if sounding.longitude < 0 else "E"
        title_header = (
            f"Sounding Atmosfer  {abs(sounding.latitude):.2f}°{lat_dir}, {abs(sounding.longitude):.2f}°{lon_dir} "
            f"({sounding.location_name})   Observation: {sounding.observation_time_str}"
        )
        fig.suptitle(title_header, fontsize=12, fontweight='bold', x=0.45, y=0.98, color=text_color)

        fig.subplots_adjust(left=0.07, right=0.95, top=0.93, bottom=0.08, wspace=0.15)
        return fig

    @staticmethod
    def save_figure(fig: matplotlib.figure.Figure, filepath: str, dpi: int = 300) -> None:
        """Saves Matplotlib Figure to file (PNG, PDF, SVG)."""
        fig.savefig(filepath, dpi=dpi, bbox_inches="tight")
