import json
import os
import time
from datetime import datetime
from ComponentHandler import ComponentHandler
from ErrorLogger import ErrorLogger
from JSONHandler import JSONHandler
from xedge_plense_tools import PreprocessingOperator_edge


class SignalProcessor:
    """
    SignalProcessor has functionality to process the signals locally.
    """

    def __init__(self):
        """
        Initializes the DataManager class.
        """
        # Initialize classes
        self.logger = ErrorLogger.get_instance(
            directory='/home/plense/error_logs',
            log_level=40,
            log_file_name='ProcessDataLocal.log'
        )
        self.edge_preprocessor = PreprocessingOperator_edge(
            '/home/plense/plensor_data/audio_data/time_domain_not_processed',
            '/home/plense/plensor_data/audio_data/time_domain_processed'
        )
        self.logger.log_info("New instance started -------")
        self.logger.set_log_level('ERROR')
        self.component_handler = ComponentHandler()
        self.json_handler = JSONHandler.get_instance()
        self.metadata_dir = '/home/plense/metadata'
        self.running = True

    def list_files(self, directory):
        """
        List all files and directories in a given directory using os.scandir.

        Parameters:
        - directory (str): The path to the directory to list files from.

        Returns:
        - list: A list of filenames found in the directory.
        """
        try:
            with os.scandir(directory) as entries:
                files = [entry.name for entry in entries if entry.is_file()]
                return files
        except FileNotFoundError:
            self.logger.log_error("The directory does not exist.")
            return None
        except PermissionError:
            self.logger.log_error("Permission denied.")
            return None
        except Exception as e:
            self.logger.log_error(f"An error occurred: {e}")
            return None

    def save_file_locally(self, filepath, local_path):
        """
        Save a file to local storage

        :param filepath: File to save
        :param local_path: Local path to save to
        :return: True if file was saved, else False
        """
        try:
            import shutil
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            shutil.copy2(filepath, local_path)
            self.logger.log_info(f"File saved locally: {local_path}")
            return True
        except FileNotFoundError:
            self.logger.log_error("The file was not found")
            return False
        except Exception as e:
            self.logger.log_critical(f"Error saving file locally: {e}")
            return False

    def get_input_signal_from_key(self, key):
        """
        Extract the input signal from the key.

        Parameters:
            key: the key

        Returns:
            input signal (str): Either BLOCK or SINE.
        """
        try:
            input_signal = key.split('#')[0]
            return input_signal
        except Exception as e:
            self.logger.log_error(f"Error extracting input signal from key: {e}")
            return None

    def create_local_metadata_file(self, sensor_id, record_timestamp, file_metadata, measurement_metadata):
        """
        Create a local metadata file instead of DynamoDB entry.

        Parameters:
            sensor_id: Sensor identifier
            record_timestamp: Timestamp of the record
            file_metadata: Metadata about the file
            measurement_metadata: Metadata about the measurement
        """
        try:
            metadata = {
                'sensor_id': sensor_id,
                'record_timestamp': record_timestamp,
                'file_metadata': file_metadata,
                'measurement_metadata': measurement_metadata,
                'created_at': datetime.now().isoformat()
            }
            
            # Save to local JSON file
            output_dir = '/home/plense/plensor_data/metadata'
            os.makedirs(output_dir, exist_ok=True)
            filename = f"{sensor_id}_{record_timestamp}.json"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            self.logger.log_info(f"Local metadata saved: {filepath}")
            return True
        except Exception as e:
            self.logger.log_error(f"Error creating local metadata: {e}")
            return False

    def create_local_env_file(self, sensor_id, record_timestamp, env_data):
        """
        Create a local environment data file.

        Parameters:
            sensor_id: Sensor identifier
            record_timestamp: Timestamp of the record
            env_data: Environmental data
        """
        try:
            metadata = {
                'sensor_id': sensor_id,
                'record_timestamp': record_timestamp,
                'environmental_data': env_data,
                'created_at': datetime.now().isoformat()
            }
            
            # Save to local JSON file
            output_dir = '/home/plense/plensor_data/environmental'
            os.makedirs(output_dir, exist_ok=True)
            filename = f"{sensor_id}_env_{record_timestamp}.json"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            self.logger.log_info(f"Local environmental data saved: {filepath}")
            return True
        except Exception as e:
            self.logger.log_error(f"Error creating local environmental data: {e}")
            return False

    def create_local_tof_file(self, metadata, record_timestamp, tof_data, prefix):
        """
        Create a local TOF data file.

        Parameters:
            metadata: Metadata about the measurement
            record_timestamp: Timestamp of the record
            tof_data: TOF data
            prefix: File prefix
        """
        try:
            data = {
                'metadata': metadata,
                'record_timestamp': record_timestamp,
                'tof_data': tof_data,
                'prefix': prefix,
                'created_at': datetime.now().isoformat()
            }
            
            # Save to local JSON file
            output_dir = '/home/plense/plensor_data/tof'
            os.makedirs(output_dir, exist_ok=True)
            filename = f"{prefix}_{record_timestamp}.json"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.logger.log_info(f"Local TOF data saved: {filepath}")
            return True
        except Exception as e:
            self.logger.log_error(f"Error creating local TOF data: {e}")
            return False

    def convert_to_epoch_millis(self, timestamp_str):
        """
        Convert timestamp string to epoch milliseconds.

        Parameters:
            timestamp_str: Timestamp string

        Returns:
            int: Epoch milliseconds
        """
        try:
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            return int(dt.timestamp() * 1000)
        except Exception as e:
            self.logger.log_error(f"Error converting timestamp: {e}")
            return None

    def add_local_health_log(self, sensor_id, data_type, input_signal, health_metric_name, health_metric_value, record_timestamp):
        """
        Add health metrics to local log file.

        Parameters:
            sensor_id: Sensor identifier
            data_type: Type of data
            input_signal: Input signal type
            health_metric_name: Name of the health metric
            health_metric_value: Value of the health metric
            record_timestamp: Timestamp of the record
        """
        try:
            health_data = {
                'sensor_id': sensor_id,
                'data_type': data_type,
                'input_signal': input_signal,
                'health_metric_name': health_metric_name,
                'health_metric_value': health_metric_value,
                'record_timestamp': record_timestamp,
                'created_at': datetime.now().isoformat()
            }
            
            # Save to local health log
            output_dir = '/home/plense/plensor_data/health_logs'
            os.makedirs(output_dir, exist_ok=True)
            filename = f"health_{sensor_id}_{record_timestamp}.json"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(health_data, f, indent=2)
            
            self.logger.log_info(f"Health log saved: {filepath}")
            return True
        except Exception as e:
            self.logger.log_error(f"Error creating health log: {e}")
            return False

    def add_local_environment_log(self, sensor_id, inside_temperature, outside_temperature, inside_humidity, outside_humidity, record_timestamp):
        """
        Add environment data to local log file.

        Parameters:
            sensor_id: Sensor identifier
            inside_temperature: Inside temperature
            outside_temperature: Outside temperature
            inside_humidity: Inside humidity
            outside_humidity: Outside humidity
            record_timestamp: Timestamp of the record
        """
        try:
            env_data = {
                'sensor_id': sensor_id,
                'inside_temperature': inside_temperature,
                'outside_temperature': outside_temperature,
                'inside_humidity': inside_humidity,
                'outside_humidity': outside_humidity,
                'record_timestamp': record_timestamp,
                'created_at': datetime.now().isoformat()
            }
            
            # Save to local environment log
            output_dir = '/home/plense/plensor_data/environment_logs'
            os.makedirs(output_dir, exist_ok=True)
            filename = f"environment_{sensor_id}_{record_timestamp}.json"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(env_data, f, indent=2)
            
            self.logger.log_info(f"Environment log saved: {filepath}")
            return True
        except Exception as e:
            self.logger.log_error(f"Error creating environment log: {e}")
            return False

    def process_time_domain(self, execute_preprocessing = True, segment_length=25000, process_num_segments=10):
        """
        Process time domain data locally.
        """
        try:
            self.logger.log_info("Starting time domain processing...")
            
            # Your existing time domain processing logic here
            # This would be the core signal processing without AWS dependencies
            
            self.logger.log_info("Time domain processing completed")
            return True
        except Exception as e:
            self.logger.log_error(f"Error in time domain processing: {e}")
            return False

    def process_tof(self):
        """
        Process TOF measurements locally.
        """
        try:
            self.logger.log_info("Starting TOF processing...")
            
            # Your existing TOF processing logic here
            # This would be the core TOF processing without AWS dependencies
            
            self.logger.log_info("TOF processing completed")
            return True
        except Exception as e:
            self.logger.log_error(f"Error in TOF processing: {e}")
            return False

    def process_environment(self):
        """
        Process environmental measurements locally.
        """
        try:
            self.logger.log_info("Starting environment processing...")
            
            # Your existing environment processing logic here
            # This would be the core environment processing without AWS dependencies
            
            self.logger.log_info("Environment processing completed")
            return True
        except Exception as e:
            self.logger.log_error(f"Error in environment processing: {e}")
            return False

    def get_preprocessing_config(self):
        """
        Get preprocessing configuration.
        """
        try:
            config_path = os.path.join(self.metadata_dir, 'measure_settings.json')
            with open(config_path, 'r') as f:
                config = json.load(f)
            return config
        except Exception as e:
            self.logger.log_error(f"Error loading preprocessing config: {e}")
            return None

    def run(self):
        """
        Main run loop for local processing.
        """
        try:
            self.logger.log_info("Starting local signal processor...")
            
            while self.running:
                # Process time domain data
                self.process_time_domain()
                
                # Process TOF data
                self.process_tof()
                
                # Process environment data
                self.process_environment()
                
                # Sleep for a bit before next iteration
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            self.logger.log_info("Signal processor stopped by user")
        except Exception as e:
            self.logger.log_error(f"Error in main run loop: {e}")


if __name__ == "__main__":
    processor = SignalProcessor()
    processor.run()
