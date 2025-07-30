import sys
import json
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTableWidget,
    QTableWidgetItem, QApplication, QMessageBox
)
from PyQt6.QtCore import Qt

# Import load_settings and save_settings from your settings module,
# and the SettingsWindow for editing an individual plan.
from settings_window import load_settings, save_settings, SettingsWindow

class MeasurementPlanWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Measurement Plan")
        self.setGeometry(100, 100, 800, 500)
        self.init_ui()
        self.refresh_table()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Measurement Plans Overview", self)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Table widget with 5 columns:
        # Plan Name, Sensors, Sequence, Damping Level, Output Path
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Plan Name", "Sensors", "Sequence", "Damping Level", "Output Path"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)
        
        # Buttons layout
        btn_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Add Plan")
        self.add_btn.setStyleSheet("font-size: 18px; padding: 10px;")
        self.add_btn.clicked.connect(self.add_plan)
        btn_layout.addWidget(self.add_btn)
        
        self.edit_btn = QPushButton("Edit Selected Plan")
        self.edit_btn.setStyleSheet("font-size: 18px; padding: 10px;")
        self.edit_btn.clicked.connect(self.edit_plan)
        btn_layout.addWidget(self.edit_btn)
        
        self.remove_btn = QPushButton("Remove Selected Plan")
        self.remove_btn.setStyleSheet("font-size: 18px; padding: 10px;")
        self.remove_btn.clicked.connect(self.remove_plan)
        btn_layout.addWidget(self.remove_btn)
        
        layout.addLayout(btn_layout)
        
        # Refresh button layout
        refresh_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Refresh", self)
        self.refresh_btn.setStyleSheet("font-size: 18px; padding: 10px;")
        self.refresh_btn.clicked.connect(self.refresh_table)
        refresh_layout.addWidget(self.refresh_btn)
        layout.addLayout(refresh_layout)
        
        self.setLayout(layout)
    
    def refresh_table(self):
        """Reload the measurement_plans from the JSON and populate the table."""
        settings = load_settings()
        plans = settings.get("measurement_plans", [])
        self.table.setRowCount(len(plans))
        for row, plan in enumerate(plans):
            # Plan Name
            name_item = QTableWidgetItem(plan.get("plan_name", "Unnamed Plan"))
            self.table.setItem(row, 0, name_item)
            # Sensors (comma separated)
            sensors = ", ".join(plan.get("sensors", []))
            self.table.setItem(row, 1, QTableWidgetItem(sensors))
            # Measurement Sequence
            sequence = ", ".join(plan.get("measurement_sequence", []))
            self.table.setItem(row, 2, QTableWidgetItem(sequence))
            # Damping Level (from BLOCK if available, otherwise from SINE)
            damping = ""
            ms = plan.get("measurement_settings", {})
            if "BLOCK" in ms:
                damping = str(ms["BLOCK"].get("damping_level", ""))
            elif "SINE" in ms:
                damping = str(ms["SINE"].get("damping_level", ""))
            self.table.setItem(row, 3, QTableWidgetItem(damping))
            # Output Path
            out_path = plan.get("output_path", "")
            self.table.setItem(row, 4, QTableWidgetItem(out_path))
        self.table.resizeColumnsToContents()

    def add_plan(self):
        """Add a new plan to the JSON configuration."""
        settings = load_settings()
        new_plan = {
            "plan_name": "New Plan",
            "interval": settings.get("measurement_interval", 300),
            "sensors": settings.get("sensors", []),
            "output_path": settings.get("metadata", {}).get("folder", ""),
            "measurement_settings": settings.get("measurement_settings", {}).copy(),
            "measurement_sequence": settings.get("default_measurement_sequence", [])
        }
        # Since the new structure does not include a DAMPING command, ensure that only BLOCK, SINE, and ENV remain.
        if "DAMPING" in new_plan["measurement_settings"]:
            del new_plan["measurement_settings"]["DAMPING"]
        if "measurement_plans" not in settings:
            settings["measurement_plans"] = []
        settings["measurement_plans"].append(new_plan)
        save_settings(settings)
        self.refresh_table()

    def edit_plan(self):
        """Open the SettingsWindow to edit the selected plan."""
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "No Selection", "Please select a plan to edit.")
            return
        self.plan_settings_window = SettingsWindow(plan_index=selected)
        self.plan_settings_window.show()
        # Refresh the table when the settings window is closed.
        self.plan_settings_window.destroyed.connect(self.refresh_table)

    def remove_plan(self):
        """Remove the selected plan from the JSON configuration."""
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "No Selection", "Please select a plan to remove.")
            return
        settings = load_settings()
        plans = settings.get("measurement_plans", [])
        if 0 <= selected < len(plans):
            del plans[selected]
            settings["measurement_plans"] = plans
            save_settings(settings)
            self.refresh_table()
        else:
            QMessageBox.warning(self, "Invalid Selection", "Selected plan index is out of range.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MeasurementPlanWindow()
    window.show()
    sys.exit(app.exec())
