"""
Integration test script for VirtualRadiosonde core package.
Verifies downloader, MetPy calculations, plotting, and CSV exports.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.downloader import SoundingDownloader
from core.sounding import SoundingData
from core.calculations import SoundingCalculator
from core.plotting import SkewTPlotter


def test_sounding_workflow():
    print("[1/4] Testing SoundingDownloader...")
    downloader = SoundingDownloader()
    lat, lon = -7.7367, 109.6461  # Kebumen
    date_str = "2026-08-04"
    utc_hour = 12

    pressures, temp_list, rh_list, ws_list, wd_list, valid_time_str = downloader.fetch_sounding(
        latitude=lat,
        longitude=lon,
        date_str=date_str,
        target_utc_hour=utc_hour,
        location_name="Kebumen"
    )

    print(f"      Downloaded {len(pressures)} pressure levels for {valid_time_str}.")
    assert len(pressures) > 0, "No pressure levels downloaded!"

    print("[2/4] Testing SoundingCalculator (MetPy)...")
    sounding = SoundingData(
        pressures=pressures,
        temperatures=temp_list,
        dewpoints=temp_list,
        relative_humidity=rh_list,
        wind_speeds=ws_list,
        wind_directions=wd_list,
        latitude=lat,
        longitude=lon,
        date_str=date_str,
        time_utc_hour=utc_hour,
        location_name="Kebumen"
    )

    sounding = SoundingCalculator.process_sounding(sounding)
    idx = sounding.indices

    print(f"      Calculated SBCAPE: {idx.sb_cape:.1f} J/kg, PWAT: {idx.pwat_mm:.1f} mm, K-Index: {idx.k_index:.1f}")
    assert idx.surface_temp_c is not None, "Surface temp is None!"

    print("[3/4] Testing SkewTPlotter...")
    fig = SkewTPlotter.create_skewt_figure(sounding)
    assert fig is not None, "SkewT Figure creation failed!"

    print("[4/4] Testing CSV export...")
    test_csv_path = os.path.join(BASE_DIR, "test_output.csv")
    sounding.to_csv(test_csv_path)
    assert os.path.exists(test_csv_path), "CSV file was not created!"
    os.remove(test_csv_path)
    print("      CSV export verified.")

    print("\n[SUCCESS] ALL CORE INTEGRATION TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    test_sounding_workflow()
