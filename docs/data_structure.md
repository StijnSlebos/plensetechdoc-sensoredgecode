# Data Structure

This document defines the structure of all data types and file formats produced by the Plensor system, including sensor logs, FFT and envelope arrays, and metadata summaries.

---

## 📁 Output Directory Layout

Each measurement is saved to a timestamped folder under `/plensor_data/[SensorID]/`:

```
/plensor_data/
└── Sensor_01/
└── 2025-07-30_14-30-00/
├── signal.flac
├── fft.npy
├── envelope.npy
├── signal_summary.json
├── processing_log.json
```

---

## 🎧 `signal.flac`

- Mono audio
- Sample rate: 192000 Hz
- Bit depth: 16-bit PCM
- Captures raw ultrasonic echo return

---

## 🔊 `fft.npy`

- Shape: `(N,)`
- Type: `float32`
- Represents magnitude of frequency bins (0–96 kHz)
- Used for spectral classification and envelope shaping

---

## 📈 `envelope.npy`

- Shape: `(N,)`
- Type: `float32`
- Amplitude over time after Hilbert transform and smoothing
- Used for TOF peak analysis

---

## 📊 `signal_summary.json`

Contains extracted features and summary statistics:



```
{
"sensor_id": 1,
"timestamp": "2025-07-30T14:30:00",
"peak_amplitude": 0.94,
"peak_position": 3221,
"dominant_freq": 25400,
"snr": 23.8,
"tof_us": 612,
"temperature_c": 25.1,
"humidity_percent": 46.3,
"command": "SINE"
}
```

---

## 🧾 `processing_log.json`

Logs internal pipeline behavior:



```
{
"processing_time_ms": 180,
"fft_bins": 1024,
"envelope_smoothing": "exp_decay",
"errors": [],
"input_file": "signal.flac",
"notes": "Success"
}
```

---

## 🧪 Validation Rules

- `peak_amplitude` should be < 1.0
- `tof_us` must be positive and realistic (< 2000 μs)
- FFT bins must be non-zero
- NaNs in `.npy` files indicate pipeline failure

---

## 🧵 Metadata Linkage

Each summary JSON embeds:
- Sensor ID
- Timestamp
- Command type
- Environmental context

These align with deployment metadata and can be batch-aggregated.

---

## 🔗 Related Documents

- [data_pipeline.md](data_pipeline.md)
- [storage_and_logging.md](storage_and_logging.md)
- [deployment_metadata.json](../deployments/)
