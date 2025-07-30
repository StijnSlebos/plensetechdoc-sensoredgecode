# Metadata Interface

This document describes the Streamlit-based metadata editing tool used to configure sensor parameters and measurement plans for the Plensor system.

---

## 📋 Purpose

The metadata interface allows users to:

- Define measurement sessions
- Configure signal types and sensor IDs
- Set environmental context
- Generate standardized JSON configuration files

---

## 🖥 Application Structure

- Implemented in `metadata_app.py` using Streamlit
- Launch via terminal:  
  ```bash
  streamlit run metadata_app.py
  ```
UI Sections:
- Session Metadata
- Sensor Settings
- Measurement Plan
- File Export

---

## 🧾 Editable Fields

### Session Metadata

| Field           | Type       | Example           |
|----------------|------------|-------------------|
| `project_name`  | String     | `"Test_Session"`  |
| `session_id`    | String     | `"Test_01"`       |
| `date`          | Date       | `"2025-07-30"`    |
| `location`      | String     | `"Greenhouse A"`  |

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
/home/plense/metadata/measure_settings.json
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
- [app.py](../code/measure-plensor/artifact/app.py)
- [metadata_app.py](../code/metadata/metadata_app.py)
