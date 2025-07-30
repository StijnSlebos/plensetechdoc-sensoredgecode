import os
import json
import time
import shutil
import numpy as np
import soundfile as sf

def current_date_str():
    return time.strftime("%Y%m%d")

def load_settings():
    SETTINGS_FILE = os.path.join("Interface-guis", "json_files", "measurement_config.json")
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {}

def schedule_measurement(plan):
    """
    For the given plan, create (or overwrite) a measurement interrupt file named
    "message_interrupt.json" in /home/plense/metadata.
    
    Returns the estimated duration (in seconds) and the interrupt file path.
    """
    metadata_dir = "/home/plense/metadata"
    if not os.path.exists(metadata_dir):
        os.makedirs(metadata_dir)
    interrupt_path = os.path.join(metadata_dir, "message_interrupt.json")
    sensor_ids = plan.get("sensors", [])
    sequence = plan.get("measurement_sequence", [])
    measurement_settings = plan.get("measurement_settings", {})
    messages = []
    for sensor in sensor_ids:
        for cmd in sequence:
            settings = measurement_settings.get(cmd, {}).copy()
            # For BLOCK and SINE commands, remove any "damping_byte" key.
            if cmd in ["BLOCK", "SINE"]:
                settings.pop("damping_byte", None)
            # Build the message (do not include plan name here)
            msg = {"sensor_id": int(str(sensor).lstrip('#')), "measurement_settings": {"type": "measure"}}
            if "damping" in settings:
                settings["command"] = settings.pop("damping")
            msg["measurement_settings"].update(settings)
            messages.append(msg)
    with open(interrupt_path, "w") as f:
        json.dump(messages, f, indent=4)
    print("Global message interrupt created at", interrupt_path)
    # Estimate measurement duration.
    est_times = []
    for cmd in sequence:
        cmd_settings = measurement_settings.get(cmd, {})
        if cmd in ["BLOCK", "SINE"]:
            duration = cmd_settings.get("duration", 0) / 1e6  # seconds
            repetitions = cmd_settings.get("repetitions", 1)
            est_time = duration * repetitions * 10 * 1.5
            est_times.append(est_time)
        else:
            est_times.append(1.0)
    # Calculate total duration accounting for all sensors
    per_sensor_duration = max(est_times) if est_times else 1.0
    num_sensors = len(sensor_ids)
    estimated_duration = per_sensor_duration * num_sensors
    print(f"Estimated measurement duration: {estimated_duration:.2f} seconds.")
    return estimated_duration, interrupt_path

def process_measurement(plan, start_time, wait_duration, audio_folder, existing_files):
    """
    Waits for the specified duration, then detects new FLAC files created after start_time.
    
    Args:
        plan (dict): Measurement plan containing output path information
        start_time (float): Unix timestamp when measurement started
        wait_duration (float): Time to wait in seconds
        audio_folder (str): Path to folder containing recorded audio files
        existing_files (set): Set of files that existed before measurement started

    Returns:
        list: List of tuples (source_path, file_creation_time) for each new FLAC file
    """
    print(f"Starting process_measurement with wait_duration: {wait_duration}")
    print(f"Existing files before wait: {existing_files}")
    
    # Wait for the measurement to complete
    time.sleep(wait_duration)
    
    current_files = set(os.listdir(audio_folder))
    new_files = current_files - existing_files
    print(f"Files after wait: {current_files}")
    print(f"New files detected: {new_files}")
    
    results = []
    
    # Detect each new FLAC file
    for file in new_files:
        if not file.lower().endswith('.flac'):
            continue
            
        source_path = os.path.join(audio_folder, file)
        file_creation_time = os.path.getctime(source_path)
        
        # Skip files created before measurement start
        if file_creation_time < start_time:
            continue
            
        results.append((source_path, file_creation_time))
    
    return results if results else [(None, 0.0)]
