import json
import os
import serial
from calibrate_sensor_mixin import CalibrateSensorMixin
from error_logger import ErrorLogger
from get_sensor_id_mixin import GetSensorIDMixin
from json_handler import JSONHandler
from measure_plensor_mixin import MeasurePlensorMixin
from reset_plensor_mixin import ResetPlensorMixin
from set_damping_mixin import SetDampingMixin


class Sensor(
    GetSensorIDMixin, CalibrateSensorMixin, MeasurePlensorMixin, SetDampingMixin, ResetPlensorMixin):
    """
    Sensor class to handle individual sensor operations.

    Attributes:
        sensor_id (int): The ID of the sensor.
        ser (serial.Serial): Serial connection for communication.
        logger (ErrorLogger): Instance of ErrorLogger for logging errors.
    """

    def __init__(self, sensor_id: int, logger: ErrorLogger) -> None:
        self.sensor_id = sensor_id
        # TODO: Serial initialization should be in appv2
        self.ser = serial.Serial(
            port='/dev/ttyAMA0',
            baudrate=921600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=2
        )
        self.logger = logger
        self.sensor_id_bytes = [(self.sensor_id >> 16) & 0xFF,
                                (self.sensor_id >> 8)
                                & 0xFF, self.sensor_id & 0xFF]
        # Load the Plensor measurement settings when the object class
        # is initialized
        # TODO: keep track of the last modified time of the metadata JSON
        # to signal the Sensor object classes to read the plensor measurement
        # settings again.
        self.plensor_measurement_settings = (
            self.get_plensor_measurement_settings()
        )
        self.sensor_version = self._get_sensor_version(self.plensor_measurement_settings)
        self.json_handler = JSONHandler.get_instance()
        self.damping_level_base = self.get_damping_level()
        self.damping_level_bytes_base = self.extract_damping()
        print(f"Damping level from metadata: {self.damping_level_bytes_base}")

    def get_plensor_measurement_settings(self) -> dict:
        """
        Function to get Plensor-specific measurement settings
        from the metadata file.
        """
        try:
            metadata_directory = '/home/plense/metadata'
            metadata_file = next((file for file in os.listdir(metadata_directory) if file.startswith("metadata_")), None)
            metadata_path = os.path.join(metadata_directory, metadata_file)

            if not metadata_file:
                raise FileNotFoundError("Metadata file not found.")

            with open(metadata_path, 'r') as f:
                config = json.load(f)
                measurement_settings = config.get("measurement_settings", {})
                measurement_sequence = config.get("measurement_sequence", [])
                default_measurement_sequence = config.get("default_measurement_sequence", [])
                sensor_specific_settings = config.get("sensor_specific_settings", {})

            # Get sensor-specific settings or use default settings
            sensor_settings = sensor_specific_settings.get(str(self.sensor_id), {})
            combined_settings = {**measurement_settings, **sensor_settings}

            # If no specific measurement sequence is provided, use the default sequence for the sensor
            if not measurement_sequence:
                combined_settings["measurement_sequence"] = default_measurement_sequence

            return combined_settings

        except Exception as e:
            self.logger.log_error(f"Error while getting Plensor measurement settings: {e}")
            return {}

    def create_message(self, message_type: str, calibrate_after: bool = False, measure_after: bool = False) -> dict:
        """
        Creates a message for the given message type (e.g., 'get_byte', 'calibrate', 'measure').

        Parameters:
            message_type (str): The type of message to create ('get_byte', 'calibrate', 'measure').
            calibrate_after (bool): Whether calibration should be performed after getting bytes.

        Returns:
            dict: A dictionary representing the message.
        """
        if message_type == "get_byte":
            return {
                "sensor_id": self.sensor_id,
                "measurement_settings": {
                    "type": "get_byte",
                    "calibrate_after": calibrate_after
                }
            }
        elif message_type == "calibrate":
            return {
                "sensor_id": self.sensor_id,
                "measurement_settings": {
                    "type": "calibrate",
                    "measure_after": measure_after
                }
            }
        else:
            raise ValueError(f"Unknown message type: {message_type}")

    def _get_metadata_file_path(self) -> str:
        """
        Finds the metadata file path for the sensor.

        Returns:
            str: The path to the metadata file, or None if not found.
        """
        metadata_directory = '/home/plense/metadata'
        metadata_file = next((file for file in os.listdir(metadata_directory) if file.startswith("metadata_")), None)
        if not metadata_file:
            self.logger.log_error("Metadata file not found.")
            return None
        return os.path.join(metadata_directory, metadata_file)

    def _get_sensor_version(self, metadata: dict) -> tuple:
        """
        Searches for the sensor version and damping level in the metadata.

        Parameters:
            metadata (dict): The metadata dictionary.

        Returns:
            tuple: A tuple containing the sensor version and damping level.
        """
        sensor_versions = metadata.get("sensor_versions", {})
        for version, version_data in sensor_versions.items():
            for sensor in version_data.get("sensors", []):
                if sensor.get("sensor_id") == self.sensor_id:
                    damping_level = sensor.get("damping_level", version_data.get("default_damping_level", 0))
                    return version
        self.logger.log_error(f"Sensor ID {self.sensor_id} not found in metadata.")
        return "V5.0"
    
    def get_damping_level(self) -> int:
        metadata_path = self._get_metadata_file_path()
        if not metadata_path:
            return self._default_damping_level()

        # Load the metadata
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        # Load the damping level from the metadata
        damping_level = self._get_damping_level(metadata)

        return damping_level

    def extract_damping(self) -> bytes:
        """
        Extracts the damping byte from the sensor's metadata file based on the sensor version.

        Returns:
            bytes: The damping byte(s) extracted from the sensor's metadata.
        """
        try:
            damping_level = self.get_damping_level()

            if damping_level is None:
                return self._default_damping_level()

            # Process damping level based on version
            return self._process_damping_level(self.sensor_version, damping_level)

        except Exception as e:
            self.logger.log_error(f"Error while extracting damping level for sensor {self.sensor_id}: {e}")
            return self._default_damping_level()

    def _default_damping_level(self) -> bytes:
        """
        Returns the default damping level bytes based on the sensor ID.

        Returns:
            bytes: Default damping level bytes.
        """
        damping_level = 0
        return damping_level.to_bytes(1 if self.sensor_id <= 68 else 2, byteorder='big')

    def _get_sensor_version_and_damping(self, metadata: dict) -> tuple:
        """
        Searches for the sensor version and damping level in the metadata.

        Parameters:
            metadata (dict): The metadata dictionary.

        Returns:
            tuple: A tuple containing the sensor version and damping level.
        """
        sensor_versions = metadata.get("sensor_versions", {})
        for version, version_data in sensor_versions.items():
            for sensor in version_data.get("sensors", []):
                if sensor.get("sensor_id") == self.sensor_id:
                    damping_level = sensor.get("damping_level", version_data.get("default_damping_level", 0))
                    return version, damping_level
        self.logger.log_error(f"Sensor ID {self.sensor_id} not found in metadata.")
        return "V5.0", 0
    
    def _get_damping_level(self, metadata: dict) -> tuple:
        """
        Searches for the sensor version and damping level in the metadata.

        Parameters:
            metadata (dict): The metadata dictionary.

        Returns:
            tuple: A tuple containing the sensor version and damping level.
        """
        sensor_versions = metadata.get("sensor_versions", {})
        for version, version_data in sensor_versions.items():
            for sensor in version_data.get("sensors", []):
                if sensor.get("sensor_id") == self.sensor_id:
                    damping_level = sensor.get("damping_level", version_data.get("default_damping_level", 0))
                    return damping_level
        self.logger.log_error(f"Sensor ID {self.sensor_id} not found in metadata.")
        return 0