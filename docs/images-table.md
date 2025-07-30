# Documentation Images Table

This table summarizes all visual assets referenced across the Plensor documentation. It includes suggested filenames, descriptions, and their source or where to capture them from.

---

## 📐 System & Hardware

| Filename                  | Description                                          | Source                            |
|---------------------------|------------------------------------------------------|------------------------------------|
| `system_architecture.png` | Block diagram of hardware-software architecture      | From your architecture slide       |
| `sensor_stack_photo.jpg`  | Photo of Pi + Pi Hat + sensor + terminal wiring      | From actual hardware               |
| `pi_hat_schematic.png`    | Schematic of Pi Hat layout and GPIO lines            | From design document               |
| `gpio_pin_map.png`        | Pi GPIO map with pins 4, 18, 21 highlighted          | From setup guide or edit online    |
| `mosfet_reset_sequence.png`| Diagram of GPIO 4 cycling for power reset           | Based on `switch_mosfet.py` logic  |
| `relay_timing_diagram.png`| Timing diagram showing GPIO 21 toggling              | From relay script                  |

---

## 🔄 Communication Protocol

| Filename                   | Description                                          | Source                            |
|----------------------------|------------------------------------------------------|------------------------------------|
| `packet_structure.png`     | Annotated byte-level command packet                  | From protocol slides               |
| `rs485_timing.png`         | GPIO 18 toggle waveform during TX                   | Can illustrate manually            |
| `command_table.png`        | Visual summary of command types and byte values      | Copy from sensor_commands.md       |

---

## 📊 Signal Processing

| Filename                   | Description                                          | Source                            |
|----------------------------|------------------------------------------------------|------------------------------------|
| `raw_waveform.png`         | Unfiltered signal plot from `signal.flac`            | Screenshot from NumPy/Matplotlib   |
| `filtered_waveform.png`    | Bandpass-filtered waveform                           | After envelope smoothing           |
| `audio_spectrum.png`       | Audio spectrum plot                                  | From `.flac` files                  |
| `envelope_overlay.png`     | Envelope on top of signal waveform                   | For TOF peak visual                |

---

## ⚡ Power & Hardware

| Filename                   | Description                                          | Source                            |
|----------------------------|------------------------------------------------------|------------------------------------|
| `voltage_vs_sensors.png`   | Voltage drop model with increasing sensor count      | Based on NPEC test plots           |
| `power_distribution.png`   | Power routing layout from Pi Hat to sensors          | From schematic or drawing          |
| `session_structure.png` | Folder structure example with sensor IDs and timestamps| From current data structure       |
| `metadata_editor_ui.png`   | Screenshot of Streamlit metadata app                 | From `metadata_app.py`             |

---

## 📁 Data & Logs

| Filename                   | Description                                          | Source                            |
|----------------------------|------------------------------------------------------|------------------------------------|
| `file_output_example.png`  | Folder and file example per measurement              | From data_pipeline.md             |
| `metadata_example.png`      | Snippet of metadata JSON fields                     | From actual JSON or doc           |
| `health_log_example.png`    | Sample of health metrics JSON                       | Same as above                     |
| `logging_overview.png`     | Diagram of error/runtime/watchdog logs              | From `storage_and_logging.md`     |

---

## 🧠 Miscellaneous

| Filename                   | Description                                          | Source                            |
|----------------------------|------------------------------------------------------|------------------------------------|
| `glossary_terms_diagram.png`| Visual map of key terms and their relationships     | Optional network diagram           |
| `streamlit_form_layout.png`| Screenshot of Streamlit field layout                | `metadata_interface.md` section    |
| `queue_execution_flow.png` | Measurement app control flow chart                  | From `measurement_app.md`          |

---

## 📂 Asset Location

Place all images under:
```
/docs/assets/
```

