import logging
import os
from datetime import datetime
from ErrorLogger import ErrorLogger
from JSONHandler import JSONHandler


class ComponentHandler:
    """
    Custom functionality that is used in multiple Plense local
    components to handle different sensor types.
    """
    _instance = None

    @classmethod
    def get_instance(cls, directory=None, log_level=logging.ERROR):
        if cls._instance is None:
            cls._instance = cls(directory, log_level=log_level)
        return cls._instance

    def __init__(
            self,
            directory=None,
            log_level=logging.ERROR,
            log_file_name='error.log'):
        """
        Initializes the ErrorLogger, setting up the logging configuration
        including the log file name, format, and log level.

        Parameters:
            - directory (str): The directory where the log file will be stored.
            - log_file_name (str): The name of the file where log messages will
              be stored.
            - log_level (int): The logging level (e.g., logging.ERROR,
              logging.DEBUG).
        """
        if self._instance is not None:
            raise Exception("ErrorLogger is a singleton!")
        self.logger = ErrorLogger.get_instance()
        self.json_handler = JSONHandler.get_instance()

    def as_local_component(self):
        """
        Checks whether the script runs as a local component.
        """
        try:
            AS_LOCAL = os.environ.get('AS_LOCAL', True)
            if AS_LOCAL:
                self.logger.log_info("Running as local component.")
            else:
                self.logger.log_info("Not running as local component.")

        except Exception as e:
            self.logger.log_error(
                f"Exception checking if the script runs as a component: {e}"
            )

        return AS_LOCAL

    def read_hostname_from_file(self):
        """
        Reads and returns the pi_id hostname.
        """
        try:
            base_dir = os.getcwd()
            hostname_file_path = os.path.join(
                base_dir,
                'etc',
                'container_hostname'
            )
        except Exception as e:
            self.logger.log_error(f"Error reading hostname from file: {e}")

        try:
            with open(hostname_file_path, 'r') as file:
                # Read the first line and strip any newline characters
                hostname = file.readline().strip()
                self.logger.log_error(f"Hostname: {hostname}")
            return hostname
        except Exception as e:
            self.logger.log_error(f"Error reading hostname: {e}")
            return None

    def get_metadata_from_cache(
            self,
            sensor_type="TEST_SENSOR_TYPE",
            sensor_id="#TEST_PI_ID"):
        """
        Read in the metadata of the specified sensor_type sensor_id.
        """
        try:
            # base_dir = os.getcwd()
            base_dir = '/home/plense'
            metadata_dir = os.path.join(base_dir, 'metadata')
            metadata_file_path = os.path.join(
                metadata_dir,
                f"{sensor_type}{sensor_id}_metadata.json"
            )

            if os.path.exists(metadata_file_path):
                metadata = self.json_handler.safe_json_load(
                    metadata_file_path
                )
                self.logger.log_info(
                    f"Metadata loaded from cache: {metadata_file_path}"
                )
                return metadata
            else:
                self.logger.log_error(
                    f"Metadata file not found: {metadata_file_path}"
                )
                return None

        except Exception as e:
            self.logger.log_error(f"Error reading metadata from cache: {e}")
            return None

    def get_metadata_by_type(self, sensor_type="TEST_SENSOR"):
        """
        Read in the metadata of the specified sensor_type.
        """
        try:
            base_dir = '/home/plense'
            metadata_dir = os.path.join(base_dir, 'metadata')
            metadata_files = os.listdir(metadata_dir)
            metadata_list = []

            for file in metadata_files:
                if file.startswith(sensor_type) and file.endswith('_metadata.json'):
                    metadata_file_path = os.path.join(metadata_dir, file)
                    metadata = self.json_handler.safe_json_load(
                        metadata_file_path
                    )
                    metadata_list.append(metadata)

            return metadata_list

        except Exception as e:
            self.logger.log_error(f"Error reading metadata by type: {e}")
            return []

    def save_logs_locally(
            self, sensor_type, pi_id, date, logfile='error.log'):
        """
        Save logs to local storage instead of S3.
        """
        try:
            import shutil
            source_log_path = f'/home/plense/error_logs/{logfile}'
            target_dir = f'/home/plense/plensor_data/logs/{sensor_type}/{pi_id}/{date}'
            target_log_path = os.path.join(target_dir, logfile)
            
            os.makedirs(target_dir, exist_ok=True)
            shutil.copy2(source_log_path, target_log_path)
            
            self.logger.log_info(f"Logs saved locally: {target_log_path}")
            return True
        except Exception as e:
            self.logger.log_error(f"Error saving logs locally: {e}")
            return False

    def create_local_metadata_file(
            self, metadata, record_timestamp):
        """
        Create a local metadata file instead of DynamoDB item.
        """
        try:
            data = {
                'metadata': metadata,
                'record_timestamp': record_timestamp,
                'created_at': datetime.now().isoformat()
            }
            
            # Save to local JSON file
            output_dir = '/home/plense/plensor_data/metadata'
            os.makedirs(output_dir, exist_ok=True)
            filename = f"metadata_{record_timestamp}.json"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w') as f:
                import json
                json.dump(data, f, indent=2)
            
            self.logger.log_info(f"Local metadata saved: {filepath}")
            return True
        except Exception as e:
            self.logger.log_error(f"Error creating local metadata: {e}")
            return False

    def create_local_file_path(self, metadata, record_date, record_time, input_signal='BLOCK'):
        """
        Create a local file path for storing data.
        """
        try:
            sensor_id = metadata.get('sensor_id', 'unknown')
            sensor_type = metadata.get('sensor_type', 'unknown')
            
            # Create a standardized local path
            local_path = f"/home/plense/plensor_data/{sensor_type}/{sensor_id}/{record_date}/{record_time}_{input_signal}"
            
            self.logger.log_info(f"Local file path created: {local_path}")
            return local_path
        except Exception as e:
            self.logger.log_error(f"Error creating local file path: {e}")
            return None

    def safe_create_local_path(self, metadata, record_date, record_time, input_signal='BLOCK'):
        """
        Safely create a local file path with error handling.
        """
        try:
            return self.create_local_file_path(metadata, record_date, record_time, input_signal)
        except Exception as e:
            self.logger.log_error(f"Error in safe_create_local_path: {e}")
            return None

    def determine_metadata_format(self, metadata):
        """
        Determine the format of metadata for local storage.
        """
        try:
            if isinstance(metadata, dict):
                return "json"
            elif isinstance(metadata, str):
                return "string"
            else:
                return "unknown"
        except Exception as e:
            self.logger.log_error(f"Error determining metadata format: {e}")
            return "unknown"

    def save_ultrasound_locally(
            self, measurement, metadata):
        """
        Save ultrasound data to local storage instead of S3.
        """
        try:
            import shutil
            
            # Create local directory structure
            sensor_id = metadata.get('sensor_id', 'unknown')
            sensor_type = metadata.get('sensor_type', 'unknown')
            local_dir = f"/home/plense/plensor_data/ultrasound/{sensor_type}/{sensor_id}"
            os.makedirs(local_dir, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ultrasound_{sensor_id}_{timestamp}.json"
            filepath = os.path.join(local_dir, filename)
            
            # Save measurement data
            with open(filepath, 'w') as f:
                import json
                json.dump({
                    'measurement': measurement,
                    'metadata': metadata,
                    'timestamp': timestamp
                }, f, indent=2)
            
            self.logger.log_info(f"Ultrasound data saved locally: {filepath}")
            return True
        except Exception as e:
            self.logger.log_error(f"Error saving ultrasound data locally: {e}")
            return False