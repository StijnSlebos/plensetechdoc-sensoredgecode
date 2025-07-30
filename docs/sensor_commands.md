# Sensor Commands Reference

This document provides a complete reference to the command bytes used in Plensor's RS485 communication protocol, including command functions, payload structure, and expected responses.

---

## 🧾 Command Index

| Byte  | Command             | Description                        | Affects Audio? |
|-------|---------------------|------------------------------------|----------------|
| 0x5E  | Block Wave Burst     | Emits a short block signal         | ✅              |
| 0x5F  | Sine Sweep Burst     | Emits frequency sweep              | ✅              |
| 0x60  | Calibrate Sensor     | Stores default signal config       | ❌              |
| 0x61  | Get Sensor ID        | Returns sensor’s unique ID         | ❌              |
| 0x62  | TOF Measurement      | Measures time of flight            | ✅              |
| 0x63  | Set Sensor ID        | Assigns new ID to sensor           | ❌              |
| 0x64  | Get Environment      | Returns temperature + humidity     | ❌              |
| 0x65  | Reset Sensor         | Power-cycles sensor via GPIO       | ❌              |
| 0x66  | Set Damping Byte     | Updates pulse shape coefficient    | ✅ (slightly)   |

---

## 📦 Payload Definitions

### Sine Sweep (0x5F) and Block Wave (0x5E)

```
[SIGNAL] [FREQ_START] [FREQ_STOP] [DURATION] [AMPLITUDE] [REPS] [DAMPING]
```


- **FREQ_START/STOP**: in kHz
- **AMPLITUDE**: in volts
- **DAMPING**: Optional byte (0–255)

### TOF (0x62)

```
[TOF_CMD] [AMPLITUDE]
```


Performs burst, waits for reflection, and returns time delta.

### Set Sensor ID (0x63)

```
[CURRENT_ID] [NEW_ID]
```

Saves to EEPROM and persists across reboots.

---

## 📥 Response Formats

### ACK or NAK

| Byte | Description      |
|------|------------------|
| 0x06 | ACK: success     |
| 0x15 | NAK: failed cmd  |

### Sensor ID (0x61)

```
[0x06] [Sensor ID]
```

### TOF Result (0x62)

```
[0x06] [High Byte] [Low Byte]
```

Time value in microseconds, split into 2 bytes.

---

## 🧪 Test and Validation Tools

- `get_sensor_id_mixin.py`
- `calibrate_sensor_mixin.py`
- `set_sensor_id_mixin.py`
- `set_damping_mixin.py`
- `reset_plensor_mixin.py`

All command calls are defined in `message_packing_functions.py`.

---

## 📊 Damping Byte Notes

- Affects waveform tapering
- Default = 0x00 (no damping)
- Higher = smoother edges
- Applied during signal burst prep, not TOF

---

## 🔗 Related Files

- [communication_protocol.md](communication_protocol.md)
- [message_packing_functions.py](../code/measure-plensor/message_packing_functions.py)
- [message_unpacking_functions.py](../code/measure-plensor/message_unpacking_functions.py)
- [sensor.py](../code/measure-plensor/sensor.py)







