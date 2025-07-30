import sys
import json
import os
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton, QLineEdit, QApplication,
    QComboBox, QHBoxLayout, QFileDialog, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt

SETTINGS_FILE = "Interface-guis/json_files/measurement_config.json"

def load_settings():
    """Load settings from JSON file or return default values if file doesn't exist."""
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    else:
        # Default global settings with new structure (no DAMPING command)
        return {
            "sensors": ["#00020", "#00021"],
            "measurement_interval": 300,
            "log_level": "INFO",
            "metadata": {
                "folder": "C:/Users/thijb/Desktop",
                "pi_id": "plensepi00DEV",
                "customer_id": "#PLENSE",
                "pilot_id": "#OFFICE_TEST",
                "test_id": "#GERBERA",
                "sensor_type": "PLENSOR",
                "sensor_version": "V5.0"
            },
            "measurement_settings": {
                "BLOCK": {
                    "command": "BLOCK",
                    "duration": 50000,
                    "start_frequency": 20000,
                    "stop_frequency": 100000,
                    "repetitions": 20,
                    "damping_level": 200
                },
                "SINE": {
                    "command": "SINE",
                    "duration": 50000,
                    "start_frequency": 20000,
                    "stop_frequency": 100000,
                    "repetitions": 20,
                    "damping_level": 200
                },
                "ENV": {"command": "ENV"}
            },
            "default_measurement_sequence": ["SINE", "ENV"],
            "measurement_sequence": [],
            "sensor_specific_settings": {},
            "measurement_plans": []  # Initially empty
        }

def save_settings(data):
    """Save settings to JSON file."""
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f, indent=4)

class SettingsWindow(QWidget):
    def __init__(self, plan_index=None):
        """
        If plan_index is None, the window edits the global (single measurement) settings.
        Otherwise, it edits the measurement plan at settings["measurement_plans"][plan_index].
        """
        super().__init__()
        self.plan_index = plan_index
        # Store previous numeric values so that if a field is left blank, we can restore it.
        self._prev_values = {}
        self.init_ui()
        self.load_settings_into_ui()

    def init_ui(self):
        title = "Measurement Settings" if self.plan_index is None else f"Measurement Plan Settings (Plan {self.plan_index + 1})"
        self.setWindowTitle(title)
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(100, 100, int(screen.width() * 0.7), int(screen.height() * 0.8))

        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # Title label
        title_label = QLabel("Changing " + ("Measurement Settings" if self.plan_index is None else "Measurement Plan Settings"), self)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        left_layout.addWidget(title_label)

        # In plan mode, add a field for the plan name.
        if self.plan_index is not None:
            self.plan_name_input = QLineEdit(self)
            self.plan_name_input.setPlaceholderText("Plan Name")
            left_layout.addWidget(QLabel("Plan Name:", self))
            left_layout.addWidget(self.plan_name_input)

        # Description text
        description = ("Modify the settings for measurement operations. Changes will be saved to the configuration file."
                       if self.plan_index is None else
                       "Modify the settings for this measurement plan. Changes will be saved to the configuration file.")
        description_label = QLabel(description, self)
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(description_label)

        # Sensors fields
        self.sensors_input = QLineEdit(self)
        self.sensors_input.setPlaceholderText("Sensors (comma-separated)")
        left_layout.addWidget(QLabel("Active Sensors:", self))
        left_layout.addWidget(self.sensors_input)

        # Folder / Output path field
        self.folder_input = QLineEdit(self)
        placeholder = "Folder Path" if self.plan_index is None else "Plan Output Path"
        self.folder_input.setPlaceholderText(placeholder)
        left_layout.addWidget(QLabel("Data Folder:" if self.plan_index is None else "Plan Output Path:", self))
        left_layout.addWidget(self.folder_input)

        self.output_path_button = QPushButton("Select Output Path", self)
        self.output_path_button.clicked.connect(self.select_output_path)
        left_layout.addWidget(self.output_path_button)

        # Global metadata fields (only for single measurement/global settings)
        if self.plan_index is None:
            self.pi_id_input = QLineEdit(self)
            self.pi_id_input.setPlaceholderText("PI ID")
            left_layout.addWidget(QLabel("PI ID:", self))
            left_layout.addWidget(self.pi_id_input)

            self.customer_id_input = QLineEdit(self)
            self.customer_id_input.setPlaceholderText("Customer ID")
            left_layout.addWidget(QLabel("Customer ID:", self))
            left_layout.addWidget(self.customer_id_input)

            self.pilot_id_input = QLineEdit(self)
            self.pilot_id_input.setPlaceholderText("Pilot ID")
            left_layout.addWidget(QLabel("Pilot ID:", self))
            left_layout.addWidget(self.pilot_id_input)

            self.test_id_input = QLineEdit(self)
            self.test_id_input.setPlaceholderText("Test ID")
            left_layout.addWidget(QLabel("Test ID:", self))
            left_layout.addWidget(self.test_id_input)

            self.sensor_type_input = QLineEdit(self)
            self.sensor_type_input.setPlaceholderText("Sensor Type")
            left_layout.addWidget(QLabel("Sensor Type:", self))
            left_layout.addWidget(self.sensor_type_input)

            self.sensor_version_input = QLineEdit(self)
            self.sensor_version_input.setPlaceholderText("Sensor Version")
            left_layout.addWidget(QLabel("Sensor Version:", self))
            left_layout.addWidget(self.sensor_version_input)

        # Interval field
        self.interval_input = QLineEdit(self)
        placeholder = "Measurement Interval (s)" if self.plan_index is None else "Plan Interval (s)"
        self.interval_input.setPlaceholderText(placeholder)
        left_layout.addWidget(QLabel("Measurement Interval:" if self.plan_index is None else "Plan Interval:", self))
        left_layout.addWidget(self.interval_input)

        # Measurement Sequence field
        self.sequence_input = QLineEdit(self)
        placeholder = "Measurement Sequence (comma-separated)" if self.plan_index is None else "Plan Sequence (comma-separated)"
        self.sequence_input.setPlaceholderText(placeholder)
        left_layout.addWidget(QLabel("Measurement Sequence:" if self.plan_index is None else "Plan Sequence:", self))
        left_layout.addWidget(self.sequence_input)

        # Damping Level field (used for both BLOCK and SINE commands)
        self.damping_level_input = QLineEdit(self)
        self.damping_level_input.setPlaceholderText("Damping Level")
        left_layout.addWidget(QLabel("Damping Level:", self))
        left_layout.addWidget(self.damping_level_input)

        # Extra Parameters for BLOCK/SINE with explanation labels.
        self.extra_params_label = QLabel("Extra Parameters (for BLOCK/SINE):", self)
        left_layout.addWidget(self.extra_params_label)
        self.duration_input = QLineEdit(self)
        self.duration_input.setPlaceholderText("Duration (microseconds)")
        left_layout.addWidget(self.duration_input)
        self.start_freq_input = QLineEdit(self)
        self.start_freq_input.setPlaceholderText("Start Frequency (Hz)")
        left_layout.addWidget(self.start_freq_input)
        self.stop_freq_input = QLineEdit(self)
        self.stop_freq_input.setPlaceholderText("Stop Frequency (Hz)")
        left_layout.addWidget(self.stop_freq_input)
        self.repetitions_input = QLineEdit(self)
        self.repetitions_input.setPlaceholderText("Repetitions (integer)")
        left_layout.addWidget(self.repetitions_input)
        self.set_extra_params_visibility(False)

        # Command selection dropdown.
        # Since DAMPING is no longer a command, only list BLOCK, SINE, and ENV.
        left_layout.addWidget(QLabel("Select Measurement Command:", self))
        self.command_selection = QComboBox(self)
        self.command_selection.addItems(["BLOCK", "SINE", "ENV"])
        self.command_selection.currentTextChanged.connect(self.load_command_settings)
        left_layout.addWidget(self.command_selection)

        # Current Settings Display on the right.
        right_layout.addWidget(QLabel("Current Settings:", self))
        self.current_settings_display = QTextEdit(self)
        self.current_settings_display.setReadOnly(True)
        right_layout.addWidget(self.current_settings_display)

        # Buttons Layout.
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save Settings", self)
        self.save_button.setStyleSheet("font-size: 18px; padding: 10px;")
        self.save_button.clicked.connect(self.save_settings_from_ui)
        button_layout.addWidget(self.save_button)
        self.close_button = QPushButton("Close", self)
        self.close_button.setStyleSheet("font-size: 18px; padding: 10px;")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)
        left_layout.addLayout(button_layout)

        main_layout.addLayout(left_layout, 2)
        main_layout.addLayout(right_layout, 1)
        self.setLayout(main_layout)

    def set_extra_params_visibility(self, visible: bool):
        self.extra_params_label.setVisible(visible)
        self.duration_input.setVisible(visible)
        self.start_freq_input.setVisible(visible)
        self.stop_freq_input.setVisible(visible)
        self.repetitions_input.setVisible(visible)

    def select_output_path(self):
        from PyQt6.QtWidgets import QFileDialog
        folder = QFileDialog.getExistingDirectory(self, "Select Output Path")
        if folder:
            self.folder_input.setText(folder)

    def load_settings_into_ui(self):
        settings = load_settings()
        if self.plan_index is None:
            # Global settings for single measurement.
            self.sensors_input.setText(", ".join(settings["sensors"]))
            self.folder_input.setText(settings["metadata"]["folder"])
            self.interval_input.setText(str(settings["measurement_interval"]))
            self.sequence_input.setText(", ".join(settings.get("measurement_sequence", [])))
            # Load damping_level from BLOCK (assumed to apply to both BLOCK and SINE).
            self.damping_level_input.setText(str(settings["measurement_settings"]["BLOCK"].get("damping_level", "0")))
            self._prev_values["damping_level"] = settings["measurement_settings"]["BLOCK"].get("damping_level", "0")
            # Load metadata fields.
            self.pi_id_input.setText(settings["metadata"].get("pi_id", ""))
            self.customer_id_input.setText(settings["metadata"].get("customer_id", ""))
            self.pilot_id_input.setText(settings["metadata"].get("pilot_id", ""))
            self.test_id_input.setText(settings["metadata"].get("test_id", ""))
            self.sensor_type_input.setText(settings["metadata"].get("sensor_type", ""))
            self.sensor_version_input.setText(settings["metadata"].get("sensor_version", ""))
            self.load_command_settings()
            # Display global settings without measurement_plans.
            global_display = {k: v for k, v in settings.items() if k != "measurement_plans"}
            self.current_settings_display.setText(json.dumps(global_display, indent=4))
        else:
            # Load settings for a specific measurement plan.
            plan = settings["measurement_plans"][self.plan_index]
            self.plan_name_input.setText(plan.get("plan_name", ""))
            self.sensors_input.setText(", ".join(plan["sensors"]))
            self.folder_input.setText(plan.get("output_path", ""))
            self.interval_input.setText(str(plan.get("interval", "")))
            self.sequence_input.setText(", ".join(plan.get("measurement_sequence", [])))
            if "BLOCK" in plan["measurement_settings"]:
                self.damping_level_input.setText(str(plan["measurement_settings"]["BLOCK"].get("damping_level", "")))
                self._prev_values["damping_level"] = plan["measurement_settings"]["BLOCK"].get("damping_level", "")
            else:
                self.damping_level_input.setText("")
            if plan["measurement_settings"]:
                first_cmd = list(plan["measurement_settings"].keys())[0]
                self.command_selection.setCurrentText(first_cmd)
            self.load_command_settings(plan_specific=True)
            self.current_settings_display.setText(json.dumps(plan, indent=4))

    def load_command_settings(self, plan_specific=False):
        settings = load_settings()
        if self.plan_index is None:
            command = self.command_selection.currentText()
            command_settings = settings["measurement_settings"].get(command, {})
        else:
            plan = settings["measurement_plans"][self.plan_index]
            command = self.command_selection.currentText()
            command_settings = plan["measurement_settings"].get(command, {})
        # Use damping_level instead of damping_byte.
        current_val = command_settings.get("damping_level", self._prev_values.get("damping_level", ""))
        self.damping_level_input.setText(str(current_val))
        if command in ["BLOCK", "SINE"]:
            self.set_extra_params_visibility(True)
            self.duration_input.setText(str(command_settings.get("duration", "")))
            self.start_freq_input.setText(str(command_settings.get("start_frequency", "")))
            self.stop_freq_input.setText(str(command_settings.get("stop_frequency", "")))
            self.repetitions_input.setText(str(command_settings.get("repetitions", "")))
        else:
            self.set_extra_params_visibility(False)

    def save_settings_from_ui(self):
        settings = load_settings()
        current_cmd = self.command_selection.currentText()
        try:
            damping_val = int(self.damping_level_input.text())
        except ValueError:
            damping_val = self._prev_values.get("damping_level", 0)
        
        # Get the sensors list and check if it's different from current settings
        new_sensors = [s.strip() for s in self.sensors_input.text().split(",") if s.strip()]
        sensors_changed = new_sensors != settings["sensors"]
        
        if self.plan_index is None:
            settings["sensors"] = new_sensors
            
            # Update the metadata file
            try:
                # Find the most recent metadata file
                metadata_dir = "/home/plense/metadata"
                metadata_files = [f for f in os.listdir(metadata_dir) if f.startswith("metadata_") and f.endswith(".json")]
                if metadata_files:
                    latest_metadata = sorted(metadata_files)[-1]
                    metadata_path = os.path.join(metadata_dir, latest_metadata)
                    
                    # Load and update metadata file
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                    
                    # Convert sensor IDs from string to decimal
                    decimal_sensors = []
                    for sensor in new_sensors:
                        try:
                            # Remove '#' and leading zeros, then convert to int
                            sensor_decimal = int(sensor.replace('#', '').lstrip('0'))
                            decimal_sensors.append({"sensor_id": sensor_decimal})
                        except ValueError:
                            print(f"Warning: Could not convert sensor ID {sensor} to decimal")
                    
                    # Update V5.0 sensors
                    if "sensor_versions" in metadata and "V5.0" in metadata["sensor_versions"]:
                        metadata["sensor_versions"]["V5.0"]["sensors"] = decimal_sensors
                        
                        # Save updated metadata
                        with open(metadata_path, 'w') as f:
                            json.dump(metadata, f, indent=2)
                    else:
                        print("Warning: Could not find V5.0 section in metadata file")
                    
            except Exception as e:
                QMessageBox.warning(self, "Warning", f"Could not update metadata file: {str(e)}")

            # Continue with existing settings save logic
            settings["metadata"]["folder"] = self.folder_input.text()
            settings["measurement_interval"] = int(self.interval_input.text())
            settings["measurement_sequence"] = [s.strip() for s in self.sequence_input.text().split(",") if s.strip()]
            settings["measurement_settings"][current_cmd]["damping_level"] = damping_val
            if current_cmd in ["BLOCK", "SINE"]:
                settings["measurement_settings"][current_cmd]["duration"] = int(self.duration_input.text() or 0)
                settings["measurement_settings"][current_cmd]["start_frequency"] = int(self.start_freq_input.text() or 0)
                settings["measurement_settings"][current_cmd]["stop_frequency"] = int(self.stop_freq_input.text() or 0)
                settings["measurement_settings"][current_cmd]["repetitions"] = int(self.repetitions_input.text() or 0)
            # Save metadata fields.
            settings["metadata"]["pi_id"] = self.pi_id_input.text()
            settings["metadata"]["customer_id"] = self.customer_id_input.text()
            settings["metadata"]["pilot_id"] = self.pilot_id_input.text()
            settings["metadata"]["test_id"] = self.test_id_input.text()
            settings["metadata"]["sensor_type"] = self.sensor_type_input.text()
            settings["metadata"]["sensor_version"] = self.sensor_version_input.text()
        else:
            plan = settings["measurement_plans"][self.plan_index]
            plan["plan_name"] = self.plan_name_input.text()
            plan["sensors"] = [s.strip() for s in self.sensors_input.text().split(",") if s.strip()]
            plan["output_path"] = self.folder_input.text()
            plan["interval"] = int(self.interval_input.text())
            plan["measurement_sequence"] = [s.strip() for s in self.sequence_input.text().split(",") if s.strip()]
            if current_cmd in plan["measurement_settings"]:
                plan["measurement_settings"][current_cmd]["damping_level"] = damping_val
                if current_cmd in ["BLOCK", "SINE"]:
                    plan["measurement_settings"][current_cmd]["duration"] = int(self.duration_input.text() or 0)
                    plan["measurement_settings"][current_cmd]["start_frequency"] = int(self.start_freq_input.text() or 0)
                    plan["measurement_settings"][current_cmd]["stop_frequency"] = int(self.stop_freq_input.text() or 0)
                    plan["measurement_settings"][current_cmd]["repetitions"] = int(self.repetitions_input.text() or 0)
        save_settings(settings)
        
        # Show restart message if sensors were changed
        if sensors_changed and self.plan_index is None:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setText("Sensor IDs have been updated")
            msg.setInformativeText("Please restart the Start Measurement application for the changes to take effect.")
            msg.setWindowTitle("Restart Required")
            msg.exec()

        if self.plan_index is None:
            global_display = {k: v for k, v in settings.items() if k != "measurement_plans"}
            self.current_settings_display.setText(json.dumps(global_display, indent=4))
        else:
            self.current_settings_display.setText(json.dumps(settings["measurement_plans"][self.plan_index], indent=4))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SettingsWindow()
    window.show()
    sys.exit(app.exec())