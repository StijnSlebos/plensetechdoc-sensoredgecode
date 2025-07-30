# Plense Edge Code Repository

Welcome to the Plense edge code repository! This repository contains the complete software stack for Plensor sensor measurement and data processing systems running on Raspberry Pi edge devices.

## 🏗️ Repository Structure

```
edge-code/
├── 📁 measure-plensor/           # Core measurement application
│   └── artifact/
│       ├── app.py               # Main measurement application
│       ├── sensor.py            # Sensor communication and control
│       ├── message_handler.py   # Message processing for Plensor
│       ├── queue_manager.py     # Measurement queue management
│       ├── calibrate_sensor_mixin.py
│       ├── set_damping_mixin.py
│       ├── set_sensor_id_mixin.py
│       ├── get_sensor_id_mixin.py
│       ├── reset_plensor_mixin.py
│       ├── serial_communication_setup.py
│       ├── message_packing_functions.py
│       ├── message_unpacking_functions.py
│       ├── error_logger.py      # Centralized error logging
│       ├── json_handler.py      # JSON configuration handling
│       └── requirements.txt
│
├── 📁 process-data/             # Data processing and local storage
│   └── artifact/
│       ├── app.py              # Main processing application
│       ├── PreProcessor.py     # Signal preprocessing
│       ├── ComponentHandler.py # Component lifecycle management
│       ├── xedge_plense_tools.py # Signal processing utilities
│       ├── JSONHandler.py      # JSON data handling
│       ├── ErrorLogger.py      # Error logging
│       ├── settings.json       # Processing configuration
│       └── requirements.txt
│
├── 📁 Interface-guis/          # User interface applications
│   ├── app.py                  # Main GUI application
│   ├── settings_window.py      # Global settings management
│   ├── single_measurement_window.py # Single measurement interface
│   ├── continuous_measurement_window.py # Continuous measurement interface
│   ├── measurement_plan_window.py # Measurement planning
│   ├── debug_window.py         # Debug and monitoring interface
│   ├── quick_plot.py          # Quick data visualization
│   ├── continuous_measurement_functions.py # Continuous measurement logic
│   └── handheld_interface/     # Handheld device interface
│       ├── app_gui.py         # Handheld GUI
│       ├── app_measurehandler.py # Measurement handling
│       ├── complex_interrupt.py # Interrupt handling
│       ├── app_config.json    # Handheld configuration
│       ├── measurement_template.json
│       └── measurement_config.json
│
├── 📁 metadata/               # Metadata management
│   ├── metadata_app.py        # Streamlit metadata manager
│   ├── run_complex_interrupt.py # Interrupt handling
│   ├── continuous_measurements.db # SQLite metadata database
│   └── requirements.txt
│
├── 📁 log-manager/           # Centralized logging
│   └── artifact/
│       ├── app.py            # Log management application
│       ├── ErrorLogger.py    # Error logging utilities
│       ├── JSONHandler.py    # JSON handling utilities
│       ├── run_log_manager.sh # Log manager startup script
│       └── requirements.txt
│
├── 📁 rpi-health/            # System health monitoring
│   └── artifact/
│       ├── app.py           # Health monitoring application
│       ├── log_health_metrics.py # Health metrics logging
│       ├── process_health_metrics.py # Health data processing
│       ├── start.py         # Health monitoring startup
│       ├── ErrorLogger.py   # Error logging utilities
│       └── requirements.txt
│
├── 📁 setup-plensor/         # Plensor setup utilities
│   ├── app_dev.py           # Development setup application
│   ├── close_pin_4.py       # GPIO pin management
│   ├── open_pin_4_8.py      # GPIO pin management
│   ├── switch_mosfet.py     # MOSFET control
│   ├── Relay.py             # Relay control
│   ├── Mosfet.py            # MOSFET utilities
│   └── ErrorLogger.py       # Error logging utilities
│
├── 📁 modem-manager/         # GSM modem management
│   └── modem_manager.sh     # Modem management script
│
├── 📁 requirements.txt       # Main Python dependencies
├── 📁 setup.cfg             # Setup configuration
├── 📁 runs.json             # Run configuration data
└── 📁 README.md             # This file
```

## 🚀 Quick Start

### Prerequisites
- Raspberry Pi (3 or 4 recommended)
- Python 3.8+
- Plensor sensor hardware
- Basic Linux knowledge

### Installation
1. Clone this repository to your Raspberry Pi
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure your sensor settings in the appropriate configuration files
4. Run the measurement application:
   ```bash
   cd measure-plensor/artifact
   python app.py
   ```

## 📊 Data Storage

All data is now stored locally on the Raspberry Pi in the following structure:
- `/home/plense/plensor_data/` - Main data directory
  - `audio_data/` - Raw and processed audio measurements
  - `metadata/` - Measurement metadata
  - `environmental/` - Environmental sensor data
  - `tof/` - Time-of-flight measurements
  - `health_logs/` - System health metrics
  - `logs/` - Application logs

## 🔧 Configuration

### Measurement Settings
Edit `process-data/artifact/settings.json` to configure:
- Signal processing parameters
- Data storage locations
- Logging levels

### Sensor Configuration
Edit metadata files in the `metadata/` directory to configure:
- Sensor IDs and types
- Measurement parameters
- Calibration settings

## 📝 Logging

The system uses a centralized logging system:
- All logs are stored in `/home/plense/error_logs/`
- Log rotation is handled automatically
- Logs are backed up to `/home/plense/plensor_data/logs/`

## 🔍 Monitoring

### Health Monitoring
The RPi health monitoring system tracks:
- CPU temperature and usage
- Memory usage
- System uptime
- Storage capacity

### Data Processing
The data processing pipeline:
1. Captures sensor measurements
2. Preprocesses audio signals
3. Stores data locally with metadata
4. Generates health and performance logs

## 🛠️ Development

### Local Development
1. Set up a Python virtual environment
2. Install development dependencies
3. Use the Interface GUIs for testing
4. Monitor logs in real-time

### Testing
- Use the handheld interface for quick tests
- Run continuous measurements for extended testing
- Monitor system health during long runs

## 📚 Documentation

See the `docs/` directory for detailed documentation on:
- Architecture overview
- Communication protocols
- Configuration guides
- Troubleshooting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Important Notes

**Note:** This repository is designed for local operation. All cloud dependencies have been removed as per your requirements. The system can run entirely on local hardware without cloud dependencies.

## 🔗 Related Repositories

- [Plensor Hardware Documentation](link-to-hardware-docs)
- [Plense Cloud Services](link-to-cloud-services)
- [Plense Mobile App](link-to-mobile-app)
