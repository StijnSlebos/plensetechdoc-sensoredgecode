# Data Pipeline

This document describes the signal processing and data transformation steps in the Plensor system, from raw `.flac` recordings to final `.json` and `.npy` feature sets.

---

## 📥 Input Format

- **File Type**: `.flac` audio
- **Channels**: Mono
- **Sample Rate**: 192 kHz
- **Bit Depth**: 16-bit

Captured via USB sound card or Pi onboard audio depending on deployment.

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
- Apply bandpass filter (10 kHz – 70 kHz)

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
| `.npy`    | `fft.npy`                         | Raw FFT bins                  |
| `.npy`    | `envelope.npy`                    | Time-domain envelope          |
| `.json`   | `signal_summary.json`             | All extracted metrics         |
| `.json`   | `processing_log.json`             | Runtime info + warnings       |

---

## 📁 Output Directory Structure

```
/plensor_data/
└── Sensor_01/
└── 2025-07-25_14-30-01/
├── signal.flac
├── fft.npy
├── envelope.npy
├── signal_summary.json
├── processing_log.json
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
