# Data Structure

This document defines the structure of all data types and file formats produced by the Plensor system, including sensor logs, FFT and envelope arrays, and metadata summaries.

---

## 📁 Output Directory Layout

Each measurement is saved to a timestamped folder under `/plensor_data/[SensorID]/`:

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

## 🎧 `{meas_id}#{sensor_id}_{timestamp}.flac`

- Mono audio
- Sample rate: 500000 Hz
- Bit depth: 16-bit PCM
- Captures raw ultrasonic echo return
- Naming convention: `{measurement_type}#{sensor_id}_{timestamp}.flac`

---

## 📊 `{sensor_id}_{timestamp}.json`

Contains local metadata and measurement parameters:

```json
{
  "sensor_id": "#00001",
  "record_timestamp": "2025-07-30T14:30:00",
  "file_metadata": {
    "meas_id": "SINE",
    "sensor_id": "#00001",
    "datetime": "2025-07-30T14:30:00"
  },
  "measurement_metadata": {
    "max_amp": 0.94,
    "successful_reps": 10,
    "sum_of_squares": 0.23
  },
  "created_at": "2025-07-30T14:30:00"
}
```

---

## 🌡️ `{sensor_id}_env_{timestamp}.json`

Environmental sensor data (if available):

```json
{
  "sensor_id": "#00001",
  "record_timestamp": "2025-07-30T14:30:00",
  "environmental_data": {
    "inside_temp": 25.1,
    "outside_temp": 24.8,
    "inside_humidity": 46.3,
    "outside_humidity": 45.9
  },
  "created_at": "2025-07-30T14:30:00"
}
```

---

## ⏱️ `{prefix}_{timestamp}.json`

TOF measurements (if available):

```json
{
  "metadata": {
    "sensor_id": "#00001",
    "sensor_type": "PLENSOR"
  },
  "record_timestamp": "2025-07-30T14:30:00",
  "tof_data": [612, 615, 618, 620],
  "prefix": "tof_ns",
  "created_at": "2025-07-30T14:30:00"
}
```

---

## 💚 `health_{sensor_id}_{timestamp}.json`

System health metrics:

```json
{
  "sensor_id": "#00001",
  "data_type": "time_domain",
  "input_signal": "SINE",
  "health_metric_name": "upload_size",
  "health_metric_value": 1024000,
  "record_timestamp": "2025-07-30T14:30:00",
  "created_at": "2025-07-30T14:30:00"
}
```

---

## 🧪 Validation Rules

- `max_amp` should be < 1.0
- `successful_reps` must be positive and match expected repetitions
- `sum_of_squares` should be reasonable for the signal type
- All JSON files must have valid `created_at` timestamps
- Sensor IDs must follow the format `#XXXXX`

---

## 🧵 Metadata Linkage

Each JSON file embeds:
- Sensor ID and timestamp
- Measurement type and parameters
- Environmental context (if available)
- System health metrics (if available)

These align with session metadata and can be batch-aggregated.

---

## 🔗 Related Documents

- [data_pipeline.md](data_pipeline.md)
- [storage_and_logging.md](storage_and_logging.md)
- [metadata files](../code/metadata/)
