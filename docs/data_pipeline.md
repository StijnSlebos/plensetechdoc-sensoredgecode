# Data Pipeline

This document describes the signal processing and data transformation steps in the Plensor system, from raw `.flac` recordings to final `.json` and `.npy` feature sets.

---

## 📥 Input Format

- **File Type**: `.flac` audio
- **Channels**: Mono
- **Sample Rate**: 500 kHz
- **Bit Depth**: 16-bit

Captured via USB sound card or Pi onboard audio depending on hardware configuration.

---

## 🔃 Processing Flow

Implemented in `process-data/` using NumPy and SciPy.

```
FLAC → WAV → Array → FFT + Envelope + Peak → Feature JSON + Spectral .npy
```

---

## 🧪 Core Steps

### 1. Load Audio

- Decode `.flac` using `soundfile`
- Normalize amplitude
- Apply bandpass filter (10 kHz – 70 kHz) (if processing is enabled)

### 2. Envelope Extraction

- Apply Hilbert transform
- Smooth using exponential decay
- Clip to max window for time-domain inspection

### 3. FFT Spectrum

- Perform FFT on windowed region
- Extract dominant frequency bins
- Identify harmonic ratios

### 4. Peak Finding

- Apply threshold logic
- Tag first and maximum peaks
- Store TOF offset if applicable

---

## 📤 Output Artifacts

For each sensor and timepoint, the pipeline outputs:

| File Type | Filename                          | Description                   |
|-----------|-----------------------------------|-------------------------------|
| `.flac`   | `{meas_id}#{sensor_id}_{timestamp}.flac` | Raw audio recording |
| `.json`   | `{sensor_id}_{timestamp}.json`   | Local metadata file           |
| `.json`   | `{sensor_id}_env_{timestamp}.json` | Environmental data (if available) |
| `.json`   | `{prefix}_{timestamp}.json`      | TOF data (if available)       |
| `.json`   | `health_{sensor_id}_{timestamp}.json` | Health metrics log |
| `.json`   | `environment_{sensor_id}_{timestamp}.json` | Environment log |

---

## 📁 Output Directory Structure

```
/home/plense/plensor_data/
├── audio_data/
│   ├── time_domain_not_processed/  # Raw audio files
│   └── time_domain_processed/      # Processed audio files
├── metadata/                       # Local metadata files
├── environmental/                  # Environmental sensor data
├── tof/                           # Time-of-flight measurements
├── health_logs/                   # System health metrics
├── environment_logs/              # Environment monitoring logs
└── logs/                          # Application logs
```

---

## 🧪 Debugging Tips

- Check for `NaN` in FFT when input audio is clipped
- Validate envelope length matches FFT input
- Logging handled in `error_logger.py`

---

## 🔗 Related Documents

- [measurement_app.md](measurement_app.md)
- [sensor_commands.md](sensor_commands.md)
- [storage_and_logging.md](storage_and_logging.md)
- [signal_processing_tools.py](../code/process-data/)
