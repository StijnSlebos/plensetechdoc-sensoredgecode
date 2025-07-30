# Metadata Interface

This document describes the Streamlit-based metadata editing tool used to configure deployments, sensor parameters, and measurement plans for the Plensor system.

---

## 📋 Purpose

The metadata interface allows users to:

- Define measurement sessions
- Configure signal types and sensor IDs
- Set GPS coordinates and environmental context
- Generate standardized JSON configuration files

---

## 🖥 Application Structure

- Implemented in `metadata_app.py` using Streamlit
- Launch via terminal:  
  ```bash
  streamlit run metadata_app.py
  ```
UI Sections:
- Deployment Metadata
- Sensor Settings
- Measurement Plan
- File Export

---

## 🧾 Editable Fields

### Deployment Metadata

| Field           | Type       | Example           |
|----------------|------------|-------------------|
| `project_name`  | String     | `"KWS_Pilot"`     |
| `deployment_id` | String     | `"KWS_01"`        |
| `date`          | Date       | `"2025-07-30"`    |
| `location`      | GPS coords | `"52.2, 4.8"`     |

### Sensor Settings

| Field            | Description               |
|------------------|---------------------------|
| `sensor_ids`     | List of RS485 addresses   |
| `reps_per_type`  | Repetitions for each type |
| `use_tof`        | Boolean toggle            |
| `env_interval_s` | How often to request ENV  |

### Signal Types

Each signal entry includes:

```
[SIGNAL_TYPE, START_FREQ, STOP_FREQ, DURATION, VOLTAGE, DAMPING]
```


---

## 📁 Output Files

When saved, a JSON file is created:


```
/home/plense/measure_settings.json
```


It includes:
- All signal commands
- Measurement timing logic
- Sensor mapping
- Metadata block

Used by `app.py` to create the next queue run.

---

## 📷 UI Screenshot Descriptions

- Field input boxes for each setting
- Dynamic sensor entry forms
- Real-time validation and preview
- Save button to export JSON

---

## 🧪 Tips

- Always validate coordinates and IDs
- Use consistent casing for project names
- Only include signals used in the current session
- Regenerate JSON if editing live session

---

## 🔗 Related Documents

- [measurement_app.md](measurement_app.md)
- [sensor_commands.md](sensor_commands.md)
- [app.py](../code/measure-plensor/app.py)
- [measure_settings.json](../code/metadata/)
