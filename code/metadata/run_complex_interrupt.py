import json
import os
import sys
import time
import traceback

MEASURING_DEVICE_ID = 122
JSON_FILE_PATH = "/home/plense/metadata/message_interrupt.json"

def get_meas_settings(command = "SINE", duration = 50000, start_freq = 1000, stop_freq = 10000, damping_level = 0, repetitions = 1):
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

def get_TOF_measurement_settings(timeout_us = 1000, repetitions = 1, tof_half_periods = 10, damping_level = 0):
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

messages = []

# we want a few sorts of runs
# 1. single frequency runs
# 2. linear sweep runs
# 3. different damping levels

def iterate_single_frequency_runs(run_frequency = 20000, iterations = 100, number_of_wavelengths = 200, repetitions = 1, damping_level = 0, command = "SINE") -> list[dict]:
    """
    Iterate over the single frequency runs.
    """

    runs = []
    for i in range(iterations):
        duration_us = int(1000000/run_frequency * number_of_wavelengths)
        message = get_meas_settings(command = command, duration = duration_us, start_freq = run_frequency, stop_freq = run_frequency, damping_level = damping_level, repetitions = repetitions)
        runs.append({"sensor_id": MEASURING_DEVICE_ID, "measurement_settings": message})

    return runs


def get_single_frequency_runs(start_freq = 20000, stop_freq = 100000, step_freq = 1000, repetitions = 1, number_of_wavelengths = 200, damping_level = 0, command = "SINE") -> list[dict]:
    """
    Get the single frequency runs.
    """

    runs = []

    for f in range(start_freq, stop_freq, step_freq):
        duration_us = int(1000000/f * number_of_wavelengths)
        message = get_meas_settings(command = command, duration = duration_us, start_freq = f, stop_freq = f, damping_level = damping_level, repetitions = repetitions)
        runs.append({"sensor_id": MEASURING_DEVICE_ID, "measurement_settings": message})

    return runs

def get_linear_sweep_runs(start_freq = 20000, stop_freq = 100000, sweep_freq = 10000, repetitions = 1, duration_us = 50000, damping_level = 0, command = "SINE") -> list[dict]:
    """
    Get the linear sweep runs.
    """

    runs = []

    for f in range(start_freq, stop_freq, sweep_freq):
        message = get_meas_settings(command = command, duration = duration_us, start_freq = f, stop_freq = f+sweep_freq, damping_level = damping_level, repetitions = repetitions)
        runs.append({"sensor_id": MEASURING_DEVICE_ID, "measurement_settings": message})

    return runs

def get_damping_runs(frequency = 20000, repetitions = 1, duration_us = 50000, damping_level_start = 0, damping_level_stop = 100, damping_level_step = 10, command = "SINE") -> list[dict]:
    """
    Get the damping runs.
    """

    runs = []
    for d in range(damping_level_start, damping_level_stop, damping_level_step):
        message = get_meas_settings(command = command, duration = duration_us, start_freq = frequency, stop_freq = frequency, damping_level = d, repetitions = repetitions)
        runs.append({"sensor_id": MEASURING_DEVICE_ID, "measurement_settings": message})

    return runs

def get_TOF_runs(timeout_us = 1000, repetitions = 5, tof_half_periods_start = 1, tof_half_periods_stop = 15, tof_half_periods_step = 1, damping_level = 0):
    """
    Get the TOF runs.
    """

    runs = []
    for t in range(tof_half_periods_start, tof_half_periods_stop, tof_half_periods_step):
        message = get_TOF_measurement_settings(timeout_us = timeout_us, repetitions = repetitions, tof_half_periods = t, damping_level = damping_level)
        runs.append({"sensor_id": MEASURING_DEVICE_ID, "measurement_settings": message})

    return runs

if __name__ == "__main__":
    runs = []
    #runs.extend(get_single_frequency_runs(start_freq = 20000, stop_freq = 100000, step_freq = 1000, repetitions = 1, number_of_wavelengths = 200, damping_level = 0, command = "SINE"))
    #runs.extend(get_linear_sweep_runs(start_freq = 20000, stop_freq = 100000, sweep_freq = 10000, repetitions = 1, duration_us = 50000, damping_level = 0, command = "SINE"))
    #runs.extend(get_damping_runs(frequency = 20000, repetitions = 1, duration_us = 10000, damping_level_start = 0, damping_level_stop = 100, damping_level_step = 10, command = "SINE"))
    runs.extend(get_TOF_runs(timeout_us = 1000, repetitions = 5, tof_half_periods_start = 1, tof_half_periods_stop = 15, tof_half_periods_step = 1, damping_level = 0))
    runs.extend(iterate_single_frequency_runs(run_frequency = 20000, iterations = 100, number_of_wavelengths = 200, repetitions = 1, damping_level = 0, command = "SINE"))

    with open(JSON_FILE_PATH, "w") as f:
        json.dump(runs, f)












