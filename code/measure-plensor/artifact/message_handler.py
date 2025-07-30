import os
import numpy as np
import soundfile as sf
import time
from datetime import datetime


class MessageHandler:
    def __init__(self, logger, json_handler, sensors, queue, measurement_dir, measurement_process_handler):
        self.sensors = sensors
        self.logger = logger
        self.json_handler = json_handler
        self.measurement_queue = queue
        self.env_dir = measurement_dir + '/environment_data'
        self.audio_dir = measurement_dir + '/audio_data/time_domain_not_processed'
        self.tof_dir = measurement_dir + '/audio_data/tof'
        self.measurement_process_handler = measurement_process_handler

    def handle_get_byte_msg(self, sensor_id, get_byte_msg) -> None:
        """
        Invokes the get_sensor_id() method on the specified Sensor instance.
        If the get_byte_for_sensor finishes successfully, it places a
        calibrate message at the front of the queue.
        If it fails, a placeholder for exception handling is added.
        """
        self.logger.log_error(f"[{sensor_id}]: handling get byte message")
        success = True  # Placeholder for actual get byte result

        sensor = next(
            (s for s in self.sensors if s.sensor_id == sensor_id), None)
        if sensor:
            try:
                success = sensor.get_sensor_id()
                self.logger.log_error(f"[{sensor_id}]: Get byte succes: {success}")
            except Exception as e:
                self.logger.log_error(f"[{sensor_id}]: Get byte failed for sensor: {e}")
                success = False

            if success and get_byte_msg["measurement_settings"]["calibrate_after"]:
                self.logger.log_error(f"[{sensor_id}]: Successful fault detection get bye, placing calibrate msg at front of queue")
                # Place a calibrate message for the sensor at the front of the queue
                self.measurement_queue.queue.appendleft(
                    sensor.create_message(
                        message_type='calibrate', measure_after=True))
                self.measurement_process_handler.mark_sensor_responsive(sensor_id)
            elif success:
                self.logger.log_error(f"[{sensor_id}]: Successfully get byte to Plensor {sensor_id}")
                self.measurement_process_handler.mark_sensor_responsive(sensor_id)
            elif not success and get_byte_msg["measurement_settings"]["calibrate_after"]:
                # Placeholder for exception handling logic when get_byte_for_sensor fails
                self.logger.log_error(f"[{sensor_id}]: Get byte failed, marking as unresponsive.")
                self.measurement_process_handler.mark_sensor_unresponsive(sensor_id)

    def handle_reset_msg(self, sensor_id, reset_msg) -> None:
        """
        Invokes the reset_plensor() method on the specified Sensor instance.
        If the reset_plensor finishes successfully, it places a
        calibrate message at the front of the queue.
        If it fails, a placeholder for exception handling is added.
        """
        self.logger.log_error(f"[{sensor_id}]: handling reset message")
        success = True  # Placeholder for actual reset result

        sensor = next(
            (s for s in self.sensors if s.sensor_id == sensor_id), None)
        if sensor:
            try:
                success = sensor.reset_plensor()
                self.logger.log_error(f"[{sensor_id}]: Reset succes: {success}")
            except Exception as e:
                self.logger.log_error(f"[{sensor_id}]: Reset failed for sensor: {e}")
                success = False

            if success and reset_msg["measurement_settings"]["get_byte_after"]:
                self.logger.log_error(f"[{sensor_id}]: Successful reset, placing get byte msg at front of queue")
                # Place a calibrate message for the sensor at the front of the queue
                self.measurement_queue.queue.appendleft(
                    sensor.create_message(
                        message_type='get_byte', calibrate_after=True))
                self.measurement_process_handler.mark_sensor_responsive(sensor_id)
            elif success:
                self.logger.log_error(f"[{sensor_id}]: Successfully reset byte to Plensor {sensor_id}")
                self.measurement_process_handler.mark_sensor_responsive(sensor_id)
            elif not success:
                # Placeholder for exception handling logic when get_byte_for_sensor fails
                self.logger.log_error(f"[{sensor_id}]: Reset failed, marking as unresponsive.")
                self.measurement_process_handler.mark_sensor_unresponsive(sensor_id)

    def handle_calibrate_msg(self, sensor_id, calibrate_msg) -> None:
        """
        Placeholder for calibration logic on the specified Sensor instance.
        If the calibrate_sensor finishes successfully, it places a measurement message at the end of the queue.
        If it fails, a placeholder for exception handling logic is added.
        """
        self.logger.log_error(f"[{sensor_id}]: handling calibration message")

        calibration_result = True  # Placeholder for actual calibration result

        sensor = next((s for s in self.sensors if s.sensor_id == sensor_id), None)
        if sensor:
            try:
                calibration_result = sensor.calibrate_plensor()
            except Exception as e:
                self.logger.log_error(f"[{sensor_id}]: Calibration failed: {e}")
                calibration_result = False

            if calibration_result:
                self.logger.log_error(f"[{sensor_id}]: Calibration succeeded!")
                self.measurement_process_handler.mark_sensor_responsive(sensor_id)

                if calibrate_msg["measurement_settings"]["measure_after"]:
                    test_measurement_msg = {
                        "sensor_id": sensor_id,
                        "measurement_settings": {
                            "type": "measure",
                            "test_measure": True,
                            "command": "BLOCK",
                            "duration": 50000,
                            "start_frequency": 20000,
                            "stop_frequency": 100000,
                            "repetitions": 2}}
                    self.measurement_queue.queue.appendleft(test_measurement_msg)

            else:
                # Placeholder for exception handling logic when calibrate_sensor fails
                self.logger.log_error(f"[{sensor_id}]: Calibration failed, marking as unresponsive.")
                self.measurement_process_handler.mark_sensor_unresponsive(sensor_id)
                return calibration_result

    def handle_measure_msg(self, sensor_id, measure_msg) -> None:
        """
        Invokes the measure() method on the specified Sensor instance.
        If the measurement fails, a get_byte message is placed at the beginning of the queue.
        If it succeeds, a measure message is placed at the end of the queue.
        """
        try:
            self.logger.log_error(f"[{sensor_id}]: handling measure message: {measure_msg}")
            sensor = next((s for s in self.sensors if s.sensor_id == sensor_id), None)
            is_test_measure = measure_msg.get("measurement_settings", {}).get("test_measure", False)

            if sensor:
                if measure_msg['measurement_settings']['command'] in ["BLOCK", "SINE"]:
                    self.handle_block_sine_msg(sensor, measure_msg, is_test_measure)
                elif measure_msg['measurement_settings']['command'] == 'ENV':
                    self.handle_env_msg(sensor, measure_msg)
                elif measure_msg['measurement_settings']['command'] == 'TOF':
                    self.handle_tof_msg(sensor, measure_msg)
                elif measure_msg['measurement_settings']['command'] == 'TOF_BLOCK':
                    self.handle_tof_block_msg(sensor, measure_msg)
        except Exception as e:
            self.logger.log_error(f" Error while handling measure msg: {e}")

    def create_identifier(self, measure_msg, sensor) -> str:
        start_frequency_identifier = f"{str(int(measure_msg['measurement_settings']['start_frequency']/10)).zfill(5)}"
        command_identifier = f"{measure_msg['measurement_settings']['command'][0]}"
        stop_frequency_identifier = f"{str(int(measure_msg['measurement_settings']['stop_frequency']/10)).zfill(5)}"

        print(f"Creating damping level identifier")
        damping_level = measure_msg['measurement_settings'].get('damping_level', None)
        if damping_level:
            damping_level_identifier = f"l{str(damping_level).zfill(3)}"
        else:
            damping_level = sensor.damping_level_base
            damping_level_identifier = f"l{str(damping_level).zfill(3)}"
        print("Damping level identified")
        duration_identifier = f"d{str(int(measure_msg['measurement_settings']['duration']/1000)).zfill(2)}"
        repetitions_identifier = f"r{str(measure_msg['measurement_settings']['repetitions']).zfill(3)}"

        identifier = f"{start_frequency_identifier}{command_identifier}{stop_frequency_identifier}{damping_level_identifier}{duration_identifier}{repetitions_identifier}"
        return identifier

    def handle_block_sine_msg(self, sensor, measure_msg, test_meas=False) -> None:
        try:
            damping_level = measure_msg['measurement_settings'].get('damping_level', None)
            print(f"Setting the damping level to {damping_level}")
            damping_success = sensor.set_damping_byte(damping_level)

            if damping_success:
                measurement = sensor.measure_block_or_sine(measure_msg['measurement_settings'])
                if measurement is not None:
                    # Save the audio measurement
                    record_timestamp = f"{datetime.now().strftime('%Y-%m-%d')}T{datetime.now().strftime('%H%M%S')}"
                    identifier = f"{measure_msg['measurement_settings']['command'][0]}"
                    print(f"Creating identifier for the filename")
                    filename = (
                        f"{self.create_identifier(measure_msg, sensor)}"
                        f"#{str(sensor.sensor_id).zfill(5)}_{record_timestamp}.flac"
                    )
                    if not test_meas:
                        sf.write(
                            os.path.join(self.audio_dir, filename),
                            np.int16(measurement),
                            samplerate=500000)

                    # And add the measurement message at the end of the queue   
                    # self.measurement_queue.put(measure_msg)

                # If measurement failed, add a get_byte message to the front of the queue
                # which also includes the original measure message
                else:
                    get_byte_msg = sensor.create_message(message_type="get_byte", calibrate_after=True)
                    self.measurement_queue.queue.appendleft(get_byte_msg)

        except Exception as e:
            self.logger.log_error(
                f"BLOCK or SINE measurement failed for sensor {sensor.sensor_id}: {e}")

    def handle_env_msg(self, sensor, measure_msg) -> None:
        try:
            measurement = sensor.measure_env()
            if measurement is not None:
                # Save the env measurement
                record_timestamp = f"{datetime.now().strftime('%Y-%m-%d')}T{datetime.now().strftime('%H%M%S')}"
                filename = (
                    f"ENV#{str(sensor.sensor_id).zfill(5)}_{record_timestamp}.json"
                )
                self.json_handler.save_to_json(
                    measurement,
                    os.path.join(self.env_dir, filename)
                )

                # And add the measurement message at the end of the queue
                # self.measurement_queue.put(measure_msg)

            # If measurement failed, add a get_byte message to the queue front
            # which also includes the original measure message
            else:
                self.logger.log_error(f"[{sensor.sensor_id}]: No env measurement success")
                get_byte_msg = sensor.create_message(message_type="get_byte", calibrate_after=True)
                get_byte_msg["original_measure_msg"] = measure_msg
                self.measurement_queue.queue.appendleft(get_byte_msg)
        except Exception as e:
            self.logger.log_error(
                f"ENV measurement failed for sensor {sensor.sensor_id}: {e}")

    def handle_tof_msg(self, sensor, measure_msg) -> None:
        try:
            damping_level = measure_msg['measurement_settings'].get('damping_level', None)
            print(f"Setting the damping level to {damping_level}")
            damping_success = sensor.set_damping_byte(damping_level)

            if damping_success:
                measurement = sensor.measure_tof_impulse(measure_msg['measurement_settings'])
                if measurement is not None:
                    # Save the env measurement
                    record_timestamp = f"{datetime.now().strftime('%Y-%m-%d')}T{datetime.now().strftime('%H%M%S')}"
                    filename = (
                        f"TOF#{str(sensor.sensor_id).zfill(5)}_{record_timestamp}.json"
                    )
                    self.json_handler.save_to_json(
                        measurement,
                        os.path.join(self.tof_dir, filename)
                    )
        except Exception as e:
            self.logger.log_error(
                f"TOF measurement failed for sensor {sensor.sensor_id}: {e}")
    
    def handle_tof_block_msg(self, sensor, measure_msg) -> None:
        try:
            damping_level = measure_msg['measurement_settings'].get('damping_level', None)
            print(f"Setting the damping level to {damping_level}")
            damping_success = sensor.set_damping_byte(damping_level)

            if damping_success:
                measurement = sensor.measure_tof_block(measure_msg['measurement_settings'])
                if measurement is not None:
                    # Save the env measurement
                    record_timestamp = f"{datetime.now().strftime('%Y-%m-%d')}T{datetime.now().strftime('%H%M%S')}"
                    # Get settings for filename
                    half_periods = str(measure_msg['measurement_settings']['tof_half_periods']).zfill(3)
                    repetitions = str(measure_msg['measurement_settings']['repetitions']).zfill(3)
                    damping_level = str(measure_msg['measurement_settings'].get('damping_level', 0)).zfill(3)
                    
                    filename = (
                        f"TOF_BLOCKh{half_periods}r{repetitions}l{damping_level}#"
                        f"{str(sensor.sensor_id).zfill(5)}_{record_timestamp}.json"
                    )
                    self.json_handler.save_to_json(
                        measurement,
                        os.path.join(self.tof_dir, filename)
                    )
        except Exception as e:
            self.logger.log_error(
                f"TOF Block measurement failed for sensor {sensor.sensor_id}: {e}")
