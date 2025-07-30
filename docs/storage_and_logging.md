# Storage and Logging

This document outlines how the Plensor system stores measurement data and manages logs for debugging, status tracking, and error recovery.

---

## 📁 Folder Structure

All data and logs are saved under `/home/plense/`:

```
/home/plense/
├── plensor_data/
│ └── [SensorID]/[Timestamp]/
│ ├── signal.flac
│ ├── fft.npy
│ ├── envelope.npy
│ ├── signal_summary.json
│ ├── processing_log.json
├── error_logs/
│ └── error.log
├── logs/
│ ├── runtime.log
│ ├── health.log
│ └── watchdog.log
```


---

## 📦 Measurement Outputs

Saved inside `/plensor_data/[SensorID]/[timestamp]/`, each measurement includes:

- `signal.flac`: Raw audio
- `fft.npy`: Spectral features
- `envelope.npy`: Time-domain envelope
- `signal_summary.json`: Extracted metrics (TOF, peak amp, etc.)
- `processing_log.json`: Metadata and processing status

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
- [error_logger.py](../code/log-manager/error_logger.py)
