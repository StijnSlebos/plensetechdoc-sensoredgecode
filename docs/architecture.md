# Plensor System Architecture

The Plensor system integrates hardware, firmware, and software into a scalable sensor platform for acoustic plant monitoring. This document provides a detailed architectural overview of the entire system.

---

## 📌 Overview

The Plensor system comprises three main layers:

1. **Hardware Layer**
2. **Software Layer (Edge Code)**
3. **Metadata & Interface Layer**

These layers interact to execute acoustic measurements, process sensor data, and manage local sessions.

---

## 🧱 1. Hardware Layer

- **Plensor Sensors**: Custom-built transducers with acoustic emission and receiving capability.
- **Raspberry Pi (Edge Computer)**: Runs the measurement logic and manages connected sensors.
- **Pi Hat Interface**: Manages power switching (MOSFETs), RS485 communication, and relays.

See [sensor_hardware.md](sensor_hardware.md) and [gpio_and_relay_setup.md](gpio_and_relay_setup.md) for details.

---

## 🧠 2. Software Layer (Edge Code)

Structured into distinct components:

### Core Applications

- **`measure-plensor/`**: Handles measurement scheduling, command transmission, and response parsing.
  - Queue-based measurement pipeline
  - Byte-level communication protocol
  - Command mixins for modular expansion

- **`process-data/`**: Post-processing of raw audio to extract signal features.
  - FFT, envelope, time-domain analysis
  - Output structured `.npy` and `.json` files

- **`log-manager/` & `rpi-health/`**:
  - Error collection
  - Health metrics logging

See [measurement_app.md](measurement_app.md), [sensor_commands.md](sensor_commands.md), and [data_pipeline.md](data_pipeline.md).

### Code Organization

Located under the `/code/` folder:
```
/code/
├── measure-plensor/artifact/
├── process-data/artifact/
├── Interface-guis/
├── metadata/
├── rpi-health/artifact/
├── log-manager/artifact/
├── setup-plensor/
└── modem-manager/
```

---

## 🗂️ 3. Metadata & Interface Layer

- **Metadata Editor**: Streamlit-based GUI for managing session metadata and sensor parameters
- **Interface GUIs**: Tkinter-based GUI for manual or continuous measurement control

Includes:
- `metadata_app.py` for metadata editing
- `measurement_plan_window.py`, `single_measurement_window.py`, etc. for GUI

See [metadata_interface.md](metadata_interface.md) and [interface_guide.md](interface_guide.md).

---

## 🔄 Data & Message Flow

1. **Measurement Queue** initializes a set of sensor commands
2. **Serial Transmission** over RS485 sends command bytes
3. **Sensor Responds** with payload data
4. **Audio Signal** saved in `.flac`
5. **Post-Processing** creates `.npy` arrays and JSON logs
6. **Logs & Metadata** saved to structured storage

---

## 🧩 Key Relationships

| Component            | Depends On            |
|---------------------|------------------------|
| `measure-plensor`   | GPIO, serial, metadata |
| `process-data`      | Raw audio, metadata     |
| `interface-guis`    | `measure-plensor`, settings |
| `metadata`          | Streamlit, local config |

---

## 🔗 Related Documents

- [sensor_hardware.md](sensor_hardware.md)
- [gpio_and_relay_setup.md](gpio_and_relay_setup.md)
- [measurement_app.md](measurement_app.md)
- [sensor_commands.md](sensor_commands.md)
- [data_pipeline.md](data_pipeline.md)
- [metadata_interface.md](metadata_interface.md)
- [interface_guide.md](interface_guide.md)

