import sys
import os
import time
import shutil
import numpy as np
import soundfile as sf

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QApplication, QMessageBox, QPlainTextEdit
)
from PyQt6.QtCore import Qt, QTimer

from settings_window import load_settings
from continuous_measurement_functions import schedule_measurement, process_measurement
from measurement_plan_window import MeasurementPlanWindow

class ContinuousMeasurementWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Continuous Measurement")
        self.setGeometry(100, 100, 600, 400)
        self.continuous_active = False
        self.plans = []
        # For each plan, store its next scheduled measurement time (timestamp)
        self.next_due = {}
        # The index of the plan currently being measured (or None if idle)
        self.current_plan_index = None
        # Global timer for waiting until the next scheduled measurement
        self.global_timer = QTimer(self)
        self.global_timer.setSingleShot(True)
        # (The connection for global_timer will be set in schedule_next_measurement)
        self.poll_timer = None  # Timer used for polling for a measurement result
        # Variables for the measurement in progress:
        self.current_start_time = None
        self.current_wait_duration = None
        self.current_existing_files = None

        self.init_ui()
        self.load_plans()

        # Progress display (updates every second)
        self.progress_display = QPlainTextEdit(self)
        self.progress_display.setReadOnly(True)
        self.progress_display.setStyleSheet("font-size: 14px;")
        self.layout().addWidget(self.progress_display)
        self.progress_timer = QTimer(self)
        self.progress_timer.setInterval(1000)
        self.progress_timer.timeout.connect(self.update_progress)

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Plan details display.
        self.plan_details_label = QLabel("", self)
        self.plan_details_label.setStyleSheet("font-size: 16px;")
        main_layout.addWidget(self.plan_details_label)

        # Buttons: Start/Stop and Change Measurement Plan.
        button_layout = QHBoxLayout()
        self.start_stop_btn = QPushButton("Start", self)
        self.start_stop_btn.setStyleSheet("font-size: 18px; padding: 10px;")
        self.start_stop_btn.clicked.connect(self.toggle_continuous)
        button_layout.addWidget(self.start_stop_btn)

        self.change_plan_btn = QPushButton("Change Measurement Plan", self)
        self.change_plan_btn.setStyleSheet("font-size: 18px; padding: 10px;")
        self.change_plan_btn.clicked.connect(self.open_plan_window)
        button_layout.addWidget(self.change_plan_btn)
        main_layout.addLayout(button_layout)

        # Status label.
        self.status_label = QLabel("Status: Idle", self)
        self.status_label.setStyleSheet("font-size: 16px;")
        main_layout.addWidget(self.status_label)

        self.setLayout(main_layout)

    def load_plans(self):
        settings = load_settings()
        self.plans = settings.get("measurement_plans", [])
        if self.plans:
            details = ""
            for i, plan in enumerate(self.plans):
                details += f"{i+1}. {plan.get('plan_name', 'Unnamed Plan')}: Sequence: {', '.join(plan.get('measurement_sequence', []))}\n"
                # Initialize next_due to current time + interval (or default 300 s)
                interval = plan.get("interval", 300)
                self.next_due[i] = time.time() + interval
            self.plan_details_label.setText(details)
        else:
            self.plan_details_label.setText("No measurement plans available.")

    def open_plan_window(self):
        self.plan_window = MeasurementPlanWindow()
        self.plan_window.show()
        self.plan_window.destroyed.connect(self.load_plans)

    def toggle_continuous(self):
        if not self.continuous_active:
            if not self.plans:
                QMessageBox.warning(self, "No Plans", "No measurement plans are available.")
                return
            self.continuous_active = True
            self.status_label.setText("Status: Measurement Running")
            self.start_stop_btn.setText("Stop")
            self.progress_timer.start()
            # Schedule the next measurement (choose the plan with the smallest next_due)
            self.schedule_next_measurement()
        else:
            self.continuous_active = False
            self.status_label.setText("Status: Idle")
            self.start_stop_btn.setText("Start")
            if self.global_timer.isActive():
                self.global_timer.stop()
            if self.poll_timer and self.poll_timer.isActive():
                self.poll_timer.stop()
            self.progress_timer.stop()
            self.progress_display.clear()

    def schedule_next_measurement(self):
        """Find the plan with the earliest next_due and schedule its measurement."""
        if not self.continuous_active:
            return
        now = time.time()
        next_plan_index = None
        min_due = float('inf')
        for idx, due in self.next_due.items():
            if due < min_due:
                min_due = due
                next_plan_index = idx
        if next_plan_index is None:
            return
        delay = max(0, min_due - now)
        self.status_label.setText(f"Status: Next measurement in {delay:.1f}s")
        # Set up the global timer to wait until the next plan is due.
        self.global_timer = QTimer(self)
        self.global_timer.setSingleShot(True)
        self.global_timer.timeout.connect(lambda: self.run_scheduled_measurement(next_plan_index))
        self.global_timer.start(int(delay * 1000))

    def run_scheduled_measurement(self, plan_index):
        """When the global timer fires, run measurement for the selected plan."""
        if not self.continuous_active:
            return
        self.current_plan_index = plan_index
        current_plan = self.plans[plan_index]
        print(f"Starting measurement for plan {current_plan.get('plan_name')}")
        # Overwrite the global interrupt file with the messages for this plan.
        estimated_duration, _ = schedule_measurement(current_plan)
        if estimated_duration is None:
            # Retry after a short delay if needed.
            QTimer.singleShot(1000, lambda: self.run_scheduled_measurement(plan_index))
            return
        # Compute wait_duration as estimated_duration * 1.5.
        wait_duration = estimated_duration * 1.1
        self.current_start_time = time.time()
        self.current_wait_duration = wait_duration
        # Use updated audio folder.
        audio_folder = "/home/plense/plensor_data/audio_data/time_domain_not_processed"
        if not os.path.exists(audio_folder):
            os.makedirs(audio_folder)
        self.current_existing_files = set(os.listdir(audio_folder))
        # Start a poll timer to check for a new FLAC file.
        self.poll_timer = QTimer(self)
        self.poll_timer.setInterval(500)
        self.poll_timer.timeout.connect(lambda: self.poll_measurement(current_plan, plan_index, audio_folder, wait_duration))
        self.poll_timer.start()

    def poll_measurement(self, plan, plan_index, audio_folder, wait_duration):
        result = process_measurement(plan, self.current_start_time, wait_duration, audio_folder, self.current_existing_files)
        if result and result[0][0] is not None:  # Check if valid file was found
            # Measurement completed successfully
            self.poll_timer.stop()
            source_path, creation_time = result[0]
            print(f"Plan {plan.get('plan_name')} measured file at {source_path} at t={creation_time:.2f}s")
            # Update next_due for this plan (add its interval to the previous scheduled time)
            interval = plan.get("interval", 300)
            self.next_due[plan_index] += interval
            self.schedule_next_measurement()
        else:
            elapsed = time.time() - self.current_start_time
            if elapsed >= wait_duration:
                # Timeout: measurement did not complete in expected time
                self.poll_timer.stop()
                print(f"Plan {plan.get('plan_name')} measurement timeout after {elapsed:.2f}s")
                interval = plan.get("interval", 300)
                self.next_due[plan_index] += interval
                self.schedule_next_measurement()

    def update_progress(self):
        """Update the progress display showing time until next measurement."""
        if not self.next_due:
            self.progress_display.setPlainText("No measurement scheduled.")
            return
        now = time.time()
        next_due_time = min(self.next_due.values())
        remaining = max(0, next_due_time - now)
        self.progress_display.setPlainText(f"Time until next measurement: {remaining:.1f}s")

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = ContinuousMeasurementWindow()
    window.show()
    sys.exit(app.exec())
