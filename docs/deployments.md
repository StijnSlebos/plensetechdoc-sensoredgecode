# Deployments

This document outlines how the Plensor system handles deployment configuration, metadata organization, and structure for long-term and multi-site sensing setups.

---

## 🌍 Deployment Scope

Each deployment defines:
- Project-specific settings (ID, name, date)
- List of active sensors
- Measurement frequencies and repetitions
- GPS + environmental metadata

---

## 📁 Directory Structure

Each deployment creates a root folder under `/plensor_data/`:

```
/plensor_data/
└── client_Pilot_01/
├── 2025-07-30_14-30-00/
│ └── [SensorID]/ (files)
├── 2025-07-30_15-00-00/
│ └── [SensorID]/ (files)
└── deployment_metadata.json
```

Each timestamped folder is a measurement round with sensor subfolders.

---

## 🧾 Deployment Metadata File

Located at:

```
/plensor_data/[deployment]/deployment_metadata.json
```


Includes:

```json
{
  "project_name": "client_Pilot",
  "deployment_id": "client_Pilot_01",
  "location": "52.37, 4.89",
  "date": "2025-07-30",
  "sensor_ids": [1, 2, 3, 4],
  "notes": "Test at university greenhouse."
}
```
Used by ```app.py``` and ````metadata_app.py````.

---

## 📆 Measurement Plans

Defined by `measure_settings.json` or directly in metadata.

Each session specifies:
- Number of repetitions
- Time between bursts
- Signal list per sensor
- Optional `use_tof` and `env_interval_s`

---

## 🧩 Integration Flow

1. Metadata created in `metadata_app.py`
2. Measurement started via `app.py`
3. Each round saved in timestamped folder
4. Summary copied to root of deployment folder

---

## 📦 Upload & Sync (optional)

Deployment folders can be:
- Uploaded via SCP or mounted drive
- Synced to cloud or central storage
- Parsed by analysis pipelines

---

## 🧪 Tips

- Name deployment folders clearly by date/project
- Sync metadata between Streamlit and app
- Back up `deployment_metadata.json` regularly

---

## 🔗 Related Documents

- [metadata_interface.md](metadata_interface.md)
- [measurement_app.md](measurement_app.md)
- [storage_and_logging.md](storage_and_logging.md)


