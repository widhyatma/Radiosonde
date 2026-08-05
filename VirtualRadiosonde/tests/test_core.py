"""
Integration test script for VirtualRadiosonde core package.
Verifies downloader, geocoding search, MetPy calculations, threat assessments, plotting, and CSV exports.
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
    print("[1/6] Testing SoundingDownloader Geocoding API...")
    cities = SoundingDownloader.search_city("Kebumen")
    print(f"      Found {len(cities)} city results for 'Kebumen'.")
    assert len(cities) > 0, "Geocoding search returned 0 results!"
    assert cities[0]["name"] == "Kebumen", f"Unexpected city name: {cities[0]['name']}"

    print("[2/6] Testing SoundingDownloader Profile Fetching...")
    downloader = SoundingDownloader()
    lat, lon = cities[0]["latitude"], cities[0]["longitude"]
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

    print("[3/6] Testing SoundingCalculator & Severe Weather Threat Assessment...")
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
    threats = idx.get_threat_assessment()

    print(f"      Calculated SBCAPE: {idx.sb_cape:.1f} J/kg, PWAT: {idx.pwat_mm:.1f} mm, K-Index: {idx.k_index:.1f}")
    print(f"      Threat Assessment -> Thunderstorm: {threats['thunderstorm']['level']}, Heavy Rain: {threats['heavy_rain']['level']}")
    assert idx.surface_temp_c is not None, "Surface temp is None!"
    assert "thunderstorm" in threats, "Threat assessment missing thunderstorm risk!"

    print("[4/6] Testing SkewTPlotter...")
    fig = SkewTPlotter.create_skewt_figure(sounding)
    assert fig is not None, "SkewT Figure creation failed!"

    print("[5/6] Testing Summary Text Report Generator...")
    summary_txt = sounding.to_summary_text()
    assert "Jerukagung Meteorologi" in summary_txt, "Summary text missing organization!"
    assert "PENILAIAN RISIKO CUACA EKSTREM" in summary_txt, "Summary text missing risk assessment section!"

    print("[6/6] Testing Local CSV Export & Read-Back Parser...")
    test_csv_path = os.path.join(BASE_DIR, "test_output.csv")
    sounding.to_csv(test_csv_path)
    assert os.path.exists(test_csv_path), "CSV file was not created!"

    loaded_sounding = SoundingData.from_csv(test_csv_path)
    assert len(loaded_sounding.pressures) == len(pressures), "Loaded CSV pressure length mismatch!"
    assert loaded_sounding.location_name == "Kebumen", f"Loaded location mismatch: {loaded_sounding.location_name}"

    os.remove(test_csv_path)
    print("      CSV export and parser verified.")

    print("\n[SUCCESS] ALL CORE INTEGRATION TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    test_sounding_workflow()
