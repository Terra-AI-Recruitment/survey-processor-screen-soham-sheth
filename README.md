# Survey Processor

A data processing pipeline for geophysical field survey data.

## Session format

This is a 45-minute paired session with four parts:

1. **Orientation** — read the code and the open issues, run the script, ask questions
2. **Prioritization** — pick one of the refactor issues and explain why you'd start there
3. **Refactor** — implement your chosen issue
4. **Simulation design** — design discussion around the third open issue

---

## Setup

Python 3.11+ required.

**Vanilla Python**
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python process.py
python -m pytest tests/
```

**uv**
```bash
uv sync --all-groups
uv run python process.py
uv run python -m pytest tests/
```

---

## What it does

Loads field survey data from two sites, detects anomalous magnetic intensity readings,
prints a summary report, and writes anomalous points to CSV.

1. Reads processing configuration from `data/survey_config.json`
2. Loads XYZ survey points from `data/survey_north.csv` and `data/survey_east.json`
3. Detects readings above the configured anomaly threshold for each site
4. Prints a summary report per site
5. Writes anomalous points to `output/<site>_anomalies.csv`

---

## Data files

**`data/survey_north.csv`** — 50 points, CSV format

```
x,y,z,magnetic_intensity
100.0,200.0,50.0,12.4
...
```

**`data/survey_east.json`** — 20 points, JSON format

```json
[{"x": 100.0, "y": 250.0, "z": 62.0, "magnetic_intensity": 10.1}, ...]
```

Fields (both sources):
- `x`, `y`, `z`: spatial coordinates (metres, local grid)
- `magnetic_intensity`: the measured magnetic field strength at that location

**`data/survey_config.json`** — processing parameters

```json
{
  "metadata": {
    "survey_id": "GS-2024-017",
    "sensor_model": "MagStar-3000"
  },
  "sites": [
    {"file": "data/survey_north.csv", "anomaly_threshold": 20.0},
    {"file": "data/survey_east.json", "anomaly_threshold": 18.0}
  ]
}
```

---

## Output

**`output/survey_north_anomalies.csv`** and **`output/survey_east_anomalies.csv`** — anomalous points only, columns: `x`, `y`, `z`, `magnetic_intensity`

---

## Sample output

```
============================================================
Survey Report: GS-2024-017
Sensor:        MagStar-3000
============================================================

Measurement statistics (50 points):
  mean      15.394
  std        5.146
  min       10.200
  max       31.200

Anomaly detection:
  8 anomalous points detected
  Top anomalies:
    (125.0, 210.0, 50.0)  magnetic_intensity=31.200
    (125.0, 220.0, 55.0)  magnetic_intensity=28.300
    (130.0, 210.0, 50.0)  magnetic_intensity=27.900
    (120.0, 210.0, 50.0)  magnetic_intensity=25.400
    (130.0, 220.0, 55.0)  magnetic_intensity=24.100
============================================================

Anomalies written to 'output/survey_north_anomalies.csv'
```

_(A second report follows for the east site.)_
