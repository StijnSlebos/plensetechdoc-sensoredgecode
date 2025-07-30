import json
import os


class QueueManager:
    def __init__(self, logger, sensor_objects, queue, measure_process_manager):
        self.logger = logger
        self.sensors = sensor_objects
        self.measurement_queue = queue
        self.metadata_directory = '/home/plense/metadata'
        self.json_file_path = os.path.join(self.metadata_directory, 'measure_settings.json')
        self.measure_process_manager = measure_process_manager

    def initialize_get_byte_queue(self) -> None:
        """
        Initializes the measurement queue with at least N measurement messages,
        where N is the number of connected sensors.
        """
        try:
            for sensor in self.sensors:
                get_byte_msg = sensor.create_message(message_type='get_byte', calibrate_after=False)
                self.measurement_queue.put(get_byte_msg)
            self.logger.log_error(f"Measurement queue initialized with {self.measurement_queue}.")
            queue_contents = list(self.measurement_queue.queue)
            self.logger.log_error("Queue contents:")
            for message in queue_contents:
                self.logger.log_error(message)
        except Exception as e:
            self.logger.log_error(f"Error initializing measurement queue: {e}")

    def initialize_calibrate_queue(self) -> None:
        """
        Initializes the measurement queue with at least N measurement messages,
        where N is the number of connected sensors.
        """
        try:
            for sensor in self.sensors:
                calibrate_msg = sensor.create_message(message_type='calibrate', measure_after=False)
                self.measurement_queue.put(calibrate_msg)
            self.logger.log_error(f"Measurement queue initialized with {self.measurement_queue}.")
            queue_contents = list(self.measurement_queue.queue)
            self.logger.log_error("Queue contents:")
            for message in queue_contents:
                self.logger.log_error(message)
        except Exception as e:
            self.logger.log_error(f"Error initializing measurement queue: {e}")

    def initialize_measurement_queue(self) -> None:
        """
        Initializes the measurement queue based on the JSON-defined sequence and settings.
        """
        try:
            with open(self.json_file_path, 'r') as f:
                # Get measurement settings from the metadata file
                config = json.load(f)
                measurement_settings = config.get("measurement_settings", {})
                measurement_sequence = config.get("measurement_sequence", [])
                default_measurement_sequence = config.get("default_measurement_sequence", [])
                sensor_specific_settings = config.get("sensor_specific_settings", {})
                default_sensors = config.get("default_sensors", [])

            # Add measurements for sensors listed in default_sensors
            responsive_sensors = self.measure_process_manager.get_responsive_sensors()

            for sensor in responsive_sensors:
                for measurement_type in default_measurement_sequence:
                    settings = measurement_settings.get(measurement_type, {})
                    combined_settings = {**settings}

                    if combined_settings:
                        measurement_message = {
                            "sensor_id": sensor.sensor_id,
                            "measurement_settings": {
                                "type": "measure",
                                **combined_settings
                            }
                        }
                        self.measurement_queue.put(measurement_message)

            # Placeholder for Plensor specific measurement settings
            self.logger.log_error(f"Measurement queue initialized with {self.measurement_queue}.")
            queue_contents = list(self.measurement_queue.queue)
            self.logger.log_error("Queue contents:")
            for message in queue_contents:
                self.logger.log_error(message)
        except Exception as e:
            self.logger.log_error(f"Error initializing measurement queue: {e}")
            # If there is an error in initializing, initialize with
            # default messages for the sensors
            for sensor in self.sensors:
                measurement_message = {
                    "sensor_id": sensor.sensor_id,
                    "measurement_settings": {
                        "type": "measure",
                        "command": "BLOCK",
                        "duration": 50000,
                        "start_frequency": 20000,
                        "stop_frequency": 100000,
                        "repetitions": 10
                    }
                }
                self.measurement_queue.put(measurement_message)
                measurement_message = {
                    "sensor_id": sensor.sensor_id,
                    "measurement_settings": {
                        "type": "measure",
                        "command": "ENV"
                    }
                }
                self.measurement_queue.put(measurement_message)
