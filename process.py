"""
Survey Data Processor
=====================
Loads field survey data (XYZ coordinate points with measured values),
detects anomalies, computes summary statistics, and writes processed output.

Usage:
    python process.py

Input files:
    data/survey_config.json  - processing configuration (lists survey sites)

Output:
    output/<site>_anomalies.csv  - anomalous points per site
"""

import csv
import json
from pathlib import Path

import numpy as np


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def load_csv_points(filepath: str) -> list[dict]:
    """
    Load XYZ survey points from a CSV file.

    Expected columns: x, y, z, magnetic_intensity
    Returns a list of dicts with float-typed fields.
    """
    points = []
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            points.append({"x": float(row["x"]), "y": float(row["y"]), "z": float(row["z"]),
                           "magnetic_intensity": float(row["magnetic_intensity"]), })
    if not points:
        raise ValueError(f"No data found in {filepath}")
    return points


def load_config(filepath: str) -> dict:
    """Load survey processing configuration from a JSON file."""
    with open(filepath) as f:
        return json.load(f)


def load_json_points(filepath: str) -> list[dict]:
    """Load XYZ survey points from a JSON file."""
    with open(filepath) as f:
        points = json.load(f)
    if not points:
        raise ValueError(f"No data found in {filepath}")
    return [{"x": float(p["x"]), "y": float(p["y"]), "z": float(p["z"]),
             "magnetic_intensity": float(p["magnetic_intensity"]), } for p in points]


# ---------------------------------------------------------------------------
# Processing
# ---------------------------------------------------------------------------


def detect_anomalies(points: list[dict], threshold: float) -> list[dict]:
    """
    Return points whose value exceeds the anomaly threshold.

    In field surveys, anomalously high readings can indicate subsurface
    features of interest. The threshold is configured per survey.
    """
    return [p for p in points if p["magnetic_intensity"] > threshold]


def compute_stats(points: list[dict]) -> dict:
    """Compute summary statistics over the 'magnetic_intensity' field of a point set."""
    values = np.array([p["magnetic_intensity"] for p in points])
    return {"count": len(values), "mean": float(np.mean(values)),
            "std": float(np.std(values, ddof=1)) if len(values) > 1 else 0.0, "min": float(np.min(values)),
            "max": float(np.max(values)), "p25": float(np.percentile(values, 25)),
            "p50": float(np.percentile(values, 50)), "p75": float(np.percentile(values, 75)), }


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def write_output(points: list[dict], filepath: str) -> None:
    """Write survey points to a CSV file."""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["x", "y", "z", "magnetic_intensity"])
        writer.writeheader()
        writer.writerows(points)


def print_report(config: dict, points: list[dict], anomalies: list[dict]) -> None:
    """Print a processing summary report to stdout."""
    stats = compute_stats(points)

    meta = config.get("metadata", {})
    print("=" * 60)
    print(f"Survey Report: {meta.get('survey_id', 'unknown')}")
    print(f"Sensor:        {meta.get('sensor_model', 'unknown')}")
    print("=" * 60)

    print(f"\nMeasurement statistics ({stats['count']} points):")
    print(f"  mean  {stats['mean']:>10.3f}")
    print(f"  std   {stats['std']:>10.3f}")
    print(f"  min   {stats['min']:>10.3f}")
    print(f"  max   {stats['max']:>10.3f}")

    print(f"\nAnomaly detection:")
    print(f"  {len(anomalies)} anomalous points detected")
    if anomalies:
        print(f"  Top anomalies:")
        for pt in sorted(anomalies, key=lambda p: p["magnetic_intensity"], reverse=True)[:5]:
            print(
                f"    ({pt['x']:.1f}, {pt['y']:.1f}, {pt['z']:.1f})  magnetic_intensity={pt['magnetic_intensity']:.3f}")

    print("=" * 60)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def detection_pipeline(site_path: str, anomaly_threshold: float, config: dict) -> None:
    if site_path.endswith(".csv"):
        points = load_csv_points(site_path)
    elif site_path.endswith(".json"):
        points = load_json_points(site_path)
    else:
        raise ValueError(f"Unsupported format: {site_path}")

    anomalies = detect_anomalies(points, anomaly_threshold)
    print_report(config, points, anomalies)

    output_name = Path(site_path).stem + "_anomalies.csv"
    write_output(anomalies, f"output/{output_name}")
    print(f"\nAnomalies written to 'output/{output_name}'")


if __name__ == "__main__":
    site_config = load_config("data/survey_config.json")
    detection_pipeline(site_config["sites"][0]["file"], site_config["sites"][0]["anomaly_threshold"], site_config)
    detection_pipeline(site_config["sites"][1]["file"], site_config["sites"][1]["anomaly_threshold"], site_config)
