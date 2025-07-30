import sys
import os
import json
import subprocess
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit, QApplication, QMessageBox, QComboBox, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import QTimer, Qt
from settings_window import load_settings  # to load sensors

class DebugWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Debug Panel")
        self.setGeometry(100, 100, 800, 600)
        self.file_not_found_shown = False
        self.empty_file_shown = False
        self.init_ui()
        self.setup_timers()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Top row: Reset mosfet & Reset relay buttons
        top_button_layout = QHBoxLayout()
        self.reset_mosfet_btn = QPushButton("Reset mosfet", self)
        self.reset_mosfet_btn.setStyleSheet("font-size: 18px; padding: 10px;")
        self.reset_mosfet_btn.clicked.connect(self.run_mosfet_script)
        top_button_layout.addWidget(self.reset_mosfet_btn)
        
        self.reset_relay_btn = QPushButton("Reset relay", self)
        self.reset_relay_btn.setStyleSheet("font-size: 18px; padding: 10px;")
        self.reset_relay_btn.clicked.connect(self.run_relay_script)
        top_button_layout.addWidget(self.reset_relay_btn)
        main_layout.addLayout(top_button_layout)
        
        # Spacer between top buttons and command layout
        main_layout.addSpacing(10)
        
        # Sensor selection dropdown at the top
        sensor_select_layout = QHBoxLayout()
        sensor_label = QLabel("Sensor ID:", self)
        sensor_label.setStyleSheet("font-size: 18px;")
        sensor_select_layout.addWidget(sensor_label)
        self.sensor_debug_dropdown = QComboBox(self)
        self.sensor_debug_dropdown.setStyleSheet("font-size: 18px; padding: 5px;")
        defaults = load_settings().get("sensors", [])
        for sensor in defaults:
            self.sensor_debug_dropdown.addItem(str(sensor))
        sensor_select_layout.addWidget(self.sensor_debug_dropdown)
        main_layout.addLayout(sensor_select_layout)
        
        # Add spacing below dropdown
        main_layout.addSpacing(20)
        
        # Command layout: Two columns side by side
        command_layout = QHBoxLayout()
        
        # Left column: Loop commands
        loop_layout = QVBoxLayout()
        self.get_byte_loop_btn = QPushButton("GET Byte loop", self)
        self.get_byte_loop_btn.setStyleSheet("font-size: 18px; padding: 10px;")
        self.get_byte_loop_btn.clicked.connect(self.run_get_byte_loop)
        loop_layout.addWidget(self.get_byte_loop_btn)
        
        self.calibrate_loop_btn = QPushButton("Calibrate loop", self)
        self.calibrate_loop_btn.setStyleSheet("font-size: 18px; padding: 10px;")
        self.calibrate_loop_btn.clicked.connect(self.run_calibrate_loop)
        loop_layout.addWidget(self.calibrate_loop_btn)
        
        self.reset_sensor_loop_btn = QPushButton("Reset sensor loop", self)
        self.reset_sensor_loop_btn.setStyleSheet("font-size: 18px; padding: 10px;")
        self.reset_sensor_loop_btn.clicked.connect(self.run_reset_sensor_loop)
        loop_layout.addWidget(self.reset_sensor_loop_btn)
        
        # Right column: Single sensor commands
        sensor_layout = QVBoxLayout()
        
        self.get_byte_btn = QPushButton("GET Byte for sensor", self)
        self.get_byte_btn.setStyleSheet("font-size: 18px; padding: 10px;")
        self.get_byte_btn.clicked.connect(self.run_get_byte)
        sensor_layout.addWidget(self.get_byte_btn)
        
        self.calibrate_byte_btn = QPushButton("Calibrate Byte for sensor", self)
        self.calibrate_byte_btn.setStyleSheet("font-size: 18px; padding: 10px;")
        self.calibrate_byte_btn.clicked.connect(self.run_calibrate_byte)
        sensor_layout.addWidget(self.calibrate_byte_btn)
        
        self.reset_sensor_btn = QPushButton("Reset sensor", self)
        self.reset_sensor_btn.setStyleSheet("font-size: 18px; padding: 10px;")
        self.reset_sensor_btn.clicked.connect(self.run_reset_sensor)
        sensor_layout.addWidget(self.reset_sensor_btn)
        
        # Add both columns to command_layout with spacing between them
        command_layout.addLayout(loop_layout)
        command_layout.addSpacing(20)
        command_layout.addLayout(sensor_layout)
        main_layout.addLayout(command_layout)
        
        # Add spacing below the command layout and above the log text area.
        main_layout.addSpacing(20)
        
        # Log display area
        self.log_text = QTextEdit(self)
        self.log_text.setReadOnly(True)
        main_layout.addWidget(self.log_text)
        
        self.setLayout(main_layout)

    def setup_timers(self):
        self.log_timer = QTimer(self)
        self.log_timer.timeout.connect(self.update_log)
        self.log_timer.start(100)

    def update_log(self):
        log_file = os.path.join(os.pardir, "error_logs", "error.log")
        abs_path = os.path.abspath(log_file)
        if not os.path.exists(log_file):
            if self.log_text.toPlainText() != "Log file not found.":
                self.log_text.setPlainText("Log file not found.")
                if not self.file_not_found_shown:
                    QMessageBox.critical(self, "Log Error", f"Log file not found at:\n{abs_path}")
                    self.file_not_found_shown = True
            return
        else:
            self.file_not_found_shown = False

        try:
            # Check if the log file has been modified since the last update.
            current_mtime = os.path.getmtime(log_file)
            if hasattr(self, "last_log_mtime") and self.last_log_mtime == current_mtime:
                return  # No changes; skip updating.
            self.last_log_mtime = current_mtime

            with open(log_file, "r") as f:
                content = f.read()

            if not content.strip():
                if self.log_text.toPlainText() != "Log file is empty.":
                    self.log_text.setPlainText("Log file is empty.")
                    if not self.empty_file_shown:
                        QMessageBox.warning(self, "Log Warning", "Log file is empty.")
                        self.empty_file_shown = True
            else:
                self.empty_file_shown = False
                self.log_text.setPlainText(content)
                # Auto-scroll only when new content is loaded.
                self.log_text.verticalScrollBar().setValue(
                    self.log_text.verticalScrollBar().maximum()
                )
        except Exception as e:
            error_msg = f"Error reading log: {e}"
            if self.log_text.toPlainText() != error_msg:
                self.log_text.setPlainText(error_msg)
                QMessageBox.critical(self, "Log Error", f"Failed to read log file:\n{e}")

    def poll_process(self, proc, button):
        timer = QTimer(self)
        timer.setInterval(100)
        def check():
            if proc.poll() is not None:
                button.setEnabled(True)
                timer.stop()
        timer.timeout.connect(check)
        timer.start()

    def update_interrupt_messages(self, command, sensor_ids):
        messages = []
        for sensor in sensor_ids:
            try:
                if isinstance(sensor, str) and sensor.startswith("#"):
                    sensor_val = int(sensor.lstrip("#"))
                else:
                    sensor_val = sensor
            except Exception:
                sensor_val = sensor
            
            # Map commands to their corresponding message types and settings
            if command == "GET":
                msg = {
                    "sensor_id": sensor_val,
                    "measurement_settings": {
                        "type": "get_byte",
                        "calibrate_after": False
                    }
                }
            elif command == "CAL":
                msg = {
                    "sensor_id": sensor_val, 
                    "measurement_settings": {
                        "type": "calibrate",
                        "measure_after": False
                    }
                }
            elif command == "RST":
                msg = {
                    "sensor_id": sensor_val,
                    "measurement_settings": {
                        "type": "reset"
                    }
                }
            messages.append(msg)
            
        metadata_dir = "/home/plense/metadata"
        if not os.path.exists(metadata_dir):
            os.makedirs(metadata_dir)
        interrupt_path = os.path.join(metadata_dir, "message_interrupt.json")
        with open(interrupt_path, "w") as f:
            json.dump(messages, f, indent=4)
        QMessageBox.information(self, "Interrupt Updated", f"Message interrupt updated with command '{command}' for sensors: {sensor_ids}")

        
    def run_get_byte(self):
        sensor_id = self.sensor_debug_dropdown.currentText()
        self.update_interrupt_messages("GET", [sensor_id])

    def run_get_byte_loop(self):
        defaults = load_settings().get("sensors", [])
        self.update_interrupt_messages("GET", defaults)

    def run_calibrate_byte(self):
        sensor_id = self.sensor_debug_dropdown.currentText()
        self.update_interrupt_messages("CAL", [sensor_id])

    def run_calibrate_loop(self):
        defaults = load_settings().get("sensors", [])
        self.update_interrupt_messages("CAL", defaults)

    def run_reset_sensor(self):
        sensor_id = self.sensor_debug_dropdown.currentText()
        self.update_interrupt_messages("RST", [sensor_id])

    def run_reset_sensor_loop(self):
        defaults = load_settings().get("sensors", [])
        self.update_interrupt_messages("RST", defaults)

    # Preserve mosfet and relay functions:
    def run_mosfet_script(self):
        if not self.reset_mosfet_btn.isEnabled():
            return
        self.reset_mosfet_btn.setEnabled(False)
        script_path = os.path.join("setup-plensor", "Mosfet.py")
        try:
            proc = subprocess.Popen(["python", script_path])
            self.poll_process(proc, self.reset_mosfet_btn)
        except Exception as e:
            self.log_text.append(f"Error running Mosfet script: {e}")
            self.reset_mosfet_btn.setEnabled(True)

    def run_relay_script(self):
        if not self.reset_relay_btn.isEnabled():
            return
        self.reset_relay_btn.setEnabled(False)
        script_path = os.path.join("setup-plensor", "Relay.py")
        try:
            proc = subprocess.Popen(["python", script_path])
            self.poll_process(proc, self.reset_relay_btn)
        except Exception as e:
            self.log_text.append(f"Error running Relay script: {e}")
            self.reset_relay_btn.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DebugWindow()
    window.show()
    sys.exit(app.exec())
