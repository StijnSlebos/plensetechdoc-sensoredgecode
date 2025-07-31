![Banner](assets/banner_plense_edge.png)

# plensetechdoc-sensoredgecode
Documentation and code for the distributed sensor system of 'plensors' from the company plense-technologies.. 

> _a note from the author:_
> I have built this repository based on an old repository with a lot of cloud infrastructure and simplyfied the code for local use (you can go back in repo-time to find some cloud elements).
> For the documentation, I have pulled data from a lot of sources and together with the help of our AI/LLM friends came up with this large clickthrough of documentation.
> I have added specific (human written) old documentation in the folder ```/docs/documentation_logs/``` if you are interested in those.
> If things are incomplete, unclear or incorrect, let us know on the discussions page.
> Have a nice read,
> plense!

# _Plensor Sensor Platform_

Plensor is a modular ultrasonic sensing platform for environmental monitoring, object detection, and remote deployments. It includes hardware (custom Pi Hat + sensors), embedded control logic (GPIO and RS485), a configurable measurement engine, and a robust signal processing pipeline.

---

## 🚀 Features

- Multi-sensor orchestration via RS485
- Custom Pi Hat with GPIO control for power cycling
- Configurable signal bursts (SINE, BLOCK, TOF)
- High-fidelity audio capture (192 kHz FLAC)
- Streamlit-based metadata interface
- Full logging and watchdog support
- Extensible signal processing pipeline with NumPy/SciPy

---

## 📁 Repository Structure

```
/
├── code/ # All code modules
│ ├── measure-plensor/artifact/ # Measurement system and sensor mixins
│ ├── process-data/artifact/ # Signal processing scripts
│ ├── metadata/ # Streamlit GUI for config
│ ├── log-manager/artifact/ # Logger, watchdog, error handling
│ ├── rpi-health/artifact/ # System health monitoring
│ ├── setup-plensor/ # Hardware setup utilities
│ ├── modem-manager/ # GSM modem management
│ └── Interface-guis/ # User interface applications
├── docs/ # Documentation site
│ ├── *.md # Pages like architecture.md, commands.md, etc.
│ └── assets/ # All supporting diagrams and screenshots
├── README.md # This file
```


---

## 📖 Documentation

Full documentation is in `/docs/`.

Start with: [docs/index.md](docs/index.md)

-> or go to code documentation: [code/README.md](code/README.md)

Includes:
- Architecture overview
- GPIO + relay wiring
- Command reference
- Measurement queue logic
- Data structure and processing flow
- Logging, errors, and deployments

---



## 🗃️ Original Documentation Files

Additional original reports, logs, and slides can be found in:

- [docs/documentation_logs/](docs/documentation_logs/)

---
## 🛠 Requirements

- Raspberry Pi 4 or Compute Module
- Plensor Pi Hat + connected sensor
- Python 3.9+
- Required packages (see `requirements.txt`)

---

## 🧪 Running the Measurement App

```bash
cd code/measure-plensor/artifact
python3 app.py
```

---

## 🔗 Links

- [Documentation Index](docs/index.md)
- [Images Table](docs/images-table.md)
- [Sensor Commands](docs/sensor_commands.md)

---

## 📜 License

See [LICENSE](LICENSE) for terms and conditions.
