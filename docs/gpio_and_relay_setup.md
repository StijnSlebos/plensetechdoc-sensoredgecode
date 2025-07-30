# GPIO and Relay Setup

This guide explains how the Plensor system uses GPIO pins on the Raspberry Pi to manage power cycling, RS485 transmission, and sensor resets via relays and MOSFET switches.

---

## 🧩 GPIO Overview

### Key GPIO Pins

| GPIO Pin | Mode | Function                       |
|----------|------|--------------------------------|
| 4        | OUT  | MOSFET power switch to sensors |
| 18       | OUT  | RS485 transceiver TX enable    |
| 21       | OUT  | Relay control (optional)       |

These pins are controlled using `RPi.GPIO` and are coordinated via scripts and the `queue_manager.py` logic.

---

## 🔁 Power Reset Logic

Power cycling is critical to reinitializing sensors and ensuring stability:

- **GPIO 4 HIGH** → Sensor power ON
- **GPIO 4 LOW**  → Sensor power OFF

Scripts like `switch_mosfet.py`, `Relay.py`, and `Mosfet.py` use this logic with timers.

**Power Reset Sequence:**
1. GPIO 4 set to HIGH → Sensor receives power
2. Delay (2–10s) for boot
3. GPIO 4 set to LOW → Power cut
4. Wait (15–30s)
5. GPIO 4 HIGH again

---

## 🔄 RS485 Line Enable

- **GPIO 18** enables the transceiver for TX
- Kept LOW during idle
- Pulled HIGH only when sending sensor commands

This prevents bus collisions and is toggled automatically inside `send_message()`.

---

## 🛠 Relay Control (Optional)

Some setups include relays controlled by GPIO 21:

- `Relay.py` and `Mosfet.py` implement logic to power-cycle sensors with delay
- `PihatRelay` class toggles GPIO and logs output state
- Alternate to pure MOSFET switching if physical line control is needed

---

## ⚠️ Implementation Notes

- Always use `GPIO.cleanup()` in exception handlers
- Never toggle GPIOs simultaneously
- Add delays (`time.sleep`) between transitions

---

## 🔗 Related Documents

- [sensor_hardware.md](sensor_hardware.md)
- [power_management.md](power_management.md)
- [switch_mosfet.py](../code/setup-plensor/switch_mosfet.py)
- [Relay.py](../code/setup-plensor/Relay.py)
- [message_handler.py](../code/measure-plensor/artifact/message_handler.py)
