# Configuration Guide

This document explains the various configuration files used in the Plensor system, detailing their formats, locations, and purposes for customizing system behavior and measurement logic.

---

## 🧾 Main Configuration Files

| File                      | Path                              | Purpose                        |
|---------------------------|-----------------------------------|--------------------------------|
| `measure_settings.json`   | `/home/plense/`                   | Measurement queue config       |
| `deployment_metadata.json`| `/plensor_data/[deployment]/`     | Deployment-wide parameters     |
| `app_settings.json`       | `/home/plense/`                   | Global runtime flags           |
| `message_interrupt.json`  | `/home/plense/`                   | Interrupt commands for queue   |
| `error_flag.json`         | `/home/plense/`                   | Used by watchdog               |

---

## 📦 `measure_settings.json`

Auto-generated via Streamlit (`metadata_app.py`):

```json
{
  "project_name": "Test_NPEC",
  "sensor_ids": [1, 2, 3],
  "use_tof": true,
  "reps_per_type": 3,
  "env_interval_s": 60,
  "signals": [
    {
      "type": "SINE",
      "start_freq": 20,
      "stop_freq": 30,
      "duration": 50,
      "voltage": 5,
      "damping": 0
    }
  ]
}
````
Used by ````app.py```` to construct the ````measure```` queue.

---

## 🧩 `deployment_metadata.json`

Manually written or exported from metadata GUI. Shared across all measurement runs for a project. Includes GPS, sensor IDs, location, and notes.

Located at:

```
/plensor_data/[deployment]/deployment_metadata.json
```


Example:

```
{
"project_name": "KWS_Pilot",
"deployment_id": "KWS_Pilot_01",
"location": "52.37, 4.89",
"date": "2025-07-30",
"sensor_ids": [1, 2, 3, 4],
"notes": "Test at NPEC greenhouse."
}
```


---

## ⚙️ `app_settings.json`

Runtime control for toggling:

```
{
"continuous_mode": true,
"force_calibration": false,
"use_metadata_json": true
}
```

Used by `app.py` at startup to control behavior.

---

## 🚨 Interrupt & Error Files

### `message_interrupt.json`

Injected mid-run to override queue or command settings:

```
{
"interrupt_type": "CALIBRATE_ALL",
"target_sensors": [1, 2]
}
```


Checked between queue cycles.

### `error_flag.json`

Created if a crash or watchdog timeout is detected. Triggers halt or restart of `app.py`.

---

## 🧪 Tips

- Always regenerate `measure_settings.json` if GUI is updated
- Keep `app_settings.json` in version control if possible
- Remove `error_flag.json` manually if stale

---

## 🔗 Related Documents

- [metadata_interface.md](metadata_interface.md)
- [measurement_app.md](measurement_app.md)
- [storage_and_logging.md](storage_and_logging.md)
- [app.py](../code/measure-plensor/app.py)
