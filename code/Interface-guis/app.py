import sys
import os
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QMainWindow, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from settings_window import SettingsWindow  # Our updated settings window with plan support
from single_measurement_window import SingleMeasurementInspection
from measurement_plan_window import MeasurementPlanWindow  # New file for plan management
from debug_window import DebugWindow  # Import the full DebugWindow implementation
from continuous_measurement_window import ContinuousMeasurementWindow  # New continuous measurement window

class SingleMeasurementWindow(QWidget):
    def __init__(self):
        super().__init__()
        # Open the full Single Measurement Inspection window.
        self.inspection = SingleMeasurementInspection()
        self.inspection.setWindowTitle("Single Measurement Inspection")
        self.inspection.show()

class PlenseMainGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.measurement_app_proc = None  # Holds the process running the measurement app
        self.init_ui()

    def closeEvent(self, event):
        """Handle the window close event by closing the application."""
        if self.measurement_app_proc is not None and self.measurement_app_proc.poll() is None:
            self.measurement_app_proc.terminate()
        QApplication.quit()
        event.accept()

    def init_ui(self):
        self.setWindowTitle("Plense Measurement GUI")
        self.setGeometry(100, 100, 500, 500)

        central_widget = QWidget()
        layout = QVBoxLayout()

        title_label = QLabel("Plense Measurement GUI", self)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title_label)

        # New: Start/Stop Measurement App button.
        self.measurement_app_btn = QPushButton("Start Measurement App", self)
        self.measurement_app_btn.setStyleSheet("font-size: 18px; padding: 15px;")
        self.measurement_app_btn.clicked.connect(self.toggle_measurement_app)
        layout.addWidget(self.measurement_app_btn)

        self.single_measurement_btn = QPushButton("Single Measurement", self)
        self.continuous_measurement_btn = QPushButton("Continuous Measurement", self)
        self.change_settings_btn = QPushButton("Change Default Measurement Settings", self)
        self.create_plan_btn = QPushButton("Create Measurement Plan", self)
        self.debug_btn = QPushButton("Debug", self)

        button_style = "font-size: 18px; padding: 15px;"
        for button in [self.single_measurement_btn,
                       self.change_settings_btn, self.create_plan_btn,
                       self.continuous_measurement_btn, self.debug_btn]:
            button.setStyleSheet(button_style)
            layout.addWidget(button)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.single_measurement_btn.clicked.connect(self.open_single_measurement)
        self.change_settings_btn.clicked.connect(self.open_global_settings)
        self.create_plan_btn.clicked.connect(self.open_plan)
        self.continuous_measurement_btn.clicked.connect(self.open_continuous_measurement)
        self.debug_btn.clicked.connect(self.open_debug)

    def toggle_measurement_app(self):
        """
        Toggle the measurement app: if not running, start it; if running, terminate it.
        """
        # If the process is running, then stop it.
        if self.measurement_app_proc is not None and self.measurement_app_proc.poll() is None:
            try:
                self.measurement_app_proc.terminate()
                self.measurement_app_proc.wait()
                self.measurement_app_proc = None
                self.measurement_app_btn.setText("Start Measurement App")
                QMessageBox.information(self, "Measurement App Stopped", "Measurement app has been stopped.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to stop measurement app:\n{e}")
            return

        # Otherwise, start the measurement app.
        script_path = os.path.join("measure-plensor", "artifact", "app.py")
        try:
            self.measurement_app_proc = subprocess.Popen(["python", script_path])
            self.measurement_app_btn.setText("Stop Measurement App")
            # Use a timer to monitor the process and update the button when it finishes.
            timer = QTimer(self)
            timer.setInterval(500)
            timer.timeout.connect(lambda: self.check_measurement_app(timer))
            timer.start()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to start measurement app:\n{e}")

    def check_measurement_app(self, timer):
        """Poll the measurement app process and update the button when finished."""
        if self.measurement_app_proc is None or self.measurement_app_proc.poll() is not None:
            timer.stop()
            self.measurement_app_btn.setText("Start Measurement App")
            self.measurement_app_proc = None

    def open_single_measurement(self):
        self.single_measurement_window = SingleMeasurementInspection()
        self.single_measurement_window.show()

    def open_global_settings(self):
        self.settings_window = SettingsWindow(plan_index=None)
        self.settings_window.show()

    def open_plan(self):
        self.measurement_plan_window = MeasurementPlanWindow()
        self.measurement_plan_window.show()

    def open_continuous_measurement(self):
        self.continuous_measurement_window = ContinuousMeasurementWindow()
        self.continuous_measurement_window.show()

    def open_debug(self):
        self.debug_window = DebugWindow()
        self.debug_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = PlenseMainGUI()
    main_window.show()
    sys.exit(app.exec())
