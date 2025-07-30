import time
import json
import os
from datetime import datetime

LOCAL_FILE_PATH = r"Interface-guis\handheld_interface"
APP_CONFIG_FILE_PATH = os.path.join(LOCAL_FILE_PATH, "app_config.json")
MEASUREMENT_CONFIG_FILE_PATH = os.path.join(LOCAL_FILE_PATH, "measurement_config.json")
MEASUREMENT_TEMPLATE_FILE_PATH = os.path.join(LOCAL_FILE_PATH, "measurement_template.json")

from complex_interrupt import ComplexInterrupt


class MeasureHandler:
    def __init__(self, app_config_file_path = APP_CONFIG_FILE_PATH, measurement_config_file_path = MEASUREMENT_CONFIG_FILE_PATH, measurement_template_file_path = MEASUREMENT_TEMPLATE_FILE_PATH):
        with open(app_config_file_path, "r") as f:
            self.app_config = json.load(f)

        self.measuring_device_id = self.app_config["MEASURING_DEVICE_ID"]
        self.interrupt_file_path = self.app_config["INTERRUPT_FILE_PATH"]
        self.audio_files_not_processed_path = self.app_config["AUDIO_FILES_NOT_PROCESSED_PATH"]
        self.tof_files_not_processed_path = self.app_config["TOF_FILES_NOT_PROCESSED_PATH"]

        with open(measurement_config_file_path, "r") as f:
            self.measurement_config = json.load(f)

        with open(measurement_template_file_path, "r") as f:
            self.measurement_template = json.load(f)

        self.complex_interrupt = ComplexInterrupt(APP_CONFIG_FILE_PATH)


    def load_measurement_config(self):
        with open(MEASUREMENT_CONFIG_FILE_PATH, "r") as f:
            self.measurement_config = json.load(f)


    def run_measurement(self):
        measurements = self.measurement_config["sensor_measurements"]
        self.complex_interrupt.build_run(measurements)
        self.complex_interrupt.run_measurement()



        self.expected_files = self.expected_files_per_measurement(measurements)
        for key, value in self.expected_files.items():
            print(f"Expected files for {key}:")
            print(f"Audio files: {value[0]}")
            print(f"TOF files: {value[1]}")

    def expected_files_per_measurement(self, measurements) -> tuple[list[str], list[str]]:

        expected_files = {}

        for idx, measurement in enumerate(measurements):
            sequences = self.complex_interrupt.get_runs(measurement_type = measurement["measurement_type"], measurement_config = measurement["measurement_configuation"])
            expected_files[f"measure_{idx}"] = self.get_expected_files(sequences)

        return expected_files

    def get_expected_files(self, sequences):
        expected_audio_files = []
        expected_tof_files = []

        record_timestamp = f"{datetime.now().strftime('%Y-%m-%d')}T"


        for sequence in sequences:
            settings = sequence["measurement_settings"]
            sensor_id = sequence["sensor_id"]
            
            if settings["command"] == "SINE" or settings["command"] == "BLOCK":
                start_frequency_identifier = f"{str(int(settings['start_frequency']/10)).zfill(5)}"
                command_identifier = f"{settings['command'][0]}"
                stop_frequency_identifier = f"{str(int(settings['stop_frequency']/10)).zfill(5)}"
                
                damping_level_identifier = f"l{str(settings['damping_level']).zfill(3)}"
                duration_identifier = f"d{str(int(settings['duration']/1000)).zfill(2)}"
                repetitions_identifier = f"r{str(settings['repetitions']).zfill(3)}"

                identifier = f"{start_frequency_identifier}{command_identifier}{stop_frequency_identifier}{damping_level_identifier}{duration_identifier}{repetitions_identifier}"

                filename = (
                        f"{identifier}"
                        f"#{str(sensor_id).zfill(5)}_{record_timestamp}"
                    )
                
                expected_audio_files.append(filename)
            elif settings["command"] == "TOF_BLOCK":
                # Get settings for filename
                half_periods = str(settings['tof_half_periods']).zfill(3)
                repetitions = str(settings['repetitions']).zfill(3)
                damping_level = str(settings.get('damping_level', 0)).zfill(3)
                
                filename = (
                    f"TOF_BLOCKh{half_periods}r{repetitions}l{damping_level}#"
                    f"{str(sensor_id).zfill(5)}_{record_timestamp}"
                )

                expected_tof_files.append(filename)
        return expected_audio_files, expected_tof_files



    def save_measurement_data(self):

        pass


if __name__ == "__main__":
    measure_handler = MeasureHandler()
    measure_handler.run_measurement()
    measure_handler.save_measurement_data()



