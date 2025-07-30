# Plensor Sensor Hardware

This document details the physical components and electrical layout of the Plensor sensor hardware stack, including the Pi Hat interface, relay logic, and power delivery system.

---

## 🔌 System Overview

The Plensor sensor assembly includes:

- **Plensor Sensor**: Active ultrasonic transducer
- **Raspberry Pi (CM4 or Pi 4)**: Hosts all measurement logic
- **Pi Hat**: Custom board for GPIO routing, RS485 comms, and MOSFET switching
- **Power Supply**: 12V DC external input, powering up to 12 sensors directly

---

## 🔧 Pi Hat Architecture

The Pi Hat routes communication and power signals via:

- **RS485 Transceiver**: Enables serial bus communication
- **MOSFET Switch**: GPIO-controlled power toggling for sensors
- **Relay Circuit**: GPIO-triggered isolation and reconnection
- **DC Jack**: External 12V input terminal
- **5-Pin Terminal Block**: Power and data out to sensors

### GPIO Pin Assignments

| GPIO Pin | Function             |
|----------|----------------------|
| GPIO 4   | Power MOSFET switch  |
| GPIO 18  | RS485 TX control     |
| GPIO 21  | Optional relay logic |

See [gpio_and_relay_setup.md](gpio_and_relay_setup.md) for usage logic.

---

## ⚙️ Power Distribution & Constraints

The sensors draw high-frequency pulses that lead to nonlinear voltage drops:

- **Max Sensors per Pi Hat**: ~12 directly via jack
- **Power Model**: Based on observed voltage drops for 17 sensors
- **Resistance Sources**:
  - Pi Hat internal routing
  - Terminal and wire resistance

Plots and models available in [power_management.md](power_management.md).

---

## 🔁 Relay and Reset Logic

Relays allow resetting sensors without rebooting the Pi:

- Power is cycled by toggling GPIO 4 (MOSFET)
- `switch_mosfet.py` and `Relay.py` implement timed cycles
- Can be invoked manually or via metadata-driven logic

---

## 📷 Hardware Assembly Notes

- Use grounded shielded cables for long runs
- Ensure proper screw-tightening on terminal blocks
- Secure Pi Hat firmly to GPIO pins
- Confirm DC power polarity (center positive)

---

## 🔗 Related Documents

- [gpio_and_relay_setup.md](gpio_and_relay_setup.md)
- [power_management.md](power_management.md)
- [communication_protocol.md](communication_protocol.md)
