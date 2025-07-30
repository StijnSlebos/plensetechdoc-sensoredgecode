# Measurement App

This document explains the structure and behavior of the core measurement system in the Plensor platform, implemented in the `measure-plensor` module. It handles queue generation, command dispatch, data collection, and scheduling.

---

## 🧠 Core Process: `MeasureProcessManager`

The main orchestrator is the `MeasureProcessManager` class (in `app.py`). It manages:

- Initialization of sensors and GPIO
- Building and managing command queues
- Interfacing with `QueueManager`, `MessageHandler`, and sensor mixins
- Scheduling with `APScheduler`

---

## 🗂 Queue Types

### `get_byte` Queue

- Sends `GetSensorID` to all ports
- Verifies connected sensors and confirms readiness

### `calibrate` Queue

- Sends `CalibrateSensor` command
- Ensures consistent configuration on cold boot

### `measure` Queue

- Main measurement loop
- Cycles through `SINE`, `BLOCK`, `TOF`, `ENV` commands
- Pulls settings from `measure_settings.json` and metadata

See `queue_manager.py` for logic and structure.

---

## 🔀 Message Handling

`MessageHandler` handles the serial port:

- Opens `/dev/ttyAMA0` at 921600 baud
- Controls GPIO 18 (TX enable)
- Encodes packets with `message_packing_functions.py`
- Waits for ACKs
- Reads and unpacks with `message_unpacking_functions.py`
- Logs responses

All logs and errors handled by `ErrorLogger`.

---

## ⚙️ Sensor Class & Mixins

The `Sensor` class dynamically combines mixins to enable modular command sets:

- `MeasurePlensorMixin`: SINE, BLOCK, TOF, ENV
- `CalibrateSensorMixin`
- `GetSensorIDMixin`
- `SetSensorIDMixin`
- `SetDampingMixin`
- `ResetPlensorMixin`

Each command:
- Packs frame
- Sends via handler
- Unpacks and verifies ACK

---

## 📆 Scheduling & Automation

The app uses `APScheduler` to run:
- Midnight resets
- Continuous measurement every X seconds
- On-demand queue via flag `new_measure_settings_flag.txt`

Interrupts are managed via:
- `message_interrupt.json`
- `error_flag.json`
- `app_settings.json`

---

## 📁 File Outputs

Each measurement creates:
- `.flac` audio file
- `.json` response log
- Stored under: `/home/plense/plensor_data/[SensorID]/[Timestamp]/`

---

## 🚨 Error Handling

- Logs go to `/home/plense/error_logs/error.log`
- `ErrorLogger` writes rotating logs with timestamp and traceback
- Watchdog monitors measurement hangs and crashes

---

## 🧪 Example Measurement Flow

1. Load settings from metadata and JSON
2. Initialize all GPIO pins
3. Run `get_byte` queue
4. Calibrate all detected sensors
5. Launch main `measure` queue
6. Store and log outputs

---

## 🔗 Related Documents

- [sensor_commands.md](sensor_commands.md)
- [sensor_hardware.md](sensor_hardware.md)
- [gpio_and_relay_setup.md](gpio_and_relay_setup.md)
- [queue_manager.py](../code/measure-plensor/queue_manager.py)
- [app.py](../code/measure-plensor/app.py)
- [sensor.py](../code/measure-plensor/sensor.py)
