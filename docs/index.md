# Plensor Documentation Index

Welcome to the official documentation for the Plensor sensor platform. This repository captures all architectural, hardware, software, and operational information necessary for development, deployment, and analysis.

---

## 📁 Documentation Structure

| Section                     | Description                                        |
|-----------------------------|----------------------------------------------------|
| [architecture.md](architecture.md)             | System overview, hardware-software interaction      |
| [sensor_hardware.md](sensor_hardware.md)       | Details on the sensor and Pi Hat stack              |
| [gpio_and_relay_setup.md](gpio_and_relay_setup.md) | GPIO usage, reset cycles, RS485 TX toggling         |
| [communication_protocol.md](communication_protocol.md) | Byte-level command and message structure            |
| [sensor_commands.md](sensor_commands.md)       | Full list of supported sensor commands              |
| [measurement_app.md](measurement_app.md)       | Core logic for executing measurement cycles         |
| [power_management.md](power_management.md)     | Voltage drop behavior, limits, and circuit design   |
| [data_pipeline.md](data_pipeline.md)           | Signal processing from `.flac` to `.json`/`.npy`    |
| [storage_and_logging.md](storage_and_logging.md)| File structure and logging mechanisms               |
| [metadata_interface.md](metadata_interface.md) | Streamlit-based tool for setting up metadata        |
| [storage_and_logging.md](storage_and_logging.md) | File structure and logging mechanisms               |
| [configuration_guide.md](configuration_guide.md)| JSON configuration files and runtime control        |
| [data_structure.md](data_structure.md)         | File format details and schema definitions          |
| [glossary.md](glossary.md)                     | Full glossary of system terms and acronyms          |

---

## 📂 Repo Layout

```
/docs/
├── *.md # All documentation pages
├── assets/ # Linked figures and diagrams

/code/
├── measure-plensor/ # Measurement app and mixins
├── process-data/ # Audio processing pipeline
├── log-manager/ # Logging utility
├── metadata/ # Metadata editor GUI
├── rpi-health/ # System health monitoring

README.md # Top-level system overview
```


---

## 🖼️ Visual Assets

See [images-table.md](images-table.md) for a full overview of all required diagrams and where to source them from.

---

## 🔗 External Resources

- Plensor GitHub Repo (internal)
- NPEC documentation (optional)
