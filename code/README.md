# Plense Edge Code Repository

Welcome to the Plense edge code repository! This repository contains the complete software stack for Plensor sensor measurement and data processing systems running on Raspberry Pi edge devices.

## 🏗️ Repository Structure

```
edge-code/
├── 📁 measure-plensor/           # Core measurement application
│   ├── artifact/
│   │   ├── app.py               # Main measurement application
│   │   ├── sensor.py            # Sensor communication and control
│   │   ├── message_handler.py   # Message processing for Plensor
│   │   ├── queue_manager.py     # Measurement queue management
│   │   ├── calibrate_sensor_mixin.py
│   │   ├── set_damping_mixin.py
│   │   ├── set_sensor_id_mixin.py
│   │   ├── get_sensor_id_mixin.py
│   │   ├── reset_plensor_mixin.py
│   │   ├── serial_communication_setup.py
│   │   ├── message_packing_functions.py
│   │   ├── message_unpacking_functions.py
│   │   ├── error_logger.py      # Centralized error logging
│   │   ├── json_handler.py      # JSON configuration handling
│   │   └── requirements.txt
│   └── recipe/
│       ├── config.json          # Component configuration
│       └── docker_run.sh        # Local run script
│
├── 📁 process-data/             # Data processing and upload
│   ├── artifact/
│   │   ├── app.py              # Main processing application
│   │   ├── PreProcessor.py     # Signal preprocessing
│   │   ├── ComponentHandler.py # Component lifecycle management
│   │   ├── xedge_plense_tools.py # Signal processing utilities
│   │   ├── JSONHandler.py      # JSON data handling
│   │   ├── ErrorLogger.py      # Error logging
│   │   ├── settings.json       # Processing configuration
│   │   └── requirements.txt
│   └── recipe/
│       ├── config.json         # Component configuration
│       └── docker_run.sh       # Local run script
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
├── 📁 deployments/            # Deployment configurations
│   ├── app_settings.json      # Application settings
│   ├── measure_settings.json  # Measurement parameters
│   ├── metadata_example.json  # Example metadata structure
│   ├── generate_metadata_files.py # Metadata generation
│   ├── ddb_deployment_info.py # Deployment information
│   ├── check_damping_level.py # Damping level verification
│   ├── plensepi00003.json    # PI-specific configurations
│   ├── plensepi00004.json
│   ├── plensepi00008.json
│   ├── metadata_npec_drought_p01.json
│   ├── NPEC deployment/      # NPEC pilot configurations
│   ├── KWS deployment/       # KWS pilot configurations
│   └── timestream-data/      # Time series data handling
│       ├── add_pi_sensor_deployments.py
│       ├── add_pilot_pi_deployments.py
│       ├── DeploymentLogger.py
│       ├── ErrorLogger.py
│       └── requirements.txt
│
├── 📁 installer_scripts/      # Installation automation
│   ├── install_all.sh        # Complete installation script
│   ├── install_basic.sh      # Basic system setup
│   ├── install_plensor.sh    # Plensor-specific installation
│   ├── install_gg.sh         # Greengrass installation
│   ├── install_gsm.sh        # GSM modem installation
│   ├── install_flir.sh       # FLIR camera installation
│   └── get-docker.sh         # Docker installation
│
├── 📁 cron/                  # Scheduled tasks
│   ├── production.cron       # User-level cron jobs
│   └── production.root.cron  # Root-level cron jobs
│
├── 📁 log-manager/           # Centralized logging
│   ├── artifact/
│   │   ├── app.py           # Log management application
│   │   ├── ErrorLogger.py   # Error logging utilities
│   │   ├── JSONHandler.py   # JSON log handling
│   │   ├── upload_log.py    # Log upload functionality
│   │   ├── run_log_manager.sh # Log manager script
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── recipe/
│       └── config.json      # Log manager configuration
│
├── 📁 rpi-health/           # Raspberry Pi health monitoring
│   ├── artifact/
│   │   ├── start.py         # Health monitoring startup
│   │   ├── log_health_metrics.py # Health metric logging
│   │   ├── process_health_metrics.py # Health data processing
│   │   ├── ErrorLogger.py   # Error logging
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── recipe/
│       ├── config.json      # Health monitoring configuration
│       └── docker_run.sh    # Local run script
│
├── 📁 modem-manager/        # GSM modem management
│   └── modem_manager.sh     # Modem control script
│
├── 📁 setup-plensor/        # Plensor hardware setup
│   ├── app_dev.py          # Development setup application
│   ├── Mosfet.py           # MOSFET control
│   ├── Relay.py            # Relay control
│   ├── switch_mosfet.py    # MOSFET switching logic
│   ├── open_pin_4_8.py     # GPIO pin control
│   ├── close_pin_4.py      # GPIO pin control
│   └── ErrorLogger.py      # Error logging
│
├── 📁 scripts/              # Utility scripts
│   ├── component.py         # Component management
│   └── deployment.py        # Deployment utilities
│
├── 📄 README.md             # This file
├── 📄 requirements.txt      # Global Python dependencies
├── 📄 setup.cfg            # Code style configuration
├── 📄 Plensor#99999_metadata.json # Example metadata
├── 📄 runs.json            # Measurement run configurations
└── 📄 .gitignore           # Git ignore patterns
```

## 🎯 Core Components

### 1. **Measure-Plensor** (`measure-plensor/`)
The core measurement application that communicates with Plensor sensors and manages the measurement process.

**Key Features:**
- Serial communication with Plensor sensors
- Measurement queue management
- Sensor calibration and configuration
- Damping level control
- Real-time measurement scheduling
- Error logging and recovery

**Main Entry Point:** `measure-plensor/artifact/app.py`

### 2. **Process-Data** (`process-data/`)
Handles data processing, signal analysis, and local storage management.

**Key Features:**
- Signal preprocessing and analysis
- Time-domain and frequency-domain processing
- Local data organization
- Measurement metadata management
- Error handling and logging

**Main Entry Point:** `process-data/artifact/app.py`

### 3. **Interface-GUIs** (`Interface-guis/`)
Provides user interfaces for measurement control and monitoring.

**Key Features:**
- Main GUI application for measurement control
- Single measurement interface
- Continuous measurement interface
- Measurement planning tools
- Debug and monitoring interface
- Handheld device interface

**Main Entry Point:** `Interface-guis/app.py`

### 4. **Metadata Management** (`metadata/`)
Manages sensor and deployment metadata using a Streamlit web interface.

**Key Features:**
- Web-based metadata editor
- Object metadata management
- Deployment configuration
- SQLite database storage

**Main Entry Point:** `metadata/metadata_app.py`

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Raspberry Pi (for production deployment)
- Plensor sensor hardware
- Required Python packages (see `requirements.txt`)

### Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd edge-code
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure deployment settings:**
   - Copy and modify deployment JSON files in `deployments/`
   - Update `measure_settings.json` for your measurement parameters
   - Configure `app_settings.json` for application behavior

4. **Start the measurement application:**
   ```bash
   python measure-plensor/artifact/app.py
   ```

5. **Start the GUI interface:**
   ```bash
   python Interface-guis/app.py
   ```

6. **Run the metadata manager:**
   ```bash
   cd metadata
   streamlit run metadata_app.py
   ```

## 📋 Configuration

### Measurement Settings (`deployments/measure_settings.json`)
Controls measurement parameters including:
- Frequency ranges
- Duration settings
- Damping levels
- Repetition counts
- Sensor-specific configurations

### Application Settings (`deployments/app_settings.json`)
Controls application behavior including:
- Logging levels
- Directory paths
- Processing parameters
- Error handling settings

### Deployment Configurations (`deployments/`)
Contains PI-specific and pilot-specific configurations:
- `plensepi00003.json`, `plensepi00004.json`, etc.
- Pilot-specific settings for NPEC, KWS deployments

## 🔧 Key Features

### Measurement Process
1. **Sensor Communication:** Serial communication with Plensor sensors
2. **Queue Management:** Organized measurement scheduling
3. **Data Collection:** Raw measurement data capture
4. **Local Storage:** Organized file structure for measurements
5. **Error Recovery:** Automatic sensor reconnection and error handling

### Data Processing
1. **Signal Analysis:** Time and frequency domain processing
2. **Preprocessing:** Signal filtering and normalization
3. **Metadata Management:** Measurement context and parameters
4. **Local Organization:** Structured data storage

### User Interface
1. **Measurement Control:** Start/stop measurements
2. **Settings Management:** Configure measurement parameters
3. **Real-time Monitoring:** Live measurement status
4. **Debug Tools:** System diagnostics and troubleshooting

## 📁 Data Structure

### Local Storage
```
/home/plense/
├── plensor_data/           # Measurement data
│   ├── audio_data/
│   │   ├── time_domain_not_processed/
│   │   └── time_domain_processed/
│   └── metadata/
├── metadata/               # Sensor metadata
├── error_logs/            # Error logs
└── health_metrics/        # System health data
```

### File Naming Convention
- Raw measurements: `{sensor_id}_{timestamp}_{frequency}_{damping}.flac`
- Processed data: `{sensor_id}_{timestamp}_{frequency}_{damping}_processed.npy`
- Metadata: `{sensor_id}_metadata.json`

## 🛠️ Development

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Document functions and classes
- Handle errors gracefully

### Testing
- Test sensor communication independently
- Verify measurement accuracy
- Check data processing pipeline
- Validate GUI functionality

### Logging
- Centralized error logging via `ErrorLogger`
- Structured log formats
- Configurable log levels
- Automatic log rotation

## 📞 Support

For questions or issues:
1. Check the error logs in `/home/plense/error_logs/`
2. Review the debug interface in the GUI
3. Verify sensor connections and configurations
4. Check deployment settings and metadata

---

**Note:** This repository is designed for local operation. Docker components have been excluded as per your requirements. The system can run entirely on local hardware without cloud dependencies.
