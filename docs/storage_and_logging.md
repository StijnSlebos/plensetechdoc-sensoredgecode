# Storage and Logging

This document outlines how the Plensor system stores measurement data and manages logs for debugging, status tracking, and error recovery.

---

## 📁 Folder Structure

All data and logs are saved under `/home/plense/`:

```
/home/plense/
├── plensor_data/
│ ├── audio_data/
│ │   ├── time_domain_not_processed/  # Raw audio files
│ │   └── time_domain_processed/      # Processed audio files
│ ├── metadata/                       # Local metadata files
│ ├── environmental/                  # Environmental sensor data
│ ├── tof/                           # Time-of-flight measurements
│ ├── health_logs/                   # System health metrics
│ ├── environment_logs/              # Environment monitoring logs
│ └── logs/                          # Application logs
├── error_logs/
│ └── error.log
└── metadata/                        # Sensor metadata files
```


---

## 📦 Measurement Outputs

Saved inside `/home/plense/plensor_data/`, each measurement includes:

- `{meas_id}#{sensor_id}_{timestamp}.flac`: Raw audio recording
- `{sensor_id}_{timestamp}.json`: Local metadata with measurement parameters
- `{sensor_id}_env_{timestamp}.json`: Environmental sensor data (if available)
- `{prefix}_{timestamp}.json`: TOF measurements (if available)
- `health_{sensor_id}_{timestamp}.json`: System health metrics
- `environment_{sensor_id}_{timestamp}.json`: Environment monitoring data

---

## 🛠 Loggers and Files

### `error_logs/error.log`

- Captures Python tracebacks
- Handles all `try/except` blocks in `app.py` and mixins
- Rotated daily by timestamp

### `logs/runtime.log`

- General info log (boot, GPIO state, measurement cycles)

### `logs/health.log`

- Periodic health checks
- Monitors Pi CPU usage, uptime, sensor activity

### `logs/watchdog.log`

- Triggered if system hangs or if `watchdog.py` intervenes

---

## 🧪 Log Tools

- `ErrorLogger`: Class from `error_logger.py` with rotating log implementation
- `Watchdog`: Monitors running processes and restarts crashed threads

---

## 🔍 Monitoring Tips

- Use `tail -f /home/plense/logs/runtime.log` during test
- If sensors don’t respond, inspect `error.log` for RS485 errors
- For long uptime checks, analyze `health.log` CPU and memory entries

---

## 🔗 Related Documents

- [data_pipeline.md](data_pipeline.md)
- [measurement_app.md](measurement_app.md)
- [gpio_and_relay_setup.md](gpio_and_relay_setup.md)
- [ErrorLogger.py](../code/log-manager/artifact/ErrorLogger.py)
