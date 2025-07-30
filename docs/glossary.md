# Glossary

This glossary defines key technical terms and acronyms used throughout the Plensor documentation and codebase.

---

## A

**ACK (Acknowledge)**  
Byte (`0x06`) returned by sensors to confirm command success.

**Amplitude**  
Signal strength or magnitude, often normalized in the envelope.

---

## B

**Block Wave**  
A square wave burst used to excite the sensor for TOF or echo analysis.

**Burst**  
A short signal pulse emitted by the sensor, often repeated several times.

---

## C

**Calibration**  
Sensor initialization process that stores signal parameters.

**Checksum**  
Single-byte XOR value used to validate message integrity.

---

## D

**Damping Byte**  
Optional parameter that tapers burst signal edges. Range: 0–255.

**Deployment**  
A project-specific installation of sensors and Pi units at a defined location.

---

## E

**Envelope**  
Smoothed amplitude signal used to detect TOF peaks.

**ErrorLogger**  
Custom logging module that writes tracebacks and logs to `error.log`.

---

## F

**FFT (Fast Fourier Transform)**  
Converts time-domain audio to frequency-domain spectrum.

---

## G

**GPIO (General Purpose Input/Output)**  
Raspberry Pi pins used to control relays, MOSFETs, and RS485 TX line.

---

## H

**Hilbert Transform**  
Mathematical method to extract signal envelope.

---

## I

**ID (Sensor ID)**  
Unique RS485 address (0x01–0xFF) assigned to each sensor.

**Interrupt**  
JSON-based signal that modifies queue or resets sensors mid-run.

---

## J

**JSON (JavaScript Object Notation)**  
Lightweight file format for metadata and measurement summaries.

---

## M

**Metadata**  
Structured information describing the context of a measurement session.

**MOSFET**  
Transistor used to switch sensor power via GPIO.

---

## N

**NAK (Negative Acknowledge)**  
Byte (`0x15`) returned when a command fails.

---

## P

**Peak Amplitude**  
Maximum envelope value, used in TOF detection.

**Processing Log**  
JSON file documenting time and steps in signal pipeline.

---

## Q

**Queue**  
Ordered list of sensor commands executed during measurement.

---

## R

**RS485**  
Differential serial communication standard used between Pi and sensors.

**Repetition Count**  
Number of times a signal is emitted per command.

---

## S

**Sine Sweep**  
Frequency modulated wave burst sweeping from low to high frequency.

**Sensor**  
Ultrasonic transducer with custom firmware to receive commands and emit signals.

---

## T

**TOF (Time of Flight)**  
Delay between burst emission and echo return, measured in microseconds.

**Timestamp**  
Date-time identifier marking the start of a measurement cycle.

---

## U

**Uptime**  
Elapsed system time since last Pi reboot, logged in `health.log`.

---

## V

**Voltage**  
Commanded excitation voltage for bursts, specified in volts (e.g., 5V).

---

## W

**Watchdog**  
Script that monitors and restarts failed processes.

---

## 🔗 Related Documents

- [sensor_commands.md](sensor_commands.md)
- [data_structure.md](data_structure.md)
- [measurement_app.md](measurement_app.md)
