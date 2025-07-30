import sys
import os
import json
import time
import shutil
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox, QApplication, QMessageBox
)
from PyQt6.QtCore import Qt
from settings_window import SettingsWindow, load_settings
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

class SingleMeasurementInspection(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Single Measurement Inspection")
        self.setGeometry(100, 100, 900, 700)
        main_layout = QVBoxLayout()

        # --- Top controls: sensor dropdown, measure button, change settings button ---
        top_layout = QHBoxLayout()
        sensor_label = QLabel("Sensor ID:")
        sensor_label.setStyleSheet("font-size: 18px;")
        top_layout.addWidget(sensor_label)
        
        self.sensor_dropdown = QComboBox()
        self.sensor_dropdown.setStyleSheet("font-size: 18px; padding: 5px;")
        config = load_settings()
        for sensor in config.get("sensors", []):
            self.sensor_dropdown.addItem(sensor)
        top_layout.addWidget(self.sensor_dropdown)

        self.measure_button = QPushButton("Measure")
        self.measure_button.setStyleSheet("font-size: 18px; padding: 15px;")
        self.measure_button.clicked.connect(self.perform_measurement)
        top_layout.addWidget(self.measure_button)

        self.change_settings_button = QPushButton("Change Measurement Settings")
        self.change_settings_button.setStyleSheet("font-size: 18px; padding: 15px;")
        self.change_settings_button.clicked.connect(self.open_settings)
        top_layout.addWidget(self.change_settings_button)

        main_layout.addLayout(top_layout)

        # --- Info display: damping level, measurement sequence, output path, max absolute ---
        info_layout = QVBoxLayout()
        self.damping_level_label = QLabel("Damping Level: N/A")
        self.measurement_sequence_label = QLabel("Measurement Sequence: N/A")
        self.output_path_label = QLabel("Output Path: N/A")
        self.max_abs_label = QLabel("Max Absolute: N/A")
        for label in [self.damping_level_label, self.measurement_sequence_label, self.output_path_label, self.max_abs_label]:
            label.setStyleSheet("font-size: 16px;")
            info_layout.addWidget(label)
        main_layout.addLayout(info_layout)

        # --- Plot display: two subplots (time domain and power spectrum) ---
        self.fig, (self.ax_time, self.ax_power) = plt.subplots(2, 1, figsize=(8, 6), sharex=False)
        self.fig.tight_layout(pad=3)
        self.ax_time.grid(True)
        self.ax_power.grid(True)
        self.time_power_canvas = FigureCanvas(self.fig)
        main_layout.addWidget(self.time_power_canvas)

        self.setLayout(main_layout)

    def open_settings(self):
        self.settings_window = SettingsWindow()
        self.settings_window.show()

    def perform_measurement(self):
        """
        Build the measurement interrupt (excluding any DAMPING command),
        and for BLOCK and SINE commands add a "damping_level" field.
        Then write the interrupt file (always named message_interrupt.json)
        and scan for a new FLAC file.
        """
        config = load_settings()
        selected_sensor = self.sensor_dropdown.currentText()
        if selected_sensor.startswith("#"):
            try:
                sensor_id = int(selected_sensor.lstrip("#"))
            except ValueError:
                sensor_id = selected_sensor
        else:
            sensor_id = selected_sensor

        measurement_sequence = config.get("measurement_sequence", [])
        measurement_settings = config.get("measurement_settings", {})

        interrupt = []
        for cmd in measurement_sequence:
            # Skip any DAMPING command (it is now merged with BLOCK and SINE)
            if cmd.upper() == "DAMPING":
                continue
            settings = measurement_settings.get(cmd, {}).copy()
            if settings:
                # For BLOCK and SINE, add a damping_level field.
                if cmd.upper() in ["SINE", "BLOCK"]:
                    # If SINE has its own damping_level use that; otherwise, use BLOCK's value.
                    damping_value = settings.get("damping_level", 
                                    measurement_settings.get("BLOCK", {}).get("damping_level", 0))
                    settings["damping_level"] = damping_value
                msg = {"sensor_id": sensor_id, "measurement_settings": {"type": "measure"}}
                # (If a "damping" key exists, move it to "command" ? should not happen now.)
                if "damping" in settings:
                    settings["command"] = settings.pop("damping")
                msg["measurement_settings"].update(settings)
                interrupt.append(msg)
        
        # Write the interrupt file (always named message_interrupt.json).
        metadata_dir = "/home/plense/metadata"
        if not os.path.exists(metadata_dir):
            os.makedirs(metadata_dir)
        interrupt_path = os.path.join(metadata_dir, "message_interrupt.json")
        with open(interrupt_path, "w") as f:
            json.dump(interrupt, f, indent=4)
        print("Interrupt file written:", json.dumps(interrupt, indent=4))

        # Update info labels.
        # Display the damping_level from the BLOCK settings as default.
        damping_value = measurement_settings.get("BLOCK", {}).get("damping_level", "N/A")
        self.damping_level_label.setText(f"Damping Level: {damping_value}")
        self.measurement_sequence_label.setText(f"Measurement Sequence: {', '.join(measurement_sequence)}")

        # Scan for new .flac file.
        time_domain_folder = "/home/plense/plensor_data/audio_data/time_domain_not_processed"
        existing_files = set(os.listdir(time_domain_folder))
        new_flac_file = None
        t0 = time.time()
        while time.time() - t0 < 20:
            current_files = set(os.listdir(time_domain_folder))
            for file in current_files - existing_files:
                if file.lower().endswith(".flac"):
                    new_flac_file = os.path.join(time_domain_folder, file)
                    break
            if new_flac_file:
                break
            time.sleep(0.5)
            print(f"Waiting for new .flac file in {time_domain_folder}...")
        
        if new_flac_file:
            print(f"Found new .flac file: {new_flac_file}")
            output_folder = config.get("metadata", {}).get("output_path", "")
            if not output_folder:
                output_folder = config.get("metadata", {}).get("folder", "")
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            destination = os.path.join(output_folder, os.path.basename(new_flac_file))
            shutil.move(new_flac_file, destination)
            try:
                data, samplerate = sf.read(destination)
                self.plot_data(data, samplerate)
                max_abs = np.max(np.abs(data))
                self.max_abs_label.setText(f"Max Absolute: {max_abs}")
                self.output_path_label.setText(f"Output Path: {destination}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load FLAC file: {e}")
        else:
            QMessageBox.warning(self, "File Not Found", "No new .flac file detected.")
            self.clear_data()

    def plot_data(self, data, samplerate):
        self.fig.clf()
        self.ax_time = self.fig.add_subplot(211)
        self.ax_power = self.fig.add_subplot(212)
        t = np.linspace(0, len(data) / samplerate, num=len(data))
        self.ax_time.plot(t, data, color='blue')
        self.ax_time.set_title("Time Domain")
        self.ax_time.set_xlabel("Time (s)")
        self.ax_time.set_ylabel("Amplitude")
        self.ax_time.set_ylim(-1, 1)
        self.ax_time.grid(True)
        fft_data = np.fft.rfft(data)
        freqs = np.fft.rfftfreq(len(data), d=1/samplerate)
        power = np.abs(fft_data) ** 2
        epsilon = 1e-12
        power_db = 10 * np.log10(np.maximum(power, epsilon))
        self.ax_power.plot(freqs, power_db, color='red')
        self.ax_power.set_title("Power Spectrum (dB)")
        self.ax_power.set_xlabel("Frequency (Hz)")
        self.ax_power.set_ylabel("Power (dB)")
        self.ax_power.grid(True)
        self.fig.tight_layout(pad=3)
        self.time_power_canvas.draw()

    def clear_data(self):
        self.fig.clf()
        self.ax_time = self.fig.add_subplot(211)
        self.ax_power = self.fig.add_subplot(212)
        self.ax_time.set_title("Time Domain")
        self.ax_time.set_xlabel("Time (s)")
        self.ax_time.set_ylabel("Amplitude")
        self.ax_time.grid(True)
        self.ax_power.set_title("Power Spectrum (dB)")
        self.ax_power.set_xlabel("Frequency (Hz)")
        self.ax_power.set_ylabel("Power (dB)")
        self.ax_power.grid(True)
        self.fig.tight_layout(pad=3)
        self.time_power_canvas.draw()
        self.damping_level_label.setText("Damping Level: N/A")
        self.measurement_sequence_label.setText("Measurement Sequence: N/A")
        self.output_path_label.setText("Output Path: N/A")
        self.max_abs_label.setText("Max Absolute: N/A")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SingleMeasurementInspection()
    window.show()
    sys.exit(app.exec())
