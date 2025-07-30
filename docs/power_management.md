# Power Management

This document outlines how the Plensor system models and manages power distribution across multiple sensors, including current limits, voltage drops, and deployment constraints.

---

## 🔌 System Power Source

- **Input Voltage**: 12V DC regulated supply
- **Connected Via**: Barrel jack into the Pi Hat
- **Shared Load**: Powers both the Raspberry Pi and up to 12 sensors

---

## ⚡ Sensor Power Characteristics

Each Plensor sensor:
- Draws high current pulses during measurement (~hundreds of mA)
- Consumes <10 mA during idle
- Generates load peaks that affect voltage stability

---

## 📉 Voltage Drop Behavior

During large deployments (e.g., NPEC), voltage drops were observed when running 17+ sensors.

### Observed Effects:
- Sensor reset loops
- Data corruption
- Failed measurement ACKs

### Primary Resistance Sources:
- Pi Hat trace and solder resistance
- Terminal block resistance
- Long cable lengths

---

## 📈 Nonlinear Voltage Model

A model was fitted to explain the nonlinearity of power degradation:

```
V_out = V_in - (a * N^b)
```

Where:
- `V_in` is input voltage (12V)
- `N` is number of sensors
- `a`, `b` are empirically derived constants

Fit data shows power failure risk beyond 12–13 sensors.

---

## 🔁 Mitigation Strategies

- Use shorter cables with thicker gauge
- Switch to powered splitters for >12 sensors
- Introduce capacitor banks near sensor terminals
- Enable automatic power reset cycle (see [gpio_and_relay_setup.md](gpio_and_relay_setup.md))

---

## 🛠 Practical Limits

| Condition                | Safe Sensor Count |
|--------------------------|-------------------|
| Direct DC jack only      | ≤ 12              |
| With powered splitter    | 13–30             |
| USB-C + GPIO bypass      | ❌ Not supported  |

---

## 🧪 Test Data Summary

Measured voltage (V) vs number of sensors:

| Sensors | V_min during burst |
|---------|---------------------|
| 1       | 11.92               |
| 5       | 11.74               |
| 10      | 11.32               |
| 15      | 10.21               |
| 17      | 9.66 (Fail)         |

---

## 🔗 Related Documents

- [sensor_hardware.md](sensor_hardware.md)
- [gpio_and_relay_setup.md](gpio_and_relay_setup.md)
- [deployment_config.json](../deployments/)

