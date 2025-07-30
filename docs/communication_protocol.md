# Communication Protocol

This document describes the RS485-based serial communication protocol used by the Plensor system to exchange data between the Raspberry Pi and sensors.

---

## 🛠 Protocol Overview

- **Bus Type**: RS485 full duplex
- **Baud Rate**: 921600
- **Frame Format**: 8 data bits, no parity, 1 stop bit (8N1)
- **Flow Control**: None
- **Transceiver Control**: GPIO 18 pulled HIGH during TX, LOW otherwise

---

## 🔤 Frame Structure

Each message exchanged between the Pi and a sensor follows a defined byte structure:

```
[STX] [Sensor ID] [Length] [Payload] [Checksum]
```


### Byte Definitions

| Byte       | Value/Type | Description                            |
|------------|------------|----------------------------------------|
| STX        | `0x5A`     | Start of transmission byte             |
| Sensor ID  | `0x01`–`0xFF` | Unique 8-bit ID of each sensor        |
| Length     | `0x00`–`0xFF` | Payload byte length                  |
| Payload    | Varies     | Command data or sensor response        |
| Checksum   | XOR        | XOR of all previous bytes              |

---

## 🧾 Command Types

Commands are sent as encoded payloads and interpreted by the sensor firmware.

### Basic Commands

| Code  | Function         |
|-------|------------------|
| 0x5E  | Block wave burst |
| 0x5F  | Sine sweep burst |
| 0x60  | Calibrate sensor |
| 0x61  | Get Sensor ID    |
| 0x62  | TOF Measurement  |
| 0x64  | Get Environment  |

### Extended Payloads

Commands may include multiple fields:

```
[SIGNAL_TYPE] [FREQ_START] [FREQ_STOP] [DURATION] [VOLTAGE] [REPS] ...
```


Refer to [sensor_commands.md](sensor_commands.md) for full byte maps.

---

## 📨 Sensor Responses

Sensors respond with payloads structured as:

```
[ACK] [Sensor ID] [Measurement Data]
```

| Response Byte | Meaning                  |
|---------------|--------------------------|
| `0x06`        | ACK: Success             |
| `0x15`        | NAK: Error or retry      |

---

## 🔄 Communication Flow

1. Pi pulls GPIO 18 HIGH
2. Encodes frame using `message_packing_functions.py`
3. Sends over serial `/dev/ttyAMA0`
4. Waits for sensor ACK + response
5. Unpacks data using `message_unpacking_functions.py`
6. GPIO 18 pulled LOW

---

## 📦 Example Packet

Sending a sine sweep burst command:

```
[0x5A] [0x01] [0x07] [0x5F] [0x10] [0x28] [0x32] [0x05] [0x01] [CHK]
```


Where:
- 0x5F = Sine sweep
- 0x10 = Start frequency
- 0x28 = Stop frequency
- 0x32 = Duration
- 0x05 = Voltage
- 0x01 = Repetition count

---

## 🧪 Testing and Debugging

- Use `screen /dev/ttyAMA0 921600` to monitor sensor responses
- Logging handled via `ErrorLogger` if checksum fails
- Test scripts: `get_sensor_id_mixin.py`, `send_tof.py`

---

## 🔗 Related Documents

- [sensor_commands.md](sensor_commands.md)
- [gpio_and_relay_setup.md](gpio_and_relay_setup.md)
- [message_packing_functions.py](../code/measure-plensor/message_packing_functions.py)
- [message_unpacking_functions.py](../code/measure-plensor/message_unpacking_functions.py)


