import json
import os
import sys
import time
import traceback


LOCAL_FILE_PATH = r"Interface-guis\handheld_interface\complex_interrupt.py"
# MEASURING_DEVICE_ID = 122
# JSON_FILE_PATH = "/home/plense/metadata/message_interrupt.json"

class ComplexInterrupt:
    def __init__(self, config_file_path = os.path.join(os.path.dirname(LOCAL_FILE_PATH), "app_config.json")):
        with open(config_file_path, "r") as f:
            self.config = json.load(f)
        self.measuring_device_id = self.config["MEASURING_DEVICE_ID"]
        self.interrupt_file_path = self.config["INTERRUPT_FILE_PATH"]
        
        # TODO: Remove this
        self.interrupt_file_path = r"C:\Users\StijnSlebos\Documents\Plense Tech\Database\dt1\plensor_sota_iteration-2_m4-y25"
        self.iterrupt_file_name = "message_interrupt.json"
        self.interrupt_file_path = os.path.join(self.interrupt_file_path, self.iterrupt_file_name)

    def get_meas_settings(self, command = "SINE", duration = 50000, start_freq = 1000, stop_freq = 10000, damping_level = 0, repetitions = 1):
        """
    Get the measurement settings for the complex interrupt test.
    """
        return {
            "type": "measure",
            "command": command,
            "duration": duration,
            "start_frequency": start_freq,
            "stop_frequency": stop_freq,
            "damping_level": damping_level,
            "repetitions": repetitions
        }

    def get_TOF_measurement_settings(self, timeout_us = 1000, repetitions = 1, tof_half_periods = 10, damping_level = 0):
        """
        Get the measurement settings for the TOF measurement.

        """
        if timeout_us > 1000:
            timeout_us = 1000
            print("Timeout set to 1000 us")

        return {
            "type": "measure",
            "command": "TOF_BLOCK",
            "timeout_duration": timeout_us,
            "tof_half_periods": tof_half_periods,
            "repetitions": repetitions,
            "damping_level": damping_level
        }
    
    
    def get_single_frequency_runs(self, start_freq = 20000, stop_freq = 100000, step_freq = 1000, repetitions = 1, number_of_wavelengths = 200, damping_level = 0, command = "SINE") -> list[dict]:
        """
        Get the single frequency runs.
        """

        runs = []

        for f in range(start_freq, stop_freq, step_freq):
            duration_us = int(1000000/f * number_of_wavelengths)
            message = self.get_meas_settings(command = command, duration = duration_us, start_freq = f, stop_freq = f, damping_level = damping_level, repetitions = repetitions)
            runs.append({"sensor_id": self.measuring_device_id, "measurement_settings": message})

        return runs

    def get_linear_sweep_runs(self, start_freq = 20000, stop_freq = 100000, sweep_freq = 10000, repetitions = 1, duration_us = 50000, damping_level = 0, command = "SINE") -> list[dict]:
        """
        Get the linear sweep runs.
        """

        runs = []

        for f in range(start_freq, stop_freq, sweep_freq):
            message = self.get_meas_settings(command = command, duration = duration_us, start_freq = f, stop_freq = f+sweep_freq, damping_level = damping_level, repetitions = repetitions)
            runs.append({"sensor_id": self.measuring_device_id, "measurement_settings": message})

        return runs

    def get_damping_runs(self, frequency = 20000, repetitions = 1, duration_us = 50000, damping_level_start = 0, damping_level_stop = 100, damping_level_step = 10, command = "SINE") -> list[dict]:
        """
        Get the damping runs.
        """

        runs = []
        for d in range(damping_level_start, damping_level_stop, damping_level_step):
            message = self.get_meas_settings(command = command, duration = duration_us, start_freq = frequency, stop_freq = frequency, damping_level = d, repetitions = repetitions)
            runs.append({"sensor_id": self.measuring_device_id, "measurement_settings": message})

        return runs

    def get_TOF_runs(self, timeout_us = 1000, repetitions = 5, tof_half_periods_start = 1, tof_half_periods_stop = 15, tof_half_periods_step = 1, damping_level = 0):
        """
        Get the TOF runs.
        """

        runs = []
        for t in range(tof_half_periods_start, tof_half_periods_stop, tof_half_periods_step):
            message = self.get_TOF_measurement_settings(timeout_us = timeout_us, repetitions = repetitions, tof_half_periods = t, damping_level = damping_level)
            runs.append({"sensor_id": self.measuring_device_id, "measurement_settings": message})

        return runs
    
    def build_run(self, measurements : dict):
        self.runs = []

        for measurement in measurements["sensor_measurements"]:
            measurement_type = measurement["measurement_type"] 
            measurement_config = measurement["measurement_configuation"]
            self.runs.extend(self.get_runs(measurement_type = measurement_type, measurement_config = measurement_config))

            # if measurement_type == "POINT_SWEEP":
            #     self.runs.extend(self.get_single_frequency_runs(start_freq = measurement_config["start_frequency"], stop_freq = measurement_config["stop_frequency"], step_freq = measurement_config["step_frequency"], repetitions = measurement_config["repetitions"], number_of_wavelengths = measurement_config["number_of_wavelengths"], damping_level = measurement_config["damping_level"], command = measurement_config["command"]))
            # elif measurement_type == "SEGMENT_SWEEP":
            #     self.runs.extend(self.get_linear_sweep_runs(start_freq = measurement_config["start_frequency"], stop_freq = measurement_config["stop_frequency"], sweep_freq = measurement_config["sweep_frequency"], repetitions = measurement_config["repetitions"], duration_us = measurement_config["duration_us"], damping_level = measurement_config["damping_level"], command = measurement_config["command"]))
            # elif measurement_type == "SINGLE_SWEEP":
            #     self.runs.extend(self.get_linear_sweep_runs(start_freq = measurement_config["start_frequency"], stop_freq = measurement_config["stop_frequency"], sweep_freq = measurement_config["stop_frequency"] - measurement_config["start_frequency"], repetitions = measurement_config["repetitions"], duration_us = measurement_config["duration_us"], damping_level = measurement_config["damping_level"], command = measurement_config["command"]))
            # elif measurement_type == "DAMPING_SWEEP":
            #     self.runs.extend(self.get_damping_runs(frequency = measurement_config["frequency"], repetitions = measurement_config["repetitions"], duration_us = measurement_config["duration_us"], damping_level_start = measurement_config["damping_level_start"], damping_level_stop = measurement_config["damping_level_stop"], damping_level_step = measurement_config["damping_level_step"], command = measurement_config["command"]))
            # elif measurement_type == "TOF_SWEEP":
            #     self.runs.extend(self.get_TOF_runs(timeout_us = measurement_config["timeout_us"], repetitions = measurement_config["repetitions"], tof_half_periods_start = measurement_config["tof_half_periods_start"], tof_half_periods_stop = measurement_config["tof_half_periods_stop"], tof_half_periods_step = measurement_config["tof_half_periods_step"], damping_level = measurement_config["damping_level"]))

    def get_runs(self, measurement_type, measurement_config):
        single_runs = []
        if measurement_type == "POINT_SWEEP":
            single_runs = self.get_single_frequency_runs(start_freq = measurement_config["start_frequency"], stop_freq = measurement_config["stop_frequency"], step_freq = measurement_config["step_frequency"], repetitions = measurement_config["repetitions"], number_of_wavelengths = measurement_config["number_of_wavelengths"], damping_level = measurement_config["damping_level"], command = measurement_config["command"])
        elif measurement_type == "SEGMENT_SWEEP":
            single_runs = self.get_linear_sweep_runs(start_freq = measurement_config["start_frequency"], stop_freq = measurement_config["stop_frequency"], sweep_freq = measurement_config["sweep_frequency"], repetitions = measurement_config["repetitions"], duration_us = measurement_config["duration_us"], damping_level = measurement_config["damping_level"], command = measurement_config["command"])
        elif measurement_type == "SINGLE_SWEEP":
            single_runs = self.get_linear_sweep_runs(start_freq = measurement_config["start_frequency"], stop_freq = measurement_config["stop_frequency"], sweep_freq = measurement_config["stop_frequency"] - measurement_config["start_frequency"], repetitions = measurement_config["repetitions"], duration_us = measurement_config["duration_us"], damping_level = measurement_config["damping_level"], command = measurement_config["command"])
        elif measurement_type == "DAMPING_SWEEP":
            single_runs = self.get_damping_runs(frequency = measurement_config["frequency"], repetitions = measurement_config["repetitions"], duration_us = measurement_config["duration_us"], damping_level_start = measurement_config["damping_level_start"], damping_level_stop = measurement_config["damping_level_stop"], damping_level_step = measurement_config["damping_level_step"], command = measurement_config["command"])
        elif measurement_type == "TOF_SWEEP":
            single_runs = self.get_TOF_runs(timeout_us = measurement_config["timeout_us"], repetitions = measurement_config["repetitions"], tof_half_periods_start = measurement_config["tof_half_periods_start"], tof_half_periods_stop = measurement_config["tof_half_periods_stop"], tof_half_periods_step = measurement_config["tof_half_periods_step"], damping_level = measurement_config["damping_level"])

        return single_runs
    
    
    def run_measurement(self):
        with open(self.interrupt_file_path, "w") as f:
            json.dump(self.runs, f, indent=4)
        
        return self.runs


if __name__ == "__main__":
    # runs = []
    #runs.extend(get_single_frequency_runs(start_freq = 20000, stop_freq = 100000, step_freq = 1000, repetitions = 1, number_of_wavelengths = 200, damping_level = 0, command = "SINE"))
    #runs.extend(get_linear_sweep_runs(start_freq = 20000, stop_freq = 100000, sweep_freq = 10000, repetitions = 1, duration_us = 50000, damping_level = 0, command = "SINE"))
    #runs.extend(get_damping_runs(frequency = 20000, repetitions = 1, duration_us = 10000, damping_level_start = 0, damping_level_stop = 100, damping_level_step = 10, command = "SINE"))
    # runs.extend(get_TOF_runs(timeout_us = 1000, repetitions = 5, tof_half_periods_start = 1, tof_half_periods_stop = 15, tof_half_periods_step = 1, damping_level = 0))
    
    # with open(JSON_FILE_PATH, "w") as f:
    #     json.dump(runs, f)

    ci = ComplexInterrupt()
    with open(os.path.join(os.path.dirname(LOCAL_FILE_PATH), "measurement_template.json"), "r") as f:
        measurements = json.load(f)
    ci.build_run(measurements = measurements)

    ci.run_measurement()












